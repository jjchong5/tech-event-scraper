import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import re
from config import Config
from scrapers.categorizer import categorize_event

def scrape_eventbrite():
    """Scrape tech events from Eventbrite San Francisco"""
    # Search for tech/startup events in San Francisco
    url = "https://www.eventbrite.com/d/ca--san-francisco/tech--events/"
    
    headers = {'User-Agent': Config.USER_AGENT}
    response = requests.get(url, headers=headers, timeout=Config.REQUEST_TIMEOUT)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    events = []
    
    # Eventbrite uses search result cards for events
    event_cards = soup.find_all(['article', 'div'], class_=re.compile(r'(event-card|search-event-card)', re.I))
    
    # Also look for event links (Eventbrite event URLs contain /e/)
    event_links = soup.find_all('a', href=re.compile(r'/e/'))
    
    seen_titles = set()
    
    for link in event_links:
        try:
            title = link.get_text(strip=True)
            
            # Skip if no title or too short
            if not title or len(title) < 10:
                continue
            
            # Skip if already processed
            if title in seen_titles:
                continue
            
            href = link.get('href', '')
            if not href:
                continue
                
            event_url = href if href.startswith('http') else 'https://www.eventbrite.com' + href
            
            # Find parent container for date/time/location
            parent = link.find_parent(['article', 'div', 'li'])
            
            event_date = None
            event_time = None
            location = 'San Francisco, CA'
            price = 'Free'
            description = ''
            
            if parent:
                parent_text = parent.get_text(separator=' ', strip=True)
                
                # Try to extract description from parent
                # Look for description elements
                desc_elem = parent.find(['p', 'div'], class_=re.compile(r'(desc|summary|about)', re.I))
                if desc_elem:
                    desc_text = desc_elem.get_text(strip=True)
                    if desc_text and len(desc_text) > 20:
                        description = desc_text[:500]  # Limit length
                
                # Try to extract date/time
                # Eventbrite uses patterns like "Wed, Nov 26" or "Thursday at 4:00 PM"
                date_patterns = [
                    r'((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+\w+\s+\d{1,2},?\s+\d{4})',  # Wed, Nov 26, 2025
                    r'((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+\w+\s+\d{1,2})',  # Wed, Nov 26
                    r'(\w+\s+\d{1,2},?\s+\d{4})',  # November 26, 2025
                    r'((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+at\s+\d)',  # Thursday at 4
                    r'(\d{1,2}/\d{1,2}/\d{2,4})',  # 11/26/2025
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, parent_text)
                    if match:
                        try:
                            date_str = match.group(1)
                            # Remove "at X" from date string if present
                            date_str = re.sub(r'\s+at\s+\d.*$', '', date_str)
                            dt = parser.parse(date_str, fuzzy=False, default=datetime.now())
                            event_date = dt.date()
                            # If date is in the past, assume next year
                            if event_date < datetime.now().date():
                                event_date = event_date.replace(year=datetime.now().year + 1)
                            break
                        except:
                            pass
                
                # Try fuzzy parsing as last resort
                if not event_date:
                    try:
                        dt = parser.parse(parent_text, fuzzy=True, default=datetime.now())
                        event_date = dt.date()
                        # If date is in the past, assume next occurrence
                        if event_date < datetime.now().date():
                            event_date = event_date.replace(year=datetime.now().year + 1)
                    except:
                        pass
                
                # Try to extract time
                time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))'
                time_match = re.search(time_pattern, parent_text)
                if time_match:
                    try:
                        event_time = parser.parse(time_match.group(1)).time()
                    except:
                        pass
                
                # Check for price
                if 'free' in parent_text.lower():
                    price = 'Free'
                elif '$' in parent_text or 'CA$' in parent_text:
                    price_match = re.search(r'(?:CA)?\$[\d,]+(?:\.\d{2})?', parent_text)
                    if price_match:
                        price = price_match.group(0)
            
            category = categorize_event(title, description)
            
            # Only add events with dates
            if event_date:
                events.append({
                    'title': title,
                    'event_date': event_date,
                    'event_time': event_time,
                    'location': location,
                    'url': event_url,
                    'description': description,
                    'category': category,
                    'source': 'Eventbrite',
                    'price': price
                })
                seen_titles.add(title)
            
        except Exception as e:
            print(f"Error parsing Eventbrite event: {e}")
            continue
    
    return events

