import sqlite3
from datetime import datetime, timedelta

DB_FILE = "travel_planner.db"


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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        city TEXT,
        event_id TEXT,
        title TEXT,
        datetime TEXT,
        location TEXT,
        price TEXT,
        url TEXT,
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
    processed_prices,
    seats,
):
    from datetime import datetime

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    search_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for price_data in processed_prices:
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
                price_data["price"],
                price_data["currency"],
                seats,
                search_date,
            ),
        )

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


def save_events(city, events):
    if not events:
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    search_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for event in events:
        cursor.execute(
            """
            INSERT INTO events 
            (city, event_id, title, datetime, location, price, url, search_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                city,
                event.get("event_id"),
                event.get("title"),
                event.get("datetime"),
                event.get("location"),
                event.get("price"),
                event.get("url"),
                search_date,
            ),
        )

    conn.commit()
    conn.close()


def get_saved_events(city=None, limit=10):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if city:
        cursor.execute(
            """
            SELECT * FROM events
            WHERE city = ?
            ORDER BY search_date DESC
            LIMIT ?
            """,
            (city, limit),
        )
    else:
        cursor.execute(
            """
            SELECT * FROM events
            ORDER BY search_date DESC
            LIMIT ?
            """,
            (limit,),
        )

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results


def get_flights_by_destination(destination_city, limit=10):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM flight_tickets
        WHERE destination_city = ?
        ORDER BY search_date DESC, price ASC
        LIMIT ?
        """,
        (destination_city, limit),
    )

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results


def delete_old_data(days=30):
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM flight_tickets
        WHERE search_date < ?
        """,
        (cutoff_date,),
    )

    cursor.execute(
        """
        DELETE FROM events
        WHERE search_date < ?
        """,
        (cutoff_date,),
    )

    conn.commit()
    deleted_rows = conn.total_changes
    conn.close()

    return deleted_rows

