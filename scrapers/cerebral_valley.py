import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import time
import re
from config import Config
from scrapers.categorizer import categorize_event, is_virtual_event

def scrape_cerebral_valley():
    """Scrape events from Cerebral Valley using undetected-chromedriver"""
    url = "https://cerebralvalley.ai/events"
    
    events = []
    driver = None
    
    try:
        # Initialize Chrome driver
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        driver = uc.Chrome(options=options, version_main=None)
        driver.get(url)
        time.sleep(6)  # Wait for JavaScript
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all links that might be events
        all_links = soup.find_all('a', href=True)
        
        seen_titles = set()
        
        for link in all_links:
            try:
                href = link.get('href', '')
                
                # Filter for event-looking links
                if not href or href.startswith('#') or len(href) < 5:
                    continue
                
                # Skip navigation/UI links
                if any(skip in href.lower() for skip in ['/home', '/about', '/contact', '/login', '/signup']):
                    continue
                
                # Get title
                title = link.get_text(strip=True)
                
                # Try nested elements
                if not title or len(title) < 10:
                    for tag in ['h1', 'h2', 'h3', 'h4', 'div', 'span']:
                        elem = link.find(tag)
                        if elem:
                            title = elem.get_text(strip=True)
                            if len(title) >= 10:
                                break
                
                # Skip if no valid title
                if not title or len(title) < 10:
                    continue
                
                # Skip duplicates
                if title in seen_titles:
                    continue
                
                # Skip UI elements
                skip_keywords = ['read more', 'learn more', 'sign up', 'register here', 
                               'view all', 'see more', 'explore', 'menu', 'navigation']
                if any(skip in title.lower() for skip in skip_keywords):
                    continue
                
                # Build full URL
                if href.startswith('http'):
                    event_url = href
                elif href.startswith('/'):
                    event_url = 'https://cerebralvalley.ai' + href
                else:
                    event_url = 'https://cerebralvalley.ai/' + href
                
                # Find parent for metadata
                parent = link.find_parent(['article', 'div', 'section', 'li'])
                
                event_date = None
                event_time = None
                location = 'San Francisco Bay Area, CA'
                
                if parent:
                    parent_text = parent.get_text(separator=' ', strip=True)
                    
                    # Try to extract date
                    date_patterns = [
                        r'(\w+\s+\d{1,2},?\s+\d{4})',  # "November 15, 2025"
                        r'(\w+\s+\d{1,2})',  # "November 15"
                        r'(\d{1,2}/\d{1,2}/\d{2,4})',  # "11/15/2025"
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, parent_text)
                        if match:
                            try:
                                dt = parser.parse(match.group(1), fuzzy=False, default=datetime.now())
                                event_date = dt.date()
                                if event_date < datetime.now().date():
                                    event_date = event_date.replace(year=datetime.now().year + 1)
                                break
                            except:
                                pass
                    
                    # Fuzzy parsing fallback
                    if not event_date:
                        try:
                            dt = parser.parse(parent_text, fuzzy=True, default=datetime.now())
                            event_date = dt.date()
                            if event_date < datetime.now().date():
                                event_date = event_date.replace(year=datetime.now().year + 1)
                        except:
                            pass
                    
                    # Extract time
                    time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))', parent_text)
                    if time_match:
                        try:
                            event_time = parser.parse(time_match.group(1)).time()
                        except:
                            pass
                    
                    # Extract location
                    if 'san francisco' in parent_text.lower():
                        location = 'San Francisco, CA'
                    elif any(loc in parent_text.lower() for loc in ['palo alto', 'oakland', 'berkeley', 'mountain view']):
                        for loc_name in ['Palo Alto', 'Oakland', 'Berkeley', 'Mountain View']:
                            if loc_name.lower() in parent_text.lower():
                                location = f'{loc_name}, CA'
                                break
                
                # Only add if we have a date
                if event_date:
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
                        'source': 'Cerebral Valley',
                        'price': 'Free',
                        'is_virtual': is_virtual
                    })
                    seen_titles.add(title)
                    
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"Error scraping Cerebral Valley: {e}")
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return events

