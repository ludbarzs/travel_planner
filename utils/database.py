import sqlite3

DB_FILE = "travel_app.db"


def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flight_tickets (
        id INTEGER PRIMARY KEY,
        departure_city TEXT,
        departure_code TEXT,
        destination_city TEXT, 
        destination_code TEXT,
        departure_date TEXT,
        return_date TEXT,
        price REAL,
        currency TEXT,
        seats INTEGER,
        search_date TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_flight_prices(
    departure_city,
    departure_code,
    destination_city,
    destination_code,
    departure_date,
    return_date,
    prices,
    seats,
):
    from datetime import datetime

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    search_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, price_str in enumerate(prices):
        parts = price_str.strip().split()
        if len(parts) >= 2:
            try:
                price = float(parts[0].replace(",", ""))
                currency = parts[1]

                cursor.execute(
                    """
                INSERT INTO flight_tickets 
                (departure_city, departure_code, destination_city, destination_code, 
                departure_date, return_date, price, currency, seats, search_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        departure_city,
                        departure_code,
                        destination_city,
                        destination_code,
                        departure_date,
                        return_date,
                        price,
                        currency,
                        seats,
                        search_date,
                    ),
                )
            except ValueError:
                print(f"Could not parse price: {price_str}")

    conn.commit()
    conn.close()


def get_saved_flights(limit=10):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT * FROM flight_tickets
    ORDER BY search_date DESC, price ASC
    LIMIT ?
    """,
        (limit,),
    )

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results
