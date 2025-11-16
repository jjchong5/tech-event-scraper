import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import time
import re
from config import Config
from scrapers.categorizer import categorize_event, is_virtual_event

def scrape_agenda_hero():
    """Scrape events from Agenda Hero SF/Bay Area AI Events using undetected-chromedriver
    
    This scraper uses undetected-chromedriver which automatically manages ChromeDriver
    installation and avoids detection issues.
    """
    url = "https://agendahero.com/schedule/sf-and-bay-area-ai-events-0f8899a0-3dbc-4d6a-ad05-58225b751316?view=month"
    
    events = []
    driver = None
    
    try:
        # Initialize Chrome driver with undetected-chromedriver
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')  # New headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        driver = uc.Chrome(options=options, version_main=None)  # Auto-detect Chrome version
        
        # Load the page
        driver.get(url)
        
        # Wait for content to load (wait for event elements to appear)
        time.sleep(5)  # Give it time to load JavaScript content
        
        # Get the page source after JavaScript has rendered
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Agenda Hero displays events in calendar format
        # Events are in the body text with emojis and formatted as:
        # "💻 Event Title, Time Location"
        body = soup.find('body')
        if not body:
            print("No body found in Agenda Hero page")
            return []
        
        body_text = body.get_text(separator='\n', strip=True)
        lines = body_text.split('\n')
        
        processed_titles = set()
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_day = None
        
        for line in lines:
            line = line.strip()
            
            # Try to detect date headers (e.g., "Oct 26", "Nov 15")
            date_match = re.match(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})$', line)
            if date_match:
                month_str = date_match.group(1)
                day = int(date_match.group(2))
                try:
                    month_num = datetime.strptime(month_str, '%b').month
                    # If month is less than current month, it's likely next year
                    # If month is same or later, it's this year
                    year = current_year
                    test_date = datetime(year, month_num, day).date()
                    if test_date < datetime.now().date():
                        year = current_year + 1
                    current_day = datetime(year, month_num, day).date()
                except:
                    pass
                continue
            
            # Check if line looks like an event (has emoji or starts with special char)
            # Events typically start with emoji and have time info
            if not line or len(line) < 15:
                continue
            
            # Skip obvious non-events
            skip_keywords = ['agendahero', 'make any schedule', 'log in', 'create for free', 
                           'submit event', 'month', 'today', 'times in', 'filter', 'follow',
                           'sun mon tue wed', 'gallery']
            if any(skip in line.lower() for skip in skip_keywords):
                continue
            
            # Look for lines that contain time patterns (likely events)
            time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))', line)
            if not time_match and current_day is None:
                continue
            
            # Extract event title (remove emoji at start if present)
            title = re.sub(r'^[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]\s*', '', line)
            
            # Further clean title - remove location and time at end
            title = re.split(r'\s+\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)', title)[0]
            title = title.strip(',').strip()
            
            if not title or len(title) < 10 or title in processed_titles:
                continue
            
            # Parse time if available
            event_time = None
            if time_match:
                try:
                    event_time = parser.parse(time_match.group(1)).time()
                except:
                    pass
            
            # Extract location from line
            location = 'San Francisco Bay Area, CA'
            if 'san francisco' in line.lower():
                location = 'San Francisco, CA'
            elif any(loc in line.lower() for loc in ['palo alto', 'oakland', 'berkeley', 'mountain view']):
                for loc in ['Palo Alto', 'Oakland', 'Berkeley', 'Mountain View']:
                    if loc.lower() in line.lower():
                        location = f'{loc}, CA'
                        break
            
            # Use current_day if we have it, otherwise try to parse from context
            event_date = current_day
            if not event_date:
                # Try fuzzy date parsing as fallback
                try:
                    dt = parser.parse(line, fuzzy=True, default=datetime.now())
                    event_date = dt.date()
                    if event_date < datetime.now().date():
                        event_date = event_date.replace(year=datetime.now().year + 1)
                except:
                    continue  # Skip if we can't determine date
            
            # Generate event URL (Agenda Hero doesn't have individual event pages usually)
            event_url = url
            
            category = categorize_event(title)
            is_virtual = is_virtual_event(title, '', location)
            
            events.append({
                'title': title,
                'event_date': event_date,
                'event_time': event_time,
                'location': location,
                'url': event_url,
                'description': '',
                'category': category,
                'source': 'Agenda Hero',
                'price': 'Free',
                'is_virtual': is_virtual
            })
            processed_titles.add(title)
        
    except Exception as e:
        print(f"Error with Selenium scraping Agenda Hero: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return events