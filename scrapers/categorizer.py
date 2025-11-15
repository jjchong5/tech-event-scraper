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
    """Check if location is in San Francisco"""
    if not location:
        return False
    location_lower = location.lower()
    return any(sf_keyword in location_lower for sf_keyword in Config.SF_LOCATIONS)