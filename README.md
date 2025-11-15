# Tech Event Scraper

A web scraper that aggregates tech events from multiple sources in the San Francisco Bay Area and displays them in a beautiful, categorized web interface.

## Features

- 🎯 **Multi-Source Scraping**: Aggregates events from:
  - Gary's Guide
  - Eventbrite
  - Luma (coming soon - JavaScript-based)
  - Agenda Hero (coming soon - requires Selenium)

- 🏷️ **Smart Categorization**: Automatically categorizes events into:
  - Hackathons
  - Coding Hangouts
  - Marketing Events
  - Demo Days
  - VC Pitch Events
  - Other

- 📍 **Location Filtering**: Highlights events in San Francisco proper
- 🎨 **Beautiful UI**: Modern, responsive web interface with color-coded categories
- 📥 **Export**: Download all events as JSON

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd tech-event-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database (happens automatically on first run):
```bash
python app.py
```

## Usage

### Run the Web App

```bash
python app.py
```

Then open your browser to `http://localhost:5000`

### Manual Scraping

```bash
python -c "from scrapers.scraper import run_all_scrapers; run_all_scrapers()"
```

## Project Structure

```
tech-event-scraper/
├── app.py                 # Flask web application
├── config.py             # Configuration and keywords
├── requirements.txt      # Python dependencies
├── database/
│   ├── db_helper.py     # Database operations
│   └── schema.sql       # Database schema
├── scrapers/
│   ├── scraper.py       # Main scraper runner
│   ├── garys_guide.py   # Gary's Guide scraper
│   ├── eventbrite.py    # Eventbrite scraper
│   ├── luma.py          # Luma scraper (needs Selenium)
│   ├── agenda_hero.py   # Agenda Hero scraper (needs Selenium)
│   └── categorizer.py   # Event categorization logic
└── templates/
    └── index.html       # Web interface template
```

## Scraper Details

### Working Scrapers

**Gary's Guide** - Primary source for SF tech events. Uses BeautifulSoup to parse event listings.

**Eventbrite** - Secondary source. Scrapes tech events in San Francisco area.

### Future Scrapers

**Luma** and **Agenda Hero** - These sites use JavaScript to render content dynamically. They require Selenium/browser automation which can be resource-intensive. Currently disabled but can be enabled by fixing the ChromeDriver setup.

## Configuration

Edit `config.py` to customize:
- Category keywords for event classification
- SF location keywords
- Request timeout and user agent

## API Endpoints

- `GET /` - Main web interface
- `GET /api/events` - JSON API of all events
- `GET /refresh` - Trigger scraper refresh (runs in background)
- `GET /static/events_export.json` - Download events as JSON

## Database

SQLite database (`events.db`) with the following schema:
- Event title, date, time, location
- URL (unique per event)
- Description, category, source
- Price information
- Created/updated timestamps

Events are automatically:
- Deduplicated by title + date
- Cleaned up after 30 days

## Contributing

Feel free to add more scrapers or improve existing ones! Key files:
- Add new scraper in `scrapers/<source_name>.py`
- Register it in `scrapers/scraper.py`
- Update category keywords in `config.py`

## License

MIT License

## Notes

- The scraper respects robots.txt and uses reasonable delays
- Some sites (Luma, Agenda Hero) require Selenium due to JavaScript rendering
- ChromeDriver setup on Windows may require manual configuration
- Events are refreshed when you click "Refresh Events" in the UI

