import sqlite3

import pandas as pd

DB_FILE = "travel_planner.db"


def connect_to_db():
    conn = sqlite3.connect(DB_FILE)
    return conn


def get_flights_table(limit=10, destination=None, departure=None):
    conn = connect_to_db()

    query = """
    SELECT 
        departure_city, 
        departure_code, 
        destination_city, 
        destination_code, 
        departure_date, 
        return_date,
        price, 
        currency, 
        seats,
        search_date
    FROM flight_tickets
    """

    conditions = []
    params = []

    if destination:
        conditions.append("destination_city LIKE ?")
        params.append(f"%{destination}%")

    if departure:
        conditions.append("departure_city LIKE ?")
        params.append(f"%{departure}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY search_date DESC, price ASC LIMIT ?"
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)

    if not df.empty:
        df["return_date"] = df["return_date"].fillna("One-way")
        df["price"] = df["price"].map(lambda x: f"{x:,.2f}")
        df["full_price"] = df.apply(
            lambda row: f"{row['price']} {row['currency']}", axis=1
        )

        # Format dates
        df["departure_date"] = pd.to_datetime(df["departure_date"]).dt.strftime(
            "%b %d, %Y"
        )
        df["search_date"] = pd.to_datetime(df["search_date"]).dt.strftime(
            "%b %d, %Y %H:%M"
        )

        mask = df["return_date"] != "One-way"
        if mask.any():
            df.loc[mask, "return_date"] = pd.to_datetime(
                df.loc[mask, "return_date"]
            ).dt.strftime("%b %d, %Y")

    conn.close()
    return df


def get_events_table(city=None, limit=10):
    conn = connect_to_db()

    query = """
    SELECT 
        city,
        title,
        datetime,
        location,
        price,
        url,
        search_date
    FROM events
    """

    params = []
    if city:
        query += " WHERE city LIKE ?"
        params.append(f"%{city}%")

    query += " ORDER BY search_date DESC LIMIT ?"
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)

    if not df.empty:
        df["search_date"] = pd.to_datetime(df["search_date"]).dt.strftime(
            "%b %d, %Y %H:%M"
        )

        df["title"] = df["title"].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
        df["location"] = df["location"].apply(
            lambda x: x[:30] + "..." if len(x) > 30 else x
        )

    conn.close()
    return df


def display_flight_table(df, show_codes=True):
    if df.empty:
        print("No flight data found.")
        return

    display_cols = [
        "departure_city",
        "destination_city",
        "departure_date",
        "return_date",
        "full_price",
        "seats",
    ]

    if show_codes:
        display_cols = [
            "departure_city",
            "departure_code",
            "destination_city",
            "destination_code",
        ] + display_cols[2:]

    rename_dict = {
        "departure_city": "From",
        "departure_code": "Code",
        "destination_city": "To",
        "destination_code": "Code",
        "departure_date": "Departure",
        "return_date": "Return",
        "full_price": "Price",
        "seats": "Seats",
    }

    display_df = df[display_cols].rename(columns=rename_dict)

    print("\nFlight Search Results:")
    print(display_df.to_string(index=False))
    print(f"\nTotal flights found: {len(df)}")


def display_event_table(df):
    if df.empty:
        print("No event data found.")
        return

    display_cols = ["city", "title", "datetime", "location", "price"]
    rename_dict = {
        "city": "City",
        "title": "Event",
        "datetime": "Date & Time",
        "location": "Location",
        "price": "Price",
    }

    display_df = df[display_cols].rename(columns=rename_dict)

    print("\nEvent Search Results:")
    print(display_df.to_string(index=False))
    print(f"\nTotal events found: {len(df)}")


def display_combined_table(destination, departure_date, return_date=None):
    flight_df = get_flights_table(limit=5, destination=destination)
    event_df = get_events_table(city=destination, limit=10)

    if flight_df.empty or event_df.empty:
        print(f"Not enough data for a combined travel plan to {destination}")

        if not flight_df.empty:
            display_flight_table(flight_df)

        if not event_df.empty:
            display_event_table(event_df)

        return

    travel_df = pd.DataFrame(
        {
            "Destination": [destination],
            "Departure Date": [departure_date],
            "Return Date": [return_date if return_date else "One-way"],
            "Cheapest Flight": [
                f"{flight_df.iloc[0]['price']} {flight_df.iloc[0]['currency']}"
            ],
            "Num. Events Found": [len(event_df)],
            "Example Event": [
                event_df.iloc[0]["title"] if not event_df.empty else "No events found"
            ],
            "Event Date": [event_df.iloc[0]["datetime"] if not event_df.empty else ""],
        }
    )

    print("\n=== Travel Plan Summary ===")
    print(travel_df.to_string(index=False))

    display_flight_table(flight_df)
    display_event_table(event_df.head())
