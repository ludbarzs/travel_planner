import threading

from scrappers.esky_scraper import get_flight_prices
from scrappers.eventbrite_scraper import get_events
from utils.database import (
    initialize_db,
    save_events,
    save_flight_prices,
)
from utils.table_display import (
    display_combined_table,
    display_event_table,
    display_flight_table,
    get_events_table,
    get_flights_table,
)


def get_airport_code(city):
    airport_codes = {
        "malaga": "AGP",
        "riga": "RIX",
        "new york": "NYC",
        "los angeles": "LAX",
        "london": "LON",
        "paris": "PAR",
        "tokyo": "TYO",
        "sydney": "SYD",
        "berlin": "BER",
        "madrid": "MAD",
    }
    return airport_codes.get(city.lower(), city.upper()[:3])


# Run eSky scraper
def scrape_esky(
    departure_code, destination_code, departure_date, return_date, seats, results
):
    print("\nSearching for flights...")
    prices, search_url = get_flight_prices(
        departure_code,
        destination_code,
        departure_date,
        return_date or "",
        seats,
    )

    results["flight_prices"] = prices
    results["flight_url"] = search_url


# Run Eventbrite scraper
def scrape_eventbrite(destination_city, departure_date, results):
    print(f"\nSearching for events in {destination_city}...")
    events, events_url = get_events(destination_city, departure_date)

    results["events"] = events
    results["events_url"] = events_url


def main():
    initialize_db()

    # user_data = get_user_input()
    user_data = {
        "departure_city": "Riga",
        "destination_city": "New york",
        "departure_date": "2025-04-20",
        "return_date": "",
        "seats": "1",
    }

    departure_code = get_airport_code(user_data["departure_city"])
    destination_code = get_airport_code(user_data["destination_city"])

    print(f"\nFrom: {user_data['departure_city']} ({departure_code})")
    print(f"To: {user_data['destination_city']} ({destination_code})")
    print(f"Departure: {user_data['departure_date']}")
    print(
        f"Return: {user_data['return_date'] if user_data['return_date'] else 'One-way'}"
    )
    print(f"Passengers: {user_data['seats']}")

    results = {"flight_prices": [], "flight_url": "", "events": [], "events_url": ""}

    # Start scrapers in parallel threads
    flight_thread = threading.Thread(
        target=scrape_esky,
        args=(
            departure_code,
            destination_code,
            user_data["departure_date"],
            user_data["return_date"],
            user_data["seats"],
            results,
        ),
    )

    event_thread = threading.Thread(
        target=scrape_eventbrite,
        args=(user_data["destination_city"], user_data["departure_date"], results),
    )

    flight_thread.start()
    event_thread.start()

    flight_thread.join()
    event_thread.join()

    # Process flight results
    prices = results["flight_prices"]
    if prices:
        # print("\nPrices found:")
        # for i, price in enumerate(prices, 1):
        #     print(f"{i}. {price}")
        #
        save_flight_prices(
            user_data["departure_city"],
            departure_code,
            user_data["destination_city"],
            destination_code,
            user_data["departure_date"],
            user_data["return_date"],
            prices,
            user_data["seats"],
        )
    else:
        print("\nNo flights found")

    # Process event results
    events = results["events"]
    if events:
        print(f"\nFound {len(events)} events in {user_data['destination_city']}:")
        # for i, event in enumerate(events[:5], 1):  # Limit to first 5 events for display
        # print(f"\n{i}. {event.get('title', 'No title')}")
        # print(f"   When: {event.get('datetime', 'No date')}")
        # print(f"   Where: {event.get('location', 'No location')}")
        # print(f"   Price: {event.get('price', 'No price')}")
        save_events(user_data["destination_city"], events)
    else:
        print(f"\nNo events found in {user_data['destination_city']}")

    print("\n========== PANDAS TABLE DISPLAY ==========")

    # Get flight data as DataFrame and display
    flight_df = get_flights_table(limit=5)
    display_flight_table(flight_df)

    # Get events data as DataFrame and display
    event_df = get_events_table(city=user_data["destination_city"], limit=5)
    display_event_table(event_df)

    # Show combined travel summary
    print("\n=== COMBINED TRAVEL SUMMARY ===")
    display_combined_table(
        user_data["destination_city"],
        user_data["departure_date"],
        user_data["return_date"],
    )

    print("\nDone!")


if __name__ == "__main__":
    main()
