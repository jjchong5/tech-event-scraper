from config import Config

def categorize_event(title, description=''):
    """Categorize event based on keywords in title and description"""
    text = f"{title} {description}".lower()
    
    # Count keyword matches for each category
    scores = {}
    for category, keywords in Config.CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for keyword in keywords if keyword in text)
    
    # Special case: VC/Pitch needs multiple founder/VC mentions
    if 'vc_pitch' in scores:
        founder_vc_count = text.count('founder') + text.count('vc') + text.count('venture')
        if founder_vc_count < 2:
            scores['vc_pitch'] = 0
    
    # Return category with highest score, or 'other'
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return 'other'

def is_sf_location(location):
    """Check if location is in San Francisco city proper"""
    if not location:
        return False
    location_lower = location.lower()
    
    # First check if it's explicitly a non-SF city (exclude these)
    if any(non_sf_city in location_lower for non_sf_city in Config.NON_SF_CITIES):
        return False
    
    # Check for "SF" or "SF," but not "South SF" or as part of another word
    if ' sf' in location_lower or ',sf' in location_lower or location_lower.startswith('sf'):
        # Make sure it's not "South SF" or similar
        if 'south sf' not in location_lower and 'ssf' not in location_lower:
            return True
    
    # Check for San Francisco neighborhoods and "san francisco" itself
    return any(sf_keyword in location_lower for sf_keyword in Config.SF_LOCATIONS)

def is_virtual_event(title, description='', location=''):
    """Check if event is virtual/online"""
    text = f"{title} {description} {location}".lower()
    return any(keyword in text for keyword in Config.VIRTUAL_KEYWORDS)