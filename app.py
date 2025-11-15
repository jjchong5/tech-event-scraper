from flask import Flask, render_template, jsonify
from database.db_helper import get_all_events, init_db
from scrapers.scraper import run_all_scrapers
from scrapers.categorizer import is_sf_location
import json
from datetime import datetime
from threading import Thread
import os

# Initialize database on first run
if not os.path.exists('events.db'):
    init_db()

app = Flask(__name__)

# Category colors
CATEGORY_COLORS = {
    'hackathon': '#FF6B6B',      # Red
    'coding_hangout': '#4ECDC4', # Teal
    'marketing': '#FFE66D',      # Yellow
    'demo': '#95E1D3',           # Mint
    'vc_pitch': '#C7CEEA',       # Purple
    'other': '#CCCCCC'           # Gray
}

def export_to_json(events):
    """Export events to JSON file"""
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    events_list = []
    for event in events:
        event_dict = dict(event)
        # Convert date/time to strings
        if event_dict.get('event_date'):
            event_dict['event_date'] = str(event_dict['event_date'])
        if event_dict.get('event_time'):
            event_dict['event_time'] = str(event_dict['event_time'])
        if event_dict.get('created_at'):
            event_dict['created_at'] = str(event_dict['created_at'])
        if event_dict.get('updated_at'):
            event_dict['updated_at'] = str(event_dict['updated_at'])
        events_list.append(event_dict)
    
    with open('static/events_export.json', 'w') as f:
        json.dump(events_list, f, indent=2)

@app.route('/')
def index():
    """Main page displaying events"""
    events = get_all_events()
    
    # Add color and SF indicator to each event
    for event in events:
        event['color'] = CATEGORY_COLORS.get(event['category'], '#CCCCCC')
        event['is_sf'] = is_sf_location(event.get('location', ''))
        
        # Parse date/time strings for display
        if event.get('event_date'):
            if isinstance(event['event_date'], str):
                try:
                    event['event_date'] = datetime.strptime(event['event_date'], '%Y-%m-%d').date()
                except:
                    pass
        
        if event.get('event_time'):
            if isinstance(event['event_time'], str):
                try:
                    event['event_time'] = datetime.strptime(event['event_time'], '%H:%M:%S').time()
                except:
                    try:
                        event['event_time'] = datetime.strptime(event['event_time'], '%H:%M:%S.%f').time()
                    except:
                        pass
    
    # Group by category
    events_by_category = {}
    for event in events:
        category = event['category']
        if category not in events_by_category:
            events_by_category[category] = []
        events_by_category[category].append(event)
    
    # Export to JSON in background
    Thread(target=export_to_json, args=(events,)).start()
    
    return render_template('index.html', 
                         events_by_category=events_by_category,
                         category_colors=CATEGORY_COLORS)

@app.route('/refresh')
def refresh():
    """Trigger scraper refresh"""
    def scrape_async():
        run_all_scrapers()
    
    Thread(target=scrape_async).start()
    return jsonify({'status': 'Scraping started'})

@app.route('/api/events')
def api_events():
    """API endpoint to get all events"""
    events = get_all_events()
    # Convert to JSON-serializable format
    events_list = []
    for event in events:
        event_dict = dict(event)
        if event_dict.get('event_date'):
            event_dict['event_date'] = str(event_dict['event_date'])
        if event_dict.get('event_time'):
            event_dict['event_time'] = str(event_dict['event_time'])
        events_list.append(event_dict)
    return jsonify(events_list)

if __name__ == '__main__':
    app.run(debug=True, port=5000)