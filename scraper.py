import requests
from bs4 import BeautifulSoup

WIKI_BASE = "https://en.wikipedia.org/wiki/"
WIKI_SEARCH = "https://en.wikipedia.org/w/index.php"
headers = {
    "User-Agent": "Mozilla/5.0"
}

def clean_text(text):
    return text.replace("\xa0", " ").replace("\ufeff", "").strip()


def get_airport_info_from_infobox(soup):
    infobox = soup.find("table", class_=lambda x: x and "infobox" in x)

    if not infobox:
        print("Infobox not found")
        return {}

    info = {}

    for row in infobox.find_all("tr"):
        th = row.find("th")
        td = row.find("td")

        if not th or not td:
            continue

        key = th.get_text(strip=True).lower()
        value = clean_text(td.get_text(" ", strip=True))

        print("Key:", key)

        if "location" in key:
            info["location"] = value
            info["country"] = value.split(",")[-1].strip()

        elif "coordinates" in key:
            parts = value.split("/")
            info["coordinates"] = clean_text(parts[-1])

        elif "elevation" in key:
            info["elevation"] = value
        elif "time zone" in key:
            info["timezone"] = value

    return info


def normalize_airport_name(name):
    name = name.replace("(", "")
    name = name.replace(")", "")
    name = name.replace("  ", " ")
    return name.strip()


def get_airport_info(airport_name):
    airport_name = normalize_airport_name(airport_name)

    if "airport" not in airport_name.lower():
        page_name = airport_name.replace(" ", "_") + "_Airport"
    else:
        page_name = airport_name.replace(" ", "_")
    url = WIKI_BASE + page_name

    print("Fetched URL:", url)

    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    info = get_airport_info_from_infobox(soup)

    # If infobox not found, try Wikipedia search
    if not info:
        print("Trying search fallback...")

        params = {"search": airport_name + " airport"}
        res = requests.get(WIKI_SEARCH, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        result = soup.select_one(".mw-search-result-heading a")

        if result:
            new_url = "https://en.wikipedia.org" + result["href"]
            print("Fetched URL:", new_url)

            page = requests.get(new_url, headers=headers)
            page_soup = BeautifulSoup(page.text, "html.parser")

            info = get_airport_info_from_infobox(page_soup)

    return info