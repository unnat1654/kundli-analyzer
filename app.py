import traceback, sys
from flask import Flask, request, jsonify, send_file, send_from_directory
from download import generate_jyotish_report
from kundli import generate_kundli, generate_d1_img
from datetime import datetime
from dasha import generate_dasha
from gochar import generate_lagna_gochar, generate_gochar_img
from utils import create_prompt, validate_input, get_raw_positions, get_rashi
from analysis import execute_deep_research
from flask_cors import CORS
import os

app = Flask(
    __name__,
    static_folder="dist",
    template_folder="dist"
)

CORS(app)

@app.route('/api/generate-kundli', methods=['POST'])
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
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate-gochar', methods=['POST'])
def route_generate_gochar():
    data = request.get_json()

    clean_params, error = validate_input(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    try:
        _, _, ascmc=get_raw_positions(**clean_params)
        asc_rashi = get_rashi(ascmc[0])

        _, gochar_data = generate_lagna_gochar(clean_params["lat"],clean_params["lon"], asc_rashi, datetime.now())
        img_buf = generate_gochar_img(gochar_data, asc_rashi)

        return send_file(img_buf, mimetype='image/png')
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/generate-prompt', methods=['POST'])   
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
        
        dob = datetime(
            clean_params['year'],
            clean_params['month'],
            clean_params['day'],
            clean_params['ist_hour'],
            clean_params['ist_minute']
        )
        moon_longitude = positions["Chandra"]["longitude"]
        _, current_dasha_data=generate_dasha(moon_longitude, dob)
        
        aprox_time=current_dasha_data['current_dasha']['start']

        lagna_gochar_str, _ = generate_lagna_gochar(clean_params["lat"], clean_params["lon"], asc_rashi, aprox_time)

        dasha_str,_=generate_dasha(moon_longitude, dob)

        prompt=create_prompt(kundli_str, dasha_str, lagna_gochar_str, jyotish_schools, inc_remedy_categories,exc_remedy_categories, language)
        
        return jsonify({"status":"success","dasha": dasha_str, "analysis_result": prompt}),200
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/generate-analysis', methods=['POST'])
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
        

        dob = datetime(
            clean_params['year'],
            clean_params['month'],
            clean_params['day'],
            clean_params['ist_hour'],
            clean_params['ist_minute']
        )
        moon_longitude = positions["Chandra"]["longitude"]
        _, current_dasha_data=generate_dasha(moon_longitude, dob)
        
        aprox_time=current_dasha_data['current_dasha']['start']

        lagna_gochar_str, _ = generate_lagna_gochar(clean_params["lat"], clean_params["lon"], asc_rashi, aprox_time)

        dasha_str,_=generate_dasha(moon_longitude, dob)

        prompt=create_prompt(kundli_str, dasha_str, lagna_gochar_str, jyotish_schools, inc_remedy_categories,exc_remedy_categories, language)
        
        result=execute_deep_research(prompt)

        req_status = result["status"]
        output_text = result["output"]

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
        error_trace = traceback.format_exc()

        # 2. Write DIRECTLY to stderr (Standard Error)
        # This bypasses Flask's logger and Python's print buffer
        sys.stderr.write("################ ERROR ################\n")
        sys.stderr.write(error_trace)
        sys.stderr.write("#######################################\n")
        sys.stderr.flush() # Force it to appear immediately
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/download-pdf', methods=['POST'])
def route_download_pdf():
    try:

        data = request.get_json()
        required_fields=["kundli_img", "gochar_img", "dasha_str", "report_str"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error", 
                    "message":f"Missing required field: {field}"
                }), 400
        
        destination = generate_jyotish_report(
            data['kundli_img'], 
            data['gochar_img'], 
            data['dasha_str'], 
            data['report_str']
        )

        if destination is None:
            return jsonify({'status':'error'}),500

        return jsonify({'status':'success', 'destination':destination}),200
    except Exception as e:
        print(e)
        return jsonify({"status": "error"}), 500


@app.route("/assets/<path:path>")
def serve_assets(path):
    return send_from_directory(os.path.join(app.static_folder or "", "assets"), path)

@app.route("/<path:path>")
def serve_static(path):
    full_path = os.path.join(app.static_folder or "", path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder or "", path)
    return send_from_directory(app.static_folder or "", "index.html")

@app.route("/")
def index():
    return send_from_directory(app.static_folder or "", "index.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)