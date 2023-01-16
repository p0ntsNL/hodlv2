# pylint: disable=broad-except
"""
TO DO
"""


def calculate_trade_value(trade_value, last_price):
    """
    TO DO
    """

    return float(trade_value) / float(last_price)


def calculate_fees(open_order, close_order, profit_currency):
    """
    TO DO
    """

    try:
        if (
            open_order["fee"]["currency"] == profit_currency
            and close_order["fee"]["currency"] == profit_currency
        ):
            return [
                (float(open_order["fee"]["cost"]) + float(close_order["fee"]["cost"])),
                profit_currency,
            ]
    except Exception as error:
        return [
            0,
            f"""Unverified exchange, verify required, please report!
                    {error}""",
        ]

    return [0, "Unverified exchange, verify required, please report!"]


def calculate_profit(profit_in, open_order, close_order):
    """
    TO DO
    """

    data = {
        "quote": (close_order["filled"] * close_order["price"]) - open_order["cost"],
        "base": open_order["filled"] - close_order["filled"],
    }

    return data[profit_in]


def find_key(data, key, key_type):
    """
    TO DO
    """

    if key in data:
        return data[key]

    if key_type == "int":
        return 0

    return None


def profit_in_trade_value(profit_in, open_amount, open_cost, close_price):
    """
    TO DO
    """

    data = {
        "quote": float(open_amount),
        "base": float(open_cost) / float(close_price),
    }

    return data[profit_in]
