from flask import Flask, render_template, request, jsonify
import sys
import os

# Ensure local modules are importable
sys.path.append(os.getcwd())

from database import init_db, save_notam, get_all_notams
from decoder import parse_notam

app = Flask(__name__)

# Initialize DB on start
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/notams', methods=['GET', 'POST'])
def handle_notams():
    if request.method == 'POST':
        data = request.json
        raw_text = data.get('raw_text')
        
        if not raw_text:
            return jsonify({'error': 'No text provided'}), 400
            
        parsed = parse_notam(raw_text)
        
        # Save to DB
        saved = save_notam(parsed)
        
        return jsonify({
            'success': saved,
            'data': parsed
        })
    else:
        # GET all archived NOTAMs
        notams = get_all_notams()
        return jsonify(notams)

@app.route('/api/check-schedule', methods=['POST'])
def check_schedule():
    # Placeholder for checking flight schedule against NOTAMS
    # Expects a list of flights or a file upload (CSV content)
    # For now, just accepts JSON list of flights
    flights = request.json.get('flights', [])
    notams = get_all_notams()
    
    impacted_flights = []
    
    # Very basic matching logic: If NOTAM location matches Flight Origin or Destination
    for flight in flights:
        flight_impact = {'flight': flight, 'notams': []}
        for notam in notams:
            # Check if NOTAM location matches Dep or Arr
            # flight object expected: { 'flight_no': 'LO3805', 'dep': 'EPWA', 'arr': 'EPGD' }
            if notam['location'] and (notam['location'] == flight.get('dep') or notam['location'] == flight.get('arr')):
                flight_impact['notams'].append(notam)
        
        if flight_impact['notams']:
            impacted_flights.append(flight_impact)
            
    return jsonify(impacted_flights)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
