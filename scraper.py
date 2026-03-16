import requests
from bs4 import BeautifulSoup
import re
from timezonefinder import TimezoneFinder
from cache import get_cached, set_cached

WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_BASE = "https://en.wikipedia.org/wiki/"

headers = {
    "User-Agent": "Mozilla/5.0"
}
tf=TimezoneFinder()

def clean_text(text):
    return text.replace("\xa0", " ").replace("\ufeff", "").strip()

def parse_coordinates(coord_text):
    """
    Extract decimal lat/lon from a Wikipedia coordinate string.
    Handles formats like: '41°47′56″N 12°14′07″E' or '41.7989; 12.2353'
    """
    # Try decimal format first (e.g. from the geo span)
    decimal = re.findall(r"[-+]?\d+\.\d+", coord_text)
    if len(decimal) >= 2:
        return float(decimal[0]), float(decimal[1])

    # Try DMS format: degrees°minutes′seconds″ N/S/E/W
    dms = re.findall(r"(\d+)°(\d+)′(\d+)″\s*([NSEW])", coord_text)
    if len(dms) >= 2:
        def to_decimal(d, m, s, direction):
            val = int(d) + int(m) / 60 + int(s) / 3600
            if direction in ("S", "W"):
                val = -val
            return val
        lat = to_decimal(*dms[0])
        lon = to_decimal(*dms[1])
        return lat, lon

    return None, None

def get_airport_info_from_infobox(soup):
    infobox = soup.find("table", class_=lambda x: x and "infobox" in x)

    if not infobox:
        return {}

    info = {}
    last_th_key = None

    for row in infobox.find_all("tr"):
        th = row.find("th")
        td = row.find("td")

        if not td:
            continue

        if th:
            key = clean_text(th.get_text(" ", strip=True)).lower()
            last_th_key = key
        else:
            key = last_th_key  # sub-row like "• Summer (DST)"

        if not key:
            continue

        value = clean_text(td.get_text(" ", strip=True))

        if "location" in key:
            info["location"] = value
            parts = [p.strip() for p in value.split(",")]
            info["country"] = parts[-1]

        elif "coordinates" in key:
            coord_span = td.find("span", class_="geo")
            if coord_span:
                raw = coord_span.get_text()
                parts = raw.split(";")
                if len(parts) == 2:
                    try:
                        info["lat"] = float(parts[0].strip())
                        info["lon"] = float(parts[1].strip())
                    except ValueError:
                        pass
            if "lat" not in info:
                lat, lon = parse_coordinates(value)
                if lat is not None:
                    info["lat"] = lat
                    info["lon"] = lon
            info["coordinates"] = value

        elif "elevation" in key:
            info["elevation"] = value

        
    
    if "timezone" not in info and "lat" in info and "lon" in info:
        tz = tf.timezone_at(lat=info["lat"], lng=info["lon"])
        if tz:
            info["timezone"] = tz

    return info


def search_wikipedia(query):
    """
    Use the Wikipedia opensearch API to find the best matching page title,
    then fetch and parse that page. Much more reliable than scraping search results.
    """
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 5,
        "namespace": 0,
        "format": "json"
    }
    res = requests.get(WIKI_API, params=params, headers=headers, timeout=10)
    data = res.json()

    titles = data[1]   # list of matching titles
    urls = data[3]     # corresponding URLs

    for title, url in zip(titles, urls):
        print(f"Trying Wikipedia page: {title} -> {url}")
        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        info = get_airport_info_from_infobox(soup)
        if info.get("country"):
            return info

    return {}


def normalize_airport_name(name):
    return name.replace("(", "").replace(")", "").replace("  ", " ").strip()


def get_airport_info(airport_name):
    airport_name = normalize_airport_name(airport_name)

    cached = get_cached(airport_name)
    if cached:
        return cached
    
    # Always try Wikipedia opensearch first — it finds the correct page title
    # regardless of how the airport API names it
    search_query = airport_name
    if "airport" not in airport_name.lower():
        search_query = airport_name + " Airport"

    print(f"Searching Wikipedia for: {search_query}")
    info = search_wikipedia(search_query)

    if not info.get("country"):
        print("Wikipedia search failed, trying direct URL...")
        page_name = search_query.replace(" ", "_")
        url = WIKI_BASE + page_name
        print("Fetched URL:", url)
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        info = get_airport_info_from_infobox(soup)

    if info.get("country"):
        set_cached(airport_name, info)
        
    return info