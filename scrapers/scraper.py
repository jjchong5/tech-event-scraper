from scrapers.garys_guide import scrape_garys_guide
from scrapers.agenda_hero import scrape_agenda_hero
from scrapers.eventbrite import scrape_eventbrite
from scrapers.luma import scrape_luma_genai_sf, scrape_luma_ai_events, scrape_luma_ai_sf
from scrapers.cerebral_valley import scrape_cerebral_valley
from scrapers.meetup import scrape_meetup
from database.db_helper import insert_event, clear_old_events

def run_all_scrapers(phase=1):
    """Run all scrapers and store results
    
    Args:
        phase: 1 for Phase 1 only, 2 for all scrapers
    """
    print("Starting scraper run...")
    
    # Clear old events first
    clear_old_events()
    
    all_events = []
    
    # Gary's Guide - Primary source (no Selenium needed)
    try:
        print("Scraping Gary's Guide...")
        events = scrape_garys_guide()
        all_events.extend(events)
        print(f"Found {len(events)} events from Gary's Guide")
    except Exception as e:
        print(f"Error scraping Gary's Guide: {e}")
    
    # Eventbrite (no Selenium needed)
    try:
        print("Scraping Eventbrite...")
        events = scrape_eventbrite()
        all_events.extend(events)
        print(f"Found {len(events)} events from Eventbrite")
    except Exception as e:
        print(f"Error scraping Eventbrite: {e}")
    
    # Agenda Hero (requires Selenium)
    try:
        print("Scraping Agenda Hero (using browser automation, may take a moment)...")
        events = scrape_agenda_hero()
        all_events.extend(events)
        print(f"Found {len(events)} events from Agenda Hero")
    except Exception as e:
        print(f"Agenda Hero scraping skipped: {e}")
    
    # Phase 2 scrapers (requires Selenium) - only run if phase >= 2
    if phase >= 2:
        phase2_scrapers = [
            ("Luma GenAI SF", scrape_luma_genai_sf),
            ("Luma AI Events", scrape_luma_ai_events),
            ("Luma AI SF", scrape_luma_ai_sf),
            ("Cerebral Valley", scrape_cerebral_valley),
            ("Meetup", scrape_meetup),
        ]
        
        for name, scraper_func in phase2_scrapers:
            try:
                print(f"Scraping {name} (using browser automation)...")
                events = scraper_func()
                all_events.extend(events)
                print(f"Found {len(events)} events from {name}")
            except Exception as e:
                print(f"Error scraping {name}: {e}")
    
    # Insert into database
    inserted = 0
    skipped = 0
    for event in all_events:
        if event['event_date']:  # Only insert if we have a valid date
            if insert_event(event):
                inserted += 1
            else:
                skipped += 1
    
    print(f"Inserted/updated {inserted} events, skipped {skipped} duplicates")
    return inserted