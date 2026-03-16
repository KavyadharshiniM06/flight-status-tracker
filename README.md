# ✈️ Flight Status Tracker

A Python tool to look up real-time flight status, departure/arrival times, delay info, and airport details.

Available as both a **CLI app** and a **Flask web UI**.

## Features
- Real-time flight status via AviationStack API
- Scheduled, estimated, and actual departure/arrival times
- Live delay indicator
- Terminal and gate info
- Airport country and timezone via Wikipedia + timezonefinder
- Airport info cached locally for 7 days

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/flight-status-tracker.git
cd flight-status-tracker
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Get a free API key from [aviationstack.com](https://aviationstack.com), then:
```bash
cp .env.example .env
```
Edit `.env` and add your key:
```
AVIATIONSTACK_API_KEY=your_api_key_here
```

## Usage

### CLI
```bash
python app.py
```
```
Enter flight IATA number: AI101

✈️  Flight Status
---------------------------
Airline:  Air India
Flight:   AI101
Status:   scheduled

Departure:
  Airport:    Leonardo Da Vinci (Fiumicino)
  Country:    Italy
  Timezone:   Europe/Rome
  Terminal:   3
  Scheduled:  2026-03-16 10:50 UTC
  Delay:      ✅ On time
```

### Web UI
```bash
python web.py
```
Open `http://127.0.0.1:5000` in your browser.

### Tests
```bash
pytest tests/ -v
```

## Project Structure
```
flight-status-tracker/
├── app.py            # CLI entry point
├── web.py            # Flask web UI
├── api.py            # AviationStack API client
├── scraper.py        # Wikipedia airport info scraper
├── cache.py          # JSON file cache for airport data
├── templates/
│   └── index.html    # Flask HTML template
├── tests/
│   ├── test_api.py
│   ├── test_scraper.py
│   └── test_cache.py
├── .env.example
├── requirements.txt
└── README.md
```

## Requirements
- Python 3.8+
- Free [AviationStack](https://aviationstack.com) API key