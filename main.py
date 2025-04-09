from scrappers.esky_scraper import get_flight_prices
from utils.user_input import get_user_input


def get_airport_code(city):
    # From city name to airport code
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


def main():
    user_data = get_user_input()

    departure_code = get_airport_code(user_data["departure_city"])
    destination_code = get_airport_code(user_data["destination_city"])

    print("\nSearching for flights...")
    print(f"From: {user_data['departure_city']} ({departure_code})")
    print(f"To: {user_data['destination_city']} ({destination_code})")
    print(f"Departure: {user_data['departure_date']}")
    print(
        f"Return: {user_data['return_date'] if user_data['return_date'] else 'One-way'}"
    )
    print(f"Passengers: {user_data['seats']}")

    prices = get_flight_prices(
        departure_code,
        destination_code,
        user_data["departure_date"],
        user_data["return_date"] or "",  # If one way flight, leave empty
        user_data["seats"],
    )

    if prices:
        print("\nPrices found:")
        for i, price in enumerate(prices, 1):
            print(f"{i}. {price}")
    else:
        print("\nNo flights found")

    print("\nDone!")


if __name__ == "__main__":
    main()

