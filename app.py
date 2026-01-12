from flask import Flask, request, jsonify, send_file
from kundli import generate_kundli, generate_d1_img
from datetime import datetime
from dasha import generate_dasha
from gochar import generate_lagna_gochar, generate_gochar_img
from utils import create_prompt, validate_input, get_raw_positions, get_rashi
from analysis import execute_deep_research
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route('/generate-kundli', methods=['POST'])
def route_generate_kundli():
    data = request.get_json()

    clean_params, error = validate_input(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    try:
        positions, _, ascmc=get_raw_positions(**clean_params)
        asc_rashi = get_rashi(ascmc[0])

        _, kundli_data = generate_kundli(positions, asc_rashi)
        img_buf = generate_d1_img(kundli_data, asc_rashi)

        return send_file(img_buf, mimetype='image/png')
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate-gochar', methods=['POST'])
def route_generate_gochar():
    data = request.get_json()

    clean_params, error = validate_input(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    try:
        _, _, ascmc=get_raw_positions(**clean_params)
        asc_rashi = get_rashi(ascmc[0])

        _, gochar_data = generate_lagna_gochar(clean_params["lat"],clean_params["lon"], asc_rashi)
        img_buf = generate_gochar_img(gochar_data, asc_rashi)

        return send_file(img_buf, mimetype='image/png')
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

        positions, _, ascmc=get_raw_positions(**clean_params)
        asc_rashi = get_rashi(ascmc[0])

        kundli_str, _ = generate_kundli(positions, asc_rashi)
        
        lagna_gochar_str, _ = generate_lagna_gochar(clean_params["lat"], clean_params["lon"], asc_rashi)

        dob = datetime(
            clean_params['year'],
            clean_params['month'],
            clean_params['day'],
            clean_params['ist_hour'],
            clean_params['ist_minute']
        )
        moon_longitude = positions["Chandra"]["longitude"]
        dasha_str=generate_dasha(moon_longitude, dob)

        prompt=create_prompt(kundli_str, dasha_str, lagna_gochar_str, jyotish_schools, inc_remedy_categories,exc_remedy_categories, language)
        
        return jsonify({"status":"success","prompt":prompt}),200
    except Exception as e:
        print(e)
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

        positions, _, ascmc=get_raw_positions(**clean_params)
        asc_rashi = get_rashi(ascmc[0])

        kundli_str, _ = generate_kundli(positions, asc_rashi)
        
        lagna_gochar_str, _ = generate_lagna_gochar(clean_params["lat"], clean_params["lon"], asc_rashi)

        dob = datetime(
            clean_params['year'],
            clean_params['month'],
            clean_params['day'],
            clean_params['ist_hour'],
            clean_params['ist_minute']
        )
        moon_longitude = positions["Moon"]["longitude"]
        dasha_str=generate_dasha(moon_longitude, dob)

        prompt=create_prompt(kundli_str, dasha_str, lagna_gochar_str, jyotish_schools, inc_remedy_categories,exc_remedy_categories, language)
        
        result=execute_deep_research(prompt)

        req_status = result.get("status")
        output_text = result.get("output")

        if req_status == "completed":
            return jsonify({
                "status": "success",
                "dasha": dasha_str,
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