from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def fetch_page_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            return page.content()
        except Exception as e:
            print(f"Error fetching page content: {e}")
            return None
        finally:
            browser.close()


def parse_flight_prices(html):
    soup = BeautifulSoup(html, "html.parser")
    flight_blocks = soup.find_all("so-fsr-flight-block")
    prices = []

    for block in flight_blocks:
        price_element = block.find("span", class_="amount")
        currency_element = block.find("span", class_="currency")

        if price_element and currency_element:
            price = price_element.text.strip()
            currency = currency_element.text.strip()
            prices.append(f"{price} {currency}")

    return prices


def get_flight_prices(departure, destination, departure_date, return_date, seats):
    url = (
        f"https://www.esky.com/flights/search/ap/{departure}/ap/{destination}"
        f"?departureDate={departure_date}&returnDate={return_date}&pa={seats}"
    )
    html = fetch_page_content(url)
    if html:
        prices = parse_flight_prices(html)
        return prices, url
    else:
        return [], url
