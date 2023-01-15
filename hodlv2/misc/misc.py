"""
TO DO
"""


def calculate_trade_value(trade_value, last_price):
    """
    TO DO
    """

    return float(trade_value) / float(last_price)


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
