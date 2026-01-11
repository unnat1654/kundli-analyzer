from flask import Flask, request, jsonify
from kundli import generate_kundli, generate_lagna_gochar
from utils import create_prompt, validate_input
from analysis import execute_deep_research


app = Flask(__name__)

@app.route('/generate-kundli', methods=['POST'])
def route_generate_kundli():
    data = request.get_json()

    clean_params, error = validate_input(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    try:
        kundli = generate_kundli(**clean_params)
        return jsonify({
            "status": "success",
            "kundli": kundli
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/generate-prompt', methods=['POST'])   
def route_generate_prompt():
    data = request.get_json()
    
    clean_params, error = validate_input(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    try:
        jyotish_schools = clean_params.pop('jyotish_schools', None)
        inc_remedy_categories = clean_params.pop('inc_remedy_categories', None)
        exc_remedy_categories = clean_params.pop('exc_remedy_categories', None)
        language = clean_params.pop('language', None)

        base_kundli = generate_kundli(**clean_params)
        
        lagna_gochar=generate_lagna_gochar(**clean_params)

        prompt=create_prompt(base_kundli,lagna_gochar, jyotish_schools, inc_remedy_categories,exc_remedy_categories, language)
        
        return prompt
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/generate-analysis', methods=['POST'])
def route_generate_analysis():
    data = request.get_json()
    
    clean_params, error = validate_input(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    try:
        jyotish_schools = clean_params.pop('jyotish_schools', None)
        inc_remedy_categories = clean_params.pop('inc_remedy_categories', None)
        exc_remedy_categories = clean_params.pop('exc_remedy_categories', None)
        language = clean_params.pop('language', None)

        base_kundli = generate_kundli(**clean_params)
        
        lagna_gochar=generate_lagna_gochar(**clean_params)

        prompt=create_prompt(base_kundli,lagna_gochar, jyotish_schools, inc_remedy_categories,exc_remedy_categories, language)
        
        result=execute_deep_research(prompt)

        req_status = result.get("status")
        output_text = result.get("output")

        if req_status == "completed":
            return jsonify({
                "status": "success",
                "analysis_result": output_text
            }), 200

        else:
            error_messages = {
                "timeout": "The research operation timed out (server took too long).",
                "fatal_error": "The research agent encountered a fatal error.",
                "connection_failed": "Could not connect to the AI service.",
                "empty": "The research finished but generated no text output."
            }

            msg = error_messages.get(req_status, f"Unknown research error: {req_status}")
            
            return jsonify({
                "status": "error", 
                "message": msg
            }), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)