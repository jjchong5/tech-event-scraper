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
        'demo': ['demo day', 'demo', 'pitch day', 'showcase', 'product launch'],
        'vc_pitch': ['vc', 'venture capital', 'founder', 'investors', 'pitch', 'funding']
    }
    
    # SF location keywords
    SF_LOCATIONS = ['san francisco', 'sf', 'soma', 'mission', 'hayes valley', 
                    'financial district', 'fidi', 'tenderloin', 'nob hill',
                    'castro', 'marina', 'pac heights', 'russian hill']