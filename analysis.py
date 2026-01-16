import time, os
import traceback
from typing import Literal, Optional
from google import genai
from pydantic import BaseModel
import pymongo
from utils import AGENT_NAME
from dotenv import load_dotenv
import os, sys

if getattr(sys, 'frozen', False):
    load_dotenv(os.path.join(sys._MEIPASS, '.env'))
else:
    load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

reports = None
try:
    mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'), serverSelectionTimeoutMS=2000)
    reports = mongo_client.get_database().kundli_reports
    
    reports.create_index("interaction_id", unique=True)
except Exception as e:
    print(f"[Warning] MongoDB connection failed: {e}")


def start_deep_research(prompt:str, birth_img:str, gochar_img:str, dasha_str:str)->str|None:
    interaction_id=""
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
        interaction_id=interaction.id
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
        client.interactions.delete(id=interaction_id)
        print(e)
        return None

class ResearchResult(BaseModel):
    status: Literal["completed", "in_progress", "failed", "error", "not_found"]
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
                status="not_found",
            )
         
        if cached and cached.get("report"):
            return ResearchResult(
                status="completed", 
                birth_img=cached.get('birth_img'),
                gochar_img=cached.get('gochar_img'), 
                dasha_str=cached.get('dasha_str'), 
                output=cached['report']
            )
        
        interaction=client.interactions.get(id=interaction_id)

        if interaction.status=='completed' and interaction.outputs:
            result=getattr(interaction.outputs[-1], 'text', None)
            if result:
                if reports is not None:
                    reports.update_one(
                        {"interaction_id": interaction_id},
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
                    birth_img=cached.get('birth_img'),
                    gochar_img=cached.get('gochar_img'), 
                    dasha_str=cached.get('dasha_str'), 
                    output=result
                )
        elif interaction.status=='in_progress':
            return ResearchResult(status="in_progress")   
        
        return ResearchResult(status="failed")
        
    except Exception as e:
        print(e)
        return ResearchResult(status="error")

def get_last_report()->ResearchResult:
    try:
        latest_report = reports.find_one(
            {},
            sort=[("created_at", -1)]
        )
        if latest_report is None:
            return ResearchResult(
                status="not_found",
            )

        if latest_report and latest_report.get("report"):
            return ResearchResult(
                status="completed", 
                birth_img=latest_report.get('birth_img'),
                gochar_img=latest_report.get('gochar_img'), 
                dasha_str=latest_report.get('dasha_str'), 
                output=latest_report['report']
            )

        interaction=client.interactions.get(id=latest_report['interaction_id'])

        if interaction.status=='completed' and interaction.outputs:
                result=getattr(interaction.outputs[-1], 'text', None)
                if result:
                    if reports is not None:
                        reports.update_one(
                            {"interaction_id": latest_report['interaction_id']},
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
                        birth_img=latest_report.get('birth_img'),
                        gochar_img=latest_report.get('gochar_img'), 
                        dasha_str=latest_report.get('dasha_str'), 
                        output=result
                    )
        elif interaction.status=='in_progress':
            return ResearchResult(status="in_progress")   

        return ResearchResult(status="failed")
    except Exception as e:
        traceback.print_exc()
        print(e)
        return ResearchResult(status="error")

        