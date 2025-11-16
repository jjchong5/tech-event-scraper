import os

class Config:
    # Scraping settings
    REQUEST_TIMEOUT = 10
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    # Category keywords
    CATEGORY_KEYWORDS = {
        'hackathon': ['hackathon', 'hack night', 'hacknight', 'buildathon'],
        'coding_hangout': ['meetup', 'coworking', 'coffee', 'networking', 'hangout', 'social'],
        'marketing': ['marketing', 'growth', 'seo', 'content', 'branding'],
        'demo': ['demo day', 'demo', 'pitch day', 'showcase', 'product launch', 'hands-on', 'workshop'],
        'vc_pitch': ['vc', 'venture capital', 'founder', 'investors', 'pitch', 'funding']
    }
    
    # SF location keywords (city proper only)
    SF_LOCATIONS = ['san francisco', 'civic center', 'soma', 'mission', 'hayes valley', 
                    'financial district', 'fidi', 'tenderloin', 'nob hill',
                    'castro', 'marina', 'pac heights', 'russian hill', 'north beach',
                    'potrero hill', 'dogpatch', 'haight', 'inner sunset', 'outer sunset',
                    'richmond district', 'presidio', 'embarcadero', 'jackson square']
    
    # Non-SF Bay Area cities to exclude
    NON_SF_CITIES = ['oakland', 'berkeley', 'palo alto', 'mountain view', 'san jose',
                     'sunnyvale', 'santa clara', 'cupertino', 'redwood city', 'menlo park',
                     'san mateo', 'south san francisco', 'daly city', 'fremont', 'hayward',
                     'milpitas', 'san leandro', 'alameda', 'emeryville']
    
    # Virtual event keywords
    VIRTUAL_KEYWORDS = ['virtual', 'online', 'remote', 'zoom', 'webinar', 'livestream', 
                        'live stream', 'video call', 'video conference', 'virtual event',
                        'online event', 'remote event', 'hybrid']