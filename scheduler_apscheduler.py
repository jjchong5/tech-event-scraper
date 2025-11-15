#!/usr/bin/env python3
"""
Alternative scheduler using APScheduler (more robust for production)
This can run as a background service or integrated into Flask
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from scrapers.scraper import run_all_scrapers
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scrape_phase1():
    """Scrape Phase 1 sources (fast, no Selenium)"""
    logger.info("Starting Phase 1 scrape...")
    try:
        inserted = run_all_scrapers(phase=1)
        logger.info(f"Phase 1 scrape completed. Inserted/updated {inserted} events")
    except Exception as e:
        logger.error(f"Phase 1 scrape failed: {e}", exc_info=True)

def scrape_phase2():
    """Scrape all sources including Phase 2 (slower, uses Selenium)"""
    logger.info("Starting Phase 2 scrape (all sources)...")
    try:
        inserted = run_all_scrapers(phase=2)
        logger.info(f"Phase 2 scrape completed. Inserted/updated {inserted} events")
    except Exception as e:
        logger.error(f"Phase 2 scrape failed: {e}", exc_info=True)

def main():
    """Main scheduler using APScheduler"""
    scheduler = BlockingScheduler()
    
    # Daily scrape at 6 AM (Phase 1 - fast)
    scheduler.add_job(
        scrape_phase1,
        CronTrigger(hour=6, minute=0),
        id='daily_scrape',
        name='Daily Phase 1 Scrape at 6 AM',
        replace_existing=True
    )
    
    # Weekly deep scrape on Monday at 8 AM (Phase 2 - includes all sources)
    scheduler.add_job(
        scrape_phase2,
        CronTrigger(day_of_week='mon', hour=8, minute=0),
        id='weekly_scrape',
        name='Weekly Phase 2 Scrape on Monday at 8 AM',
        replace_existing=True
    )
    
    # Optional: Every 12 hours for frequent updates
    # scheduler.add_job(
    #     scrape_phase1,
    #     'interval',
    #     hours=12,
    #     id='frequent_scrape',
    #     name='Every 12 Hours Phase 1 Scrape'
    # )
    
    logger.info("="*60)
    logger.info("Tech Event Scraper - APScheduler")
    logger.info("="*60)
    logger.info("Scheduled jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  • {job.name} (next run: {job.next_run_time})")
    logger.info("="*60)
    
    # Run initial scrape
    logger.info("Running initial scrape...")
    scrape_phase1()
    
    # Start scheduler
    logger.info("Scheduler started. Press Ctrl+C to stop")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")

if __name__ == '__main__':
    main()

