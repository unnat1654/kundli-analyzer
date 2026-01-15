import time, os
from typing import Literal, Optional
from google import genai
from pydantic import BaseModel
import pymongo
from utils import AGENT_NAME, MAX_DURATION
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

reports = None
try:
    mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'), serverSelectionTimeoutMS=2000)
    reports = mongo_client.get_database().kundli_reports
    
    reports.create_index("interaction_id", unique=True)
except Exception as e:
    print(f"[Warning] MongoDB connection failed: {e}")


def execute_deep_research(prompt:str)->dict[str,str]:
    """
    Executes a Deep Research task with auto-reconnection and timeout handling.
    
    Returns:
        dict: { "status": str, "output": str }
        Possible statuses: "completed", "timeout", "fatal_error", "connection_failed", "empty"
    """

    if reports is not None:
        try:
            cached = reports.find_one({
                "prompt": prompt,
            })
            if cached and cached.get("report"):
                return {"status": "completed", "output": cached["report"]}
            if cached:
                interaction=client.interactions.get(id=cached["interaction_id"])
                if interaction.status=='completed' and interaction.outputs:
                    return {"status": "completed", "output": interaction.outputs[-1].text}
                if interaction.status=='in_progress':
                    return {"status": "connection_failed", "output": ""}
        except Exception:
            pass
    
    collected_output = []
  
    state = {
        "last_event_id": None,
        "interaction_id": None,
        "is_complete": False,
        "exit_status": "unknown" 
    }
    
    start_time = time.time()

    def process_stream(event_stream):
        for event in event_stream:
            if event.event_type == "interaction.start":
                state["interaction_id"] = event.interaction.id
                print(f"\n[Server] Research started with ID: {state['interaction_id']}")
                if reports is not None:
                    try:
                        reports.insert_one({
                            "prompt": prompt,
                            "interaction_id": state["interaction_id"],
                            "created_at": time.time()
                        })
                    except Exception:
                        pass
            
            if event.event_id:
                state["last_event_id"] = event.event_id

            if event.event_type == "content.delta":
                delta = event.delta
                if hasattr(delta, 'text') and delta.text:
                    collected_output.append(delta.text)

            if event.event_type == "error":
                err_code = getattr(event.error, 'code', '')
                err_msg = getattr(event.error, 'message', '')
    
                if 'gateway_timeout' in str(err_code) or 'deadline' in str(err_msg).lower():
                    return 
                else:
                    print(f"\n[Fatal Error] {err_code}: {err_msg}")
                    state["exit_status"] = "fatal_error"
                    state["is_complete"] = True
                    
                    if state["interaction_id"]:
                        try:
                            client.interactions.delete(id=state["interaction_id"])
                        except:
                            pass
                    return

            if event.event_type == "interaction.complete":
                state["is_complete"] = True
                state["exit_status"] = "completed"

    try:
        initial_stream = client.interactions.create(
            input=prompt,
            agent=AGENT_NAME,
            background=True,
            stream=True,
            agent_config={"type": "deep-research", "thinking_summaries": "none"}
        )
        process_stream(initial_stream)

    except Exception as e:
        return {"status": "connection_failed", "output": ""}

    while not state["is_complete"] and state["interaction_id"]:
        if time.time() - start_time > MAX_DURATION:
            try:
                client.interactions.delete(id=state["interaction_id"])
            except Exception:
                pass
            
            return {"status": "timeout", "output": ""}
        time.sleep(5)
        try:
            resume_stream = client.interactions.get(
                id=state["interaction_id"],
                stream=True,
                last_event_id=state["last_event_id"]
            )
            process_stream(resume_stream)
        except Exception:
            pass

    final_output = "".join(collected_output)

    if state["exit_status"] == "completed" and not final_output:
        return {"status": "empty", "output": ""}

    if state["exit_status"] == "fatal_error":
         return {"status": "fatal_error", "output": ""}
    
    if reports is not None:
        try:
            reports.update_one(
                {"prompt": prompt},
                {
                    "$set": {
                        "report": final_output,
                        "interaction_id": state.get("interaction_id"),
                        "updated_at": time.time()
                    }
                },
                upsert=True
            )
        except Exception:
            pass

    return {"status": "completed", "output": final_output}


def start_deep_research(prompt:str, birth_img:str, gochar_img:str, dasha_str:str)->str|None:
    try:
        if reports is None:
            return None
        cached = reports.find_one({
            "prompt": prompt,
        })
        if cached and cached.get("report"):
            return cached['interaction_id']
        if cached:
            interaction=client.interactions.get(id=cached["interaction_id"])
            if interaction.status=='completed' or interaction.status=='in_progress':
                return interaction.id
        
        interaction = client.interactions.create(
            input=prompt,
            agent=AGENT_NAME,
            background=True,
            agent_config={"type": "deep-research", "thinking_summaries": "none"}
        )
        if reports is not None:
            reports.insert_one({
                "prompt": prompt,
                "birth_img":birth_img,
                "gochar_img":gochar_img,
                "dasha_str":dasha_str,
                "interaction_id": interaction.id,
                "created_at": time.time()
            })
        return interaction.id
    except Exception as e:
        print(e)
        return None

class ResearchResult(BaseModel):
    status: Literal["completed", "in_progress", "failed", "error", "error"]
    birth_img:Optional[str]=None
    gochar_img:Optional[str]=None
    dasha_str:Optional[str]=None
    output: Optional[str]=None

def get_research_result(interaction_id:str)->ResearchResult:
    try:
        if reports is None:
            return ResearchResult(
                status="error",
            )

        cached = reports.find_one({
            "interaction_id": interaction_id,
        })
        if cached is None:
            return ResearchResult(
                status="error",
            )
         
        if cached and cached.get("report"):
            return ResearchResult(
                status="completed", 
                birth_img=cached['birth_img'],
                gochar_img=cached['gochar_img'], 
                dasha_str=cached['dasha_str'], 
                output=cached['report']
            )
        
        interaction=client.interactions.get(id=interaction_id)

        if interaction.status=='completed' and interaction.outputs:
            result=getattr(interaction.outputs[-1], 'text', None)
            if result:
                if reports is not None:
                    reports.update_one(
                        {"prompt": 'interaction_id'},
                        {
                            "$set": {
                                "report": result,
                                "updated_at": time.time()
                            }
                        },
                        upsert=True
                    )
                return ResearchResult(
                    status="completed", 
                    birth_img=cached['birth_img'],
                    gochar_img=cached['gochar_img'], 
                    dasha_str=cached['dasha_str'], 
                    output=result
                )
        elif interaction.status=='in_progress':
            return ResearchResult(status="in_progress")   
        
        return ResearchResult(status="failed")
        
    except Exception as e:
        print(e)
        return ResearchResult(status="error")
