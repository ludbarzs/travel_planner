import re


def clean_price(price_text):
    # Clean price strings and convert to float.
    if not price_text or price_text.lower() in ["free", "unknown", "no price"]:
        return 0.0

    # Remove currency symbols except decimal points
    cleaned = re.sub(r"[^\d.,]", "", price_text)

    # Handle comma or period
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def clean_currency(price_text):
    # Remove currency symbol, depending on format
    if not price_text or price_text.lower() in ["free", "unknown", "no price"]:
        return ""

    currency_map = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "¥": "JPY",
        "₽": "RUB",
        "₹": "INR",
    }

    currency_match = re.search(r"[\$€£¥₽₹]", price_text)
    if currency_match:
        symbol = currency_match.group(0)
        return currency_map.get(symbol, symbol)

    # Find currency code
    currency_code_match = re.search(r"\b(USD|EUR|GBP|JPY|RUB|INR)\b", price_text)
    if currency_code_match:
        return currency_code_match.group(1)

    return ""


def process_flight_prices(price_list):
    processed_prices = []

    for price_str in price_list:
        price = clean_price(price_str)
        currency = clean_currency(price_str)

        if price > 0:
            processed_prices.append(
                {"price": price, "currency": currency, "original": price_str}
            )

    processed_prices.sort(key=lambda x: x["price"])

    return processed_prices
