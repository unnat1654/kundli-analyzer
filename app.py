import base64
import traceback
from flask import Flask, request, jsonify, send_from_directory
from download import generate_jyotish_report
from kundli import generate_kundli, generate_d1_img
from datetime import datetime
from dasha import generate_dasha
from gochar import generate_lagna_gochar, generate_gochar_img
from utils import create_prompt, validate_input, get_raw_positions, get_rashi
from analysis import get_research_result, start_deep_research, get_last_report
from flask_cors import CORS
import os

app = Flask(
    __name__,
    static_folder="dist",
    template_folder="dist"
)
CORS(app)


@app.route('/api/start-analysis', methods=['POST'])  
def route_start_analysis():
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

        kundli_str, kundli_data = generate_kundli(positions,ascmc[0], asc_rashi)
        

        dob = datetime(
            clean_params['year'],
            clean_params['month'],
            clean_params['day'],
            clean_params['ist_hour'],
            clean_params['ist_minute']
        )
        moon_longitude = positions["Chandra"]["longitude"]
        _, current_dasha_data=generate_dasha(moon_longitude, dob)
        
        aprox_time=current_dasha_data['current_dasha']['pratyantardasha']['start']

        gochar_str, gochar_data = generate_lagna_gochar(clean_params["lat"], clean_params["lon"], asc_rashi, aprox_time)

        dasha_str,_=generate_dasha(moon_longitude, dob)

        gochar_img = generate_gochar_img(gochar_data, asc_rashi)
        gochar_img.seek(0)

        birth_img = generate_d1_img(kundli_data, asc_rashi)
        birth_img.seek(0)

        prompt=create_prompt(kundli_str, dasha_str, gochar_str, jyotish_schools, inc_remedy_categories,exc_remedy_categories, language)
        interaction_id=start_deep_research(
            prompt, 
            base64.b64encode(birth_img.read()).decode("utf-8"), 
            base64.b64encode(gochar_img.read()).decode("utf-8"), 
            dasha_str
            )

        if interaction_id is None:
            return jsonify({"status":"error"}), 500
        else:
            return jsonify({"status":"success"}), 200
        
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return jsonify({"status":"error"}), 500


@app.route('/api/get-analysis', methods=['GET'])
@app.route('/api/get-analysis/<interaction_id>', methods=['GET'])
def route_get_analysis(interaction_id: str | None = None):
    if interaction_id is None:
        result=get_last_report()
    else:
        result = get_research_result(interaction_id)

    return jsonify(result.model_dump()), 200
    
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

        kundli_str, _ = generate_kundli(positions,ascmc[0], asc_rashi)
        
        dob = datetime(
            clean_params['year'],
            clean_params['month'],
            clean_params['day'],
            clean_params['ist_hour'],
            clean_params['ist_minute']
        )
        moon_longitude = positions["Chandra"]["longitude"]
        _, current_dasha_data=generate_dasha(moon_longitude, dob)
        
        aprox_time=current_dasha_data['current_dasha']['pratyantardasha']['start']

        lagna_gochar_str, _ = generate_lagna_gochar(clean_params["lat"], clean_params["lon"], asc_rashi, aprox_time)

        dasha_str,_=generate_dasha(moon_longitude, dob)

        prompt=create_prompt(kundli_str, dasha_str, lagna_gochar_str, jyotish_schools, inc_remedy_categories,exc_remedy_categories, language)
        
        return jsonify({"status":"success","dasha": dasha_str, "analysis_result": prompt}),200
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500


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