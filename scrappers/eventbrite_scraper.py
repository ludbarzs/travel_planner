import re
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def fetch_eventbrite_page(destination, start_date):
    formatted_destination = destination.lower().replace(" ", "-")
    url = f"https://www.eventbrite.com/d/{formatted_destination}/events/?start_date={start_date}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            # Adding timout to allow dynamic JS values to populate the HTML
            print(f"Fetching events from: {url}")
            page.goto(url, timeout=60000)

            page.wait_for_load_state("networkidle")

            try:
                page.wait_for_selector(
                    "[class*=price], [class*=cost], [class*=fee]", timeout=5000
                )
            except:
                print("Price elements may not have loaded, continuing anyway...")

            page.evaluate("window.scrollBy(0, 1000)")
            page.wait_for_timeout(2000)

            page.evaluate("window.scrollBy(0, 1000)")
            page.wait_for_timeout(2000)

            return page.content(), url
        except Exception as e:
            print(f"Error fetching Eventbrite content: {e}")
            return None, url
        finally:
            browser.close()


def parse_events(html):
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    events_data = []
    seen_urls = set()

    event_cards = soup.select("section[class*='event-card']")
    print(f"Found {len(event_cards)} event cards")

    for card in event_cards[:100]:
        try:
            event = {}

            # For some reasons it repeatedly fetched the same card element multiple times
            # Validation to only output one of each event
            link = card.select_one("a[href*='/e/']")
            if not link:
                continue
            event_url = link["href"]
            if not event_url.startswith("http"):
                event_url = "https://www.eventbrite.com" + event_url

            if event_url in seen_urls:
                continue
            seen_urls.add(event_url)

            event["url"] = event_url
            event_id_match = re.search(r"/e/([^/?]+)", event_url)
            event["event_id"] = event_id_match.group(1) if event_id_match else None

            # Title
            title = card.select_one("h3") or card.select_one("h2")
            event["title"] = title.get_text(strip=True) if title else "No title"

            # Date/Time
            # Find date based on format, since there is no guaranteed structure
            datetime_text = "No date"
            for el in card.select("p"):
                txt = el.get_text(strip=True)
                if re.search(r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", txt) or re.search(
                    r"\b\d{1,2}:\d{2}", txt
                ):
                    datetime_text = txt
                    break
            event["datetime"] = datetime_text

            # Location
            location_el = card.select_one(
                'p[class*="event-card__clamp-line"]'
            ) or card.select_one("div[data-subcontent]")
            location_text = (
                location_el.get_text(strip=True) if location_el else "No location"
            )
            event["location"] = location_text

            # Price
            # Detection based on $ symbol
            price_text = "Unknown"
            for el in card.select("p, span, div"):
                txt = el.get_text(strip=True)
                if "$" in txt:
                    match = re.search(r"\$[\d,.]+", txt)
                    if match:
                        price_text = match.group(0)
                        break
            event["price"] = price_text

            if event["title"] != "No title":
                events_data.append(event)

        except Exception as e:
            print(f"Error parsing event card: {e}")
            continue

    return events_data


def get_events(destination, start_date):
    html, url = fetch_eventbrite_page(destination, start_date)
    if html:
        with open("page.html", "w", encoding="utf-8") as file:
            file.write(html)

        events = parse_events(html)
        return events, url
    return [], url


if __name__ == "__main__":
    destination = "new york"
    start_date = datetime.now().strftime("%Y-%m-%d")
    events, url = get_events(destination, start_date)

    print(f"Searched: {url}")
    print(f"Found {len(events)} events:")

    for i, event in enumerate(events, 1):
        print(f"\n{i}. {event.get('title', 'No title')}")
        print(f"   When: {event.get('datetime', 'No date')}")
        print(f"   Where: {event.get('location', 'No location')}")
        print(f"   Price: {event.get('price', 'No price')}")
