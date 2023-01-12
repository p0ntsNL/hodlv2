#!/usr/bin/env python3
# pylint: disable=too-many-instance-attributes
"""
Main bot class
"""

import sys

from hodlv2.backend.backend import Backend
from hodlv2.exchange.exchange import Exchange
from hodlv2.notify.notify import Notify

from hodlv2.misc.misc import (  # isort:skip
    calculate_profit,  # isort:skip
    calculate_trade_value,  # isort:skip
    check_next_price,  # isort:skip
    get_base,  # isort:skip
    get_profit_currency,  # isort:skip
    get_quote,  # isort:skip
    profit_in_trade_value,  # isort:skip
)  # isort:skip

# check min. python version
if sys.version_info < (3, 8):
    sys.exit("HODLv2 requires Python version >= 3.8")


class HODLv2Bot:
    """
    TO DO
    """

    def __init__(self, config):
        """
        TO DO
        """

        self.config = config
        self.ccxt = Exchange(self.config)
        self.notify = Notify(self.config)
        self.backend = Backend(self.config)

        self.open_orders = self.ccxt.get_open_orders()
        self.closed_orders = self.ccxt.get_closed_orders()
        self.balances = self.ccxt.get_balances()

        self.trade_value = self.config.TRADE_VALUE
        self.side = self.config.SIDE
        self.max_trades = self.config.MAX_TRADES
        self.perc_open = self.config.PERC_OPEN
        self.perc_close = self.config.PERC_CLOSE
        self.profit_in = self.config.PROFIT_IN
        self.open_side = self.side
        self.close_side = "sell" if self.side == "buy" else "buy"

    def open_closed_ok(self):
        """
        TO DO
        """

        if self.open_orders[0] and self.closed_orders[0]:
            return True

        return False

    def fetch_order(self, market, order_id):
        """
        TO DO
        """

        return self.ccxt.fetch_order(market, order_id)

    def get_balance(self, quote):
        """
        TO DO
        """

        balance = self.balances
        if balance[0]:
            return balance[1]["total"][quote]

        return 0

    def get_ticker_data(self, market):
        """
        TO DO
        """

        return self.ccxt.get_ticker_data(market)

    def create_market_order(self, market, last):
        """
        TO DO
        """

        trade_value = calculate_trade_value(self.trade_value, last)
        return self.ccxt.create_market_order(market, self.open_side, trade_value)

    def create_limit_order(self, market, trade_value, price):
        """
        TO DO
        """

        return self.ccxt.create_limit_order(market, self.close_side, trade_value, price)

    def no_open_orders(self, market):
        """
        TO DO
        """

        # If open orders is retrieved from exchange
        if self.open_orders[0]:
            open_orders = 0
            for order in self.open_orders[1]:
                if order["symbol"] == market:
                    open_orders += 1

            if open_orders == 0:
                return True

        return False

    def check_max_trades(self):
        """
        TO DO
        """

        if self.open_orders[0] and len(self.open_orders[1]) <= self.max_trades:
            return True

        return False

    def get_market_data(self, market):
        """
        TO DO
        """

        ticker_data = self.get_ticker_data(market)

        if ticker_data[0]:

            return True, {
                "base": get_base(market),
                "quote": get_quote(market),
                "ticker": ticker_data[1],
            }

        return False, {}

    def calculate_close_price(self, open_price):
        """
        TO DO
        """

        data = {
            "buy": float(open_price)
            + ((float(open_price) / 100) * float(self.perc_close)),
            "sell": float(open_price)
            - ((float(open_price) / 100) * float(self.perc_close)),
        }

        return data[self.open_side]

    def calculate_next_open_price(self, open_price):
        """
        TO DO
        """

        data = {
            "buy": float(open_price)
            - ((float(open_price) / 100) * float(self.perc_open)),
            "sell": float(open_price)
            + ((float(open_price) / 100) * float(self.perc_open)),
        }

        return data[self.open_side]

    def check_balance(self, quote, required):
        """
        TO DO
        """

        balance = self.get_balance(quote)
        if float(balance) >= float(required):
            return True

        return False

    def get_next_price(self, market):
        """
        TO DO
        """

        data = self.backend.find_one("markets", market)
        if data[0]:
            return data[1]["next_price"]

        return 9999999999999

    def check_new_trade(self, market):
        """
        TO DO
        """

        # Retrieve market data
        market_data = self.get_market_data(market)

        # Check if balance is sufficient
        check_balance = self.check_balance(get_quote(market), self.trade_value)

        # Check if max trades is reached
        max_trades = self.check_max_trades()

        # If market data, balance and max trades are ok
        if market_data[0] and check_balance and max_trades:

            # If next price is reached or no open orders are found, give ok
            if check_next_price(
                self.open_side,
                self.get_next_price(market),
                market_data[1]["ticker"]["last"],
            ) or self.no_open_orders(market):
                return True, market_data[1]

        return False, {}

    def new_trade(self, market, market_data):
        """
        TO DO
        """

        # Create market open order
        # If market order can not be created, do not proceed with the rest
        market_open_order = self.create_market_order(
            market, market_data["ticker"]["last"]
        )
        if not market_open_order[0]:
            self.notify.send(
                f"{market}: Unable to create market open order, trade stopped.",
                "ERROR",
            )
            return

        # Retrieve open order details
        # If open order details can not be retrieved, do not proceed with the rest
        open_order_details = self.fetch_order(
            market, market_open_order[1]["info"]["txid"][0]
        )
        if not open_order_details[0]:
            self.notify.send(
                f"{market}: Unable to retrieve open order details, trade stopped.",
                "ERROR",
            )
            return

        # Calculate close price
        close_price = self.calculate_close_price(
            open_order_details[1]["average"],
        )

        # Calculate next price
        next_price = self.calculate_next_open_price(
            open_order_details[1]["average"],
        )
        self.backend.update_one("markets", market, {"next_price": next_price}, True)

        # Calculate trade value
        close_trade_value = profit_in_trade_value(
            self.profit_in,
            open_order_details[1]["filled"],
            open_order_details[1]["cost"],
            close_price,
        )

        # Create limit close order
        limit_close_order = self.create_limit_order(
            market,
            close_trade_value,
            close_price,
        )
        if not limit_close_order[0]:
            self.notify.send(
                f"{market}: Unable to create limit close order, trade stopped.",
                "ERROR",
            )
            return

        # Insert data into database
        data = {
            "_id": limit_close_order[1]["info"]["txid"][0],
            "market": market,
            "open": open_order_details[1],
            "close": limit_close_order[1],
            "profit_in": self.profit_in,
            "status": "active",
        }
        self.backend.insert_one("trades", data)

        close_cost = float(limit_close_order[1]["price"]) * float(close_trade_value)

        self.notify.send(
            f"""<b>Trade opened</b>
            Id: {limit_close_order[1]["info"]["txid"][0]}
            Market: {market}
            Side: {self.open_side}
            Price: {open_order_details[1]['average']} quote
            Amount: {open_order_details[1]['filled']} base
            Cost: {open_order_details[1]['cost']} quote

            <b>Closing order</b>
            Side: {self.close_side}
            Close price: {limit_close_order[1]['price']} quote
            Close amount: {close_trade_value} base
            Close cost: {close_cost} quote""",
            "INFO",
        )

    def check_closed_orders(self):
        """
        TO DO
        """

        closed_orders = self.closed_orders
        for close_order in closed_orders[1]:

            trade = self.backend.find_one_exists(
                "trades", close_order["id"], "profit", False
            )
            if trade[0]:

                market = trade[1]["market"]
                open_order = trade[1]["open"]
                profit_in = trade[1]["profit_in"]
                status = trade[1]["status"]

                if status == "active" and close_order["status"] in [
                    "canceled",
                    "expired",
                    "rejected",
                ]:

                    # Update close order and profit to backend
                    update = self.backend.update_one(
                        "trades",
                        close_order["id"],
                        {
                            "close": close_order,
                            "profit": 0,
                            "profit_currency": "n/a",
                            "status": close_order["status"],
                        },
                        False,
                    )
                    if update[0]:
                        self.notify.send(
                            f"""<b>Trade closed ({close_order['status']})</b>
                            Id: {close_order['id']}
                            Market: {market}""",
                            "WARNING",
                        )

                elif status == "active" and close_order["status"] == "closed":

                    profit = calculate_profit(profit_in, open_order, close_order)
                    profit_currency = get_profit_currency(
                        profit_in, get_quote(market), get_base(market)
                    )

                    # Update close order and profit to backend
                    update = self.backend.update_one(
                        "trades",
                        close_order["id"],
                        {
                            "close": close_order,
                            "profit": profit,
                            "profit_currency": profit_currency,
                            "status": "finished",
                        },
                        False,
                    )
                    if update[0]:

                        self.notify.send(
                            f"""<b>Trade closed</b>
                            Id: {close_order['id']}
                            Market: {market}
                            Profit:{profit:.8f} {profit_currency}""",
                            "INFO",
                        )
