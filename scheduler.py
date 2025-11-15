#!/usr/bin/env python3
"""
Background scheduler for automatically running scrapers
"""
import schedule
import time
from datetime import datetime
from scrapers.scraper import run_all_scrapers
import sys

def scrape_job(phase=1):
    """Job to run scrapers"""
    print(f"\n{'='*60}")
    print(f"Running scheduled scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        inserted = run_all_scrapers(phase=phase)
        print(f"\n✓ Scheduled scrape completed. Inserted/updated {inserted} events")
    except Exception as e:
        print(f"\n✗ Scheduled scrape failed: {e}")
    
    print(f"\n{'='*60}\n")

def main():
    """Main scheduler loop"""
    print("="*60)
    print("Tech Event Scraper - Scheduler")
    print("="*60)
    print("\nSchedule Configuration:")
    print("  • Daily at 6:00 AM")
    print("  • Every Monday at 8:00 AM")
    print("\nPhase: 1 (Gary's Guide, Eventbrite, Agenda Hero)")
    print("To include Phase 2 (Luma calendars, Cerebral Valley, Meetup),")
    print("modify the schedule calls in scheduler.py")
    print("\nPress Ctrl+C to stop")
    print("="*60)
    
    # Schedule jobs
    # Daily scrape at 6 AM
    schedule.every().day.at("06:00").do(scrape_job, phase=1)
    
    # Weekly scrape on Monday at 8 AM (with Phase 2)
    schedule.every().monday.at("08:00").do(scrape_job, phase=2)
    
    # Optional: Run every 12 hours
    # schedule.every(12).hours.do(scrape_job, phase=1)
    
    # Run once immediately on startup
    print("\nRunning initial scrape...")
    scrape_job(phase=1)
    
    # Keep running scheduled jobs
    print("\nScheduler started. Waiting for scheduled times...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    main()

