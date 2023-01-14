#!/usr/bin/env python3
# pylint: disable=too-many-instance-attributes
"""
Main bot class
"""

import logging
import sys

from hodlv2.backend.backend import Backend
from hodlv2.exchange.exchange import Exchange
from hodlv2.notify.notify import Notify

from hodlv2.misc.misc import (  # isort:skip
    calculate_profit,  # isort:skip
    calculate_trade_value,  # isort:skip
    check_next_price,  # isort:skip
    get_base,  # isort:skip
    get_quote,  # isort:skip
    profit_in_trade_value,  # isort:skip
    find_key,  # isort:skip
)  # isort:skip

# check min. python version
if sys.version_info < (3, 8):
    sys.exit("HODLv2 requires Python version >= 3.8")

logger = logging.getLogger(__name__)


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
            logger.info(
                "Successfully retrieved open and closed orders from the exchange."
            )
            return True

        logger.error("Unable to retrieve open and closed orders from the exchange.")
        return False

    def fetch_order(self, market, order_id):
        """
        TO DO
        """

        return self.ccxt.fetch_order(market, order_id)

    def get_balance(self, market, quote):
        """
        TO DO
        """

        balances = self.ccxt.get_balances()
        if balances[0]:
            logger.info(
                "%s: %s balance: %s", market, quote, balances[1]["total"][quote]
            )
            return balances[1]["total"][quote]

        logger.error("%s balance set to 0.", quote)
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

        open_orders = "n/a"

        # If open orders is retrieved from exchange
        if self.open_orders[0]:
            open_orders = 0
            for order in self.open_orders[1]:
                if order["symbol"] == market:
                    open_orders += 1

            if open_orders == 0:
                logger.info("%s: 0 open orders found.", market)
                return True

        logger.info(
            "%s: %s open orders found.",
            market,
            open_orders,
        )
        return False

    def check_max_trades(self, market):
        """
        TO DO
        """

        if self.open_orders[0] and len(self.open_orders[1]) <= self.max_trades:
            logger.info(
                "%s: The maximum amount of trades (%s) is not reached yet (%s).",
                market,
                self.max_trades,
                len(self.open_orders[1]),
            )
            return True

        logger.warning(
            "%s: The maximum amount of trades (%s) is reached, therefore not starting a new trade.",
            market,
            self.max_trades,
        )
        return False

    def check_trade_value(self, market_data):
        """
        TO DO
        """

        trade_value = calculate_trade_value(
            self.trade_value, market_data["ticker"]["last"]
        )

        if float(trade_value) >= float(market_data["min_trade_value"]):
            logger.info(
                "%s: The trade value %s is higher than the minimum %s.",
                market_data["market"],
                trade_value,
                market_data["min_trade_value"],
            )
            return True

        logger.warning(
            "%s: The trade value %s is lower than the minimum %s, therefore not starting a new trade.",
            market_data["market"],
            trade_value,
            market_data["min_trade_value"],
        )
        return False

    def get_market_data(self, market):
        """
        TO DO
        """

        market_data = self.ccxt.get_market_data(market)
        ticker_data = self.get_ticker_data(market)

        if market_data[0] and ticker_data[0]:

            logger.info("%s: Market data retrieved successfully.", market)
            return True, {
                "market": market,
                "base": market_data[1]["base"],
                "quote": market_data[1]["quote"],
                "maker": market_data[1]["maker"],
                "taker": market_data[1]["taker"],
                "min_trade_value": market_data[1]["limits"]["amount"]["min"],
                "min_price": market_data[1]["limits"]["price"]["min"],
                "ticker": ticker_data[1],
            }

        logger.warning(
            "%s: Unable to retrieve required market data, therefore not starting a new trade.",
            market,
        )
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

    def check_balance(self, market, quote, required):
        """
        TO DO
        """

        balance = self.get_balance(market, quote)
        if float(balance) >= float(required):
            logger.info(
                "%s: Got enough %s balance (%s) to initiate trade.",
                market,
                quote,
                balance,
            )
            return True

        logger.warning(
            "%s: Not enough %s balance (%s) to initiate trade, required: %s.)",
            market,
            quote,
            balance,
            required,
        )
        return False

    def get_next_price(self, market):
        """
        TO DO
        """

        data = self.backend.find_one("markets", market)
        if data[0]:
            logger.info("%s: The next_price is %s.", market, data[1]["next_price"])
            return data[1]["next_price"]

        logger.warning("%s: Unable to retrieve next_price from backend.", market)
        return 9999999999999

    def get_profit_aggregates(self):
        """
        TO DO
        """

        aggregates = {}
        get_profit_aggregates = self.backend.aggregate(
            "trades",
            {"$match": {"status": "finished"}},
            {"$group": {"_id": "$profit_currency", "sum_val": {"$sum": "$profit"}}},
        )
        get_profit_perc_aggregates = self.backend.aggregate(
            "trades",
            {"$match": {"status": "finished"}},
            {
                "$group": {
                    "_id": "$profit_currency",
                    "sum_val": {"$sum": "$profit_perc"},
                }
            },
        )

        if get_profit_aggregates[0] & get_profit_perc_aggregates[0]:
            for aggregate in get_profit_aggregates[1]:

                if aggregate["_id"] not in aggregates:
                    aggregates[aggregate["_id"]] = {}

                aggregates[aggregate["_id"]]["profit"] = aggregate["sum_val"]

            for aggregate in get_profit_perc_aggregates[1]:

                if aggregate["_id"] not in aggregates:
                    aggregates[aggregate["_id"]] = {}

                aggregates[aggregate["_id"]]["profit_perc"] = aggregate["sum_val"]

        return aggregates

    def stringify_profit_aggregates(self):
        """
        TO DO
        """

        aggregates = []
        get_aggregates = self.get_profit_aggregates()
        for quote, data in get_aggregates.items():
            aggregates.append(
                f"{data['profit']:.8f} {quote} ({data['profit_perc']:.2f}%)"
            )

        return "\n".join(aggregates)

    def get_count(self, collection, criteria):
        """
        TO DO
        """

        count = self.backend.count_documents(collection, criteria)
        if count[0]:
            return count[1]

        return "n/a"

    def check_new_trade(self, market):
        """
        TO DO
        """

        # Retrieve market data
        market_data = self.get_market_data(market)

        # Check if balance is sufficient
        check_balance = self.check_balance(market, get_quote(market), self.trade_value)

        # Check if max trades is reached
        max_trades = self.check_max_trades(market)

        # Check if trade value is above the minimum
        trade_value = self.check_trade_value(market_data[1])

        # If market data, balance and max trades are ok
        if market_data[0] and check_balance and max_trades and trade_value:

            # If next price is reached or no open orders are found, give ok
            if self.no_open_orders(market) or check_next_price(
                self.open_side,
                self.get_next_price(market),
                market_data[1]["ticker"]["last"],
            ):
                logger.info("%s: New trade required.", market)
                return True, market_data[1]

        logger.info("%s: No new trade required based on the criteria.", market)
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
            logger.error(
                "%s: Unable to create market open order, trade stopped.", market
            )
            return

        # Retrieve open order details
        # If open order details can not be retrieved, do not proceed with the rest
        open_order_details = self.fetch_order(
            market, market_open_order[1]["info"]["txid"][0]
        )
        if not open_order_details[0]:
            logger.error(
                "%s: Unable to retrieve open order details, trade stopped.", market
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
            logger.error(
                "%s: Unable to create limit close order, trade stopped.", market
            )
            return

        # Insert data into database
        data = {
            "_id": limit_close_order[1]["info"]["txid"][0],
            "market": market,
            "open": open_order_details[1],
            "close": limit_close_order[1],
            "profit_in": self.profit_in,
            "profit_perc": self.perc_open,
            "base": get_base(market),
            "quote": get_quote(market),
            "profit_currency": get_quote(market)
            if self.profit_in == "quote"
            else get_base(market),
            "status": "active",
        }
        self.backend.insert_one("trades", data)

        close_cost = float(limit_close_order[1]["price"]) * float(close_trade_value)

        logger.info(
            "%s: Trade opened | Id: %s | Side: %s | Price: %s %s | Amount: %s %s | Cost: %s %s",
            market,
            limit_close_order[1]["info"]["txid"][0],
            self.open_side,
            open_order_details[1]["average"],
            get_quote(market),
            open_order_details[1]["filled"],
            get_base(market),
            open_order_details[1]["cost"],
            get_quote(market),
        )
        self.notify.send(
            f"""<b>Trade opened</b>
            Id: {limit_close_order[1]["info"]["txid"][0]}
            Market: {market}
            Side: {self.open_side}
            Price: {open_order_details[1]['average']} {get_quote(market)}
            Amount: {open_order_details[1]['filled']} {get_base(market)}
            Cost: {open_order_details[1]['cost']} {get_quote(market)}

            <b>Closing order</b>
            Side: {self.close_side}
            Close price: {limit_close_order[1]['price']} {get_quote(market)}
            Close amount: {close_trade_value} {get_base(market)}
            Close cost: {close_cost} {get_quote(market)}""",
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
                profit_currency = trade[1]["profit_currency"]
                status = trade[1]["status"]
                profit_perc = find_key(trade[1], "profit_perc", "int")

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
                            "status": close_order["status"],
                        },
                        False,
                    )
                    if update[0]:
                        logger.info(
                            "%s: Trade closed (%s) | Id: %s",
                            market,
                            close_order["status"],
                            close_order["id"],
                        )
                        self.notify.send(
                            f"""<b>Trade closed ({close_order['status']})</b>
                            Id: {close_order['id']}
                            Market: {market}""",
                        )

                elif status == "active" and close_order["status"] == "closed":

                    profit = calculate_profit(profit_in, open_order, close_order)

                    # Update close order and profit to backend
                    update = self.backend.update_one(
                        "trades",
                        close_order["id"],
                        {
                            "close": close_order,
                            "profit": profit,
                            "status": "finished",
                        },
                        False,
                    )
                    if update[0]:

                        logger.info(
                            "%s: Trade closed | Id: %s | Profit: %s %s (%s%)",
                            market,
                            close_order["id"],
                            profit,
                            profit_currency,
                            profit_perc,
                        )
                        self.notify.send(
                            f"""<b>Trade closed</b>
                            Id: {close_order['id']}
                            Market: {market}
                            Profit:{profit:.8f} {profit_currency} ({profit_perc:.2f}%)

                            <b>Statistics</b>
                            Active trades: {self.get_count("trades", {"status": "active"})}
                            Finished trades: {self.get_count("trades", {"status": "finished"})}

                            <b>Total Profit</b>
                            {self.stringify_profit_aggregates()}""",
                        )
