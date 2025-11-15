import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from config import Config
from scrapers.categorizer import categorize_event

def scrape_garys_guide():
    """Scrape events from Gary's Guide"""
    url = "https://www.garysguide.com/events?region=sf"
    
    headers = {'User-Agent': Config.USER_AGENT}
    response = requests.get(url, headers=headers, timeout=Config.REQUEST_TIMEOUT)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    events = []
    
    # Gary's Guide uses table rows for events
    # The structure has event info in table cells
    event_rows = soup.find_all('tr')
    
    for row in event_rows:
        try:
            # Find the event link
            link = row.find('a', href=lambda x: x and '/events/' in x)
            if not link:
                continue
                
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
                
            event_url = 'https://www.garysguide.com' + link.get('href', '')
            
            # Get all text from the row to extract info
            row_text = row.get_text(separator='|', strip=True)
            
            # Try to find date/time info
            cells = row.find_all('td')
            event_date = None
            event_time = None
            location = ''
            price = 'Free'
            description = ''
            
            # First cell usually has date/time
            if cells and len(cells) > 0:
                date_cell = cells[0].get_text(strip=True)
                try:
                    # Parse with default year to current year
                    dt = parser.parse(date_cell, fuzzy=True, default=datetime.now().replace(day=1))
                    event_date = dt.date()
                    event_time = dt.time()
                    
                    # If parsed date is in the past, assume it's for next year
                    if event_date < datetime.now().date():
                        event_date = event_date.replace(year=datetime.now().year + 1)
                except Exception as parse_error:
                    # Try alternative parsing if first attempt fails
                    try:
                        # Remove extra text and try again
                        date_text = date_cell.split('\n')[0].strip()
                        dt = parser.parse(date_text, fuzzy=True, default=datetime.now())
                        event_date = dt.date()
                        event_time = dt.time() if dt.time().hour != 0 else None
                        
                        if event_date < datetime.now().date():
                            event_date = event_date.replace(year=datetime.now().year + 1)
                    except:
                        pass
            
            # Look for location in row cells
            if len(cells) > 2:
                location_text = cells[2].get_text(strip=True)
                if location_text and not location_text.startswith('$'):
                    location = location_text
            
            # Try to extract description from row or find_next
            # Sometimes description is in a hidden element or next row
            desc_elem = row.find('div', class_=re.compile(r'desc', re.I))
            if desc_elem:
                description = desc_elem.get_text(strip=True)[:500]  # Limit length
            elif len(cells) > 1:
                # Try to get description from second cell
                desc_text = cells[1].get_text(strip=True)
                # Filter out the title from description
                if desc_text and desc_text != title and len(desc_text) > 20:
                    description = desc_text[:500]
            
            # Look for price
            if '$' in row_text:
                price_parts = [p for p in row_text.split('|') if '$' in p]
                if price_parts:
                    price = price_parts[0].strip()
            elif 'free' in row_text.lower():
                price = 'Free'
            
            # Categorize
            category = categorize_event(title, description)
            
            if event_date:  # Only add if we have a date
                events.append({
                    'title': title,
                    'event_date': event_date,
                    'event_time': event_time,
                    'location': location,
                    'url': event_url,
                    'description': description,
                    'category': category,
                    'source': 'Gary\'s Guide',
                    'price': price
                })
            
        except Exception as e:
            # Silently continue on errors to not spam output
            continue
    
    return events