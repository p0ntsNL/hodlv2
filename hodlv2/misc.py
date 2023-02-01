# pylint: disable=broad-except
"""
Miscellaneous functions.
None of these require data from other classes.
"""

import logging

import requests

logger = logging.getLogger(__name__)


def version_check():
    """
    Compares the bot's version to the latest repository version.
    """

    version = "2023.2"
    logger.info("")
    start_msg = f"Starting HODLv2 {version}"
    logger.info(start_msg)
    print(start_msg)

    try:
        url = "https://api.github.com/repos/p0ntsNL/hodlv2/releases/latest"
        req = requests.get(url, timeout=5)
        rtn = req.json()["tag_name"]
        if version != rtn:
            version_msg = (
                f"A new version of HODLv2 is available, plz update to version {rtn}."
            )
            logger.warning(version_msg)
    except Exception as error:
        version_msg = f"Unable to retrieve latest HODLv2 version from GitHub! {error}"
        logger.error(version_msg)


def calculate_trade_value(trade_value, last_price):
    """
    Divide trade value by last price to return the actual trade value.
    :param trade_value: the value of a trade.
    :param last_price: the latest price of the market.
    """

    return float(trade_value) / float(last_price)


def calculate_next_trade_price(open_price, perc_open, open_side):
    """
    TO DO
    """

    data = {
        "buy": float(open_price)
        - ((float(open_price) / 100) * float(perc_open)),
        "sell": float(open_price)
        + ((float(open_price) / 100) * float(perc_open)),
    }

    return data[open_side]


def calculate_close_price(open_price, perc_close, open_side):
    """
    TO DO
    """

    data = {
        "buy": float(open_price)
        + ((float(open_price) / 100) * float(perc_close)),
        "sell": float(open_price)
        - ((float(open_price) / 100) * float(perc_close)),
    }

    return data[open_side]


def set_fees(open_order, close_order):
    """
    Sets open and close fees in a nicely formatted dict.
    :param open_order: open order data.
    :param close_order: close order data.
    """

    fees = {
        "open": {
            open_order["currency"]: open_order["cost"],
        },
        "close": {
            close_order["currency"]: close_order["cost"],
        },
    }

    return fees


def set_profit(profit_in, open_order, close_order):
    """
    Calculates profit based on which profit currency is used.
    :param profit_in: currency in which profit is taken.
    :param open_order: open order data.
    :param close_order: close order data.
    """

    data = {
        "quote": (close_order["filled"] * close_order["price"]) - open_order["cost"],
        "base": open_order["filled"] - close_order["filled"],
    }

    return data[profit_in]


def find_key(data, key, key_type):
    """
    Find a specific key inside a dict.
    Return 0 if key_type is int and key is not found.
    :param data: the dict
    :param key: the key to find
    :param key_type: the key type to return to if key is not found.
    """

    if key in data:
        return data[key]

    if key_type in ("int", "float"):
        return 0
    if key_type == "str":
        return ""

    return None


def profit_in_trade_value(profit_in, open_amount, open_cost, close_price):
    """
    Set trade value based on profit_in.
    :param profit_in: the currency profit should be taken in.
    :param open_amount: the trade amount of the open order.
    :param open_cost: the cost of the open order.
    :param close_price: the price the closing order should be.
    """

    data = {
        "quote": float(open_amount),
        "base": float(open_cost) / float(close_price),
    }

    return data[profit_in]
