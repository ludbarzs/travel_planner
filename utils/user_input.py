import datetime


def validate_date_format(date_str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        if date_obj < today:
            return False, "Date has passed"
        return True, date_obj
    except ValueError:
        return False, "Use YYYY-MM-DD format"


def get_user_input():
    print("Enter travel details:")

    departure_city = input("Departure city: ").strip()
    destination_city = input("Destination city: ").strip()

    while True:
        departure_date = input("Departure date (YYYY-MM-DD): ").strip()
        valid, msg_or_date = validate_date_format(departure_date)
        if valid:
            break
        print(f"Error: {msg_or_date}")

    while True:
        return_date = input(
            "Return date (YYYY-MM-DD, leave empty for one-way): "
        ).strip()
        if not return_date:
            return_date = None
            break
        valid, msg_or_date = validate_date_format(return_date)
        if valid:
            if (
                msg_or_date
                < datetime.datetime.strptime(departure_date, "%Y-%m-%d").date()
            ):
                print("Error: Return date must be after departure date")
                continue
            break
        print(f"Error: {msg_or_date}")

    while True:
        try:
            seats = input("Number of passengers (1-9): ").strip()
            seats = int(seats)
            if 1 <= seats <= 9:
                break
            print("Error: Number of passengers must be between 1 and 9")
        except ValueError:
            print("Error: Please enter a valid number")

    return {
        "departure_city": departure_city,
        "destination_city": destination_city,
        "departure_date": departure_date,
        "return_date": return_date,
        "seats": seats,
    }


if __name__ == "__main__":
    print(get_user_input())

