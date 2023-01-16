#!/usr/bin/env python3
# pylint: disable=too-many-instance-attributes
"""
Main bot class
"""

import logging
import time

from hodlv2.backend.backend import Backend
from hodlv2.exchange.exchange import Exchange
from hodlv2.notify.notify import Notify

from hodlv2.misc.misc import (  # isort:skip
    calculate_profit,  # isort:skip
    calculate_fees,  # isort:skip
    calculate_trade_value,  # isort:skip
    profit_in_trade_value,  # isort:skip
    find_key,  # isort:skip
)  # isort:skip

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

        self.markets_data = self.config.MARKETS
        self.markets = self.markets_data.keys()

    def bot_settings(self, market):
        """
        TO DO
        """

        self.base = market.split("/")[0]
        self.quote = market.split("/")[1]
        self.trade_value = self.markets_data[market]["TradeValue"]
        self.side = self.markets_data[market]["Side"]
        self.max_trades = self.markets_data[market]["MaxTrades"]
        self.perc_open = self.markets_data[market]["PercOpen"]
        self.perc_close = self.markets_data[market]["PercClose"]
        self.next_trade_price_reset = self.markets_data[market]["ResetNextTradePrice"]
        self.open_side = self.side
        self.close_side = "sell" if self.side == "buy" else "buy"
        self.profit_in = (
            "base"
            if self.markets_data[market]["TakeProfitIn"] == self.base
            else "quote"
        )

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
                logger.info("%s: 0 open orders found, lets start a new trade.", market)
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
            "%s: The maximum amount of trades (%s) is reached, not starting a new trade.",
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
            "%s: The trade value %s is lower than the minimum %s, not starting a new trade.",
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
            "%s: Unable to retrieve required market data, not starting a new trade.",
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

    def calculate_next_trade_price(self, open_price):
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

    def get_next_trade_price_data(self, market):
        """
        TO DO
        """

        data = self.backend.find_one("markets", market)
        if data[0]:
            if (
                "next_trade_price" in data[1]
                and "next_trade_price_updated_at" in data[1]
            ):
                return [
                    data[1]["next_trade_price"],
                    data[1]["next_trade_price_updated_at"],
                ]

        logger.critical(
            "%s: Unable to retrieve next_trade_price data from backend.", market
        )
        return [0, 0]

    def check_next_trade_price(self, market, next_trade_price, last_price):
        """
        TO DO
        """

        if self.open_side == "buy":
            if float(last_price) <= float(next_trade_price):
                logger.info(
                    "%s: last_price (%s) <= next_trade_price (%s), lets start a new trade.",
                    market,
                    last_price,
                    next_trade_price,
                )
                return True
        else:
            if float(last_price) >= float(next_trade_price):
                logger.info(
                    "%s: last_price (%s) >= next_trade_price (%s), lets start a new trade.",
                    market,
                    last_price,
                    next_trade_price,
                )
                return True

        logger.info(
            "%s: last_price: (%s) | next_trade_price: (%s)",
            market,
            last_price,
            next_trade_price,
        )
        return False

    def get_total_fees(self):
        """
        TO DO
        """

        fees = {}
        get_fees = self.backend.find("trades", {"fees":{"$exists":1 }}, { "fees":1})

        if get_fees[0]:

            for fee in get_fees[1]:
                for order_type,fee_data in fee['fees'].items():
                    for currency,value in fee_data.items():

                        if currency not in fees:
                            fees[currency] = 0

                        if not isinstance(value, type(None)):
                            fees[currency] += float(value)

        return fees

    def stringify_total_fees(self):
        """
        TO DO
        """

        fees = {}
        get_total_fees = self.get_total_fees()
        for quote, fee in get_total_fees:
            fees.append(
                f"{fee} {quote}"
            )
            
        return "\n".join(fees)

    def get_profit_aggregates(self):
        """
        TO DO
        """

        aggregates = {}
        get_profit_aggregates = self.backend.aggregate(
            "trades",
            {"$sort": {"profit_currency": 1}},
            {"$match": {"status": "finished"}},
            {"$group": {"_id": "$profit_currency", "sum_val": {"$sum": "$profit"}}},
        )
        get_profit_perc_aggregates = self.backend.aggregate(
            "trades",
            {"$sort": {"profit_currency": 1}},
            {"$match": {"status": "finished"}},
            {
                "$group": {
                    "_id": "$profit_currency",
                    "sum_val": {"$sum": "$profit_perc"},
                }
            },
        )

        if get_profit_aggregates[0] and get_profit_perc_aggregates[0]:
            for aggregate in get_profit_aggregates[1]:

                if aggregate["_id"] not in aggregates:
                    aggregates[aggregate["_id"]] = {}

                aggregates[aggregate["_id"]]["profit"] = aggregate["sum_val"]

            for aggregate in get_profit_perc_aggregates[1]:

                if aggregate["_id"] not in aggregates:
                    aggregates[aggregate["_id"]] = {}

                aggregates[aggregate["_id"]]["profit_perc"] = aggregate["sum_val"]

        else:
            logger.critical("Unable to retrieve aggregates from backend.")

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

        logger.critical("Unable to retrieve document count from backend.")
        return "n/a"

    def check_next_trade_price_reset(self, market):
        """
        TO DO
        """

        next_trade_price_updated_at = self.get_next_trade_price_data(market)[1]

        if next_trade_price_updated_at != 0:

            reset_at = int(next_trade_price_updated_at) + (
                int(self.next_trade_price_reset) * 86400
            )

            if int(time.time()) > int(reset_at):

                update_next_trade_price = self.backend.update_one(
                    "markets", market, {"next_trade_price": 999999999999}, True
                )

                if update_next_trade_price[0]:
                    logger.info("%s: Next trade price have been reset.", market)
                else:
                    logger.error("%s: Unable to reset next trade price.", market)
            else:
                logger.info(
                    "%s: Next trade price reset is not required, next reset at %s.",
                    market,
                    time.strftime("%d-%m-%Y %H:%M", time.localtime(reset_at)),
                )

    def check_new_trade(self, market):
        """
        TO DO
        """

        # Retrieve market data
        market_data = self.get_market_data(market)

        # Check if balance is sufficient
        check_balance = self.check_balance(market, self.quote, self.trade_value)

        # Check if max trades is reached
        max_trades = self.check_max_trades(market)

        # Check if trade value is above the minimum
        trade_value = self.check_trade_value(market_data[1])

        # If market data, balance and max trades are ok
        if market_data[0] and check_balance and max_trades and trade_value:

            # Check if next trade price should be reset
            self.check_next_trade_price_reset(market)

            # If next trade price is reached or no open orders are found, give ok
            if self.no_open_orders(market) or self.check_next_trade_price(
                market,
                self.get_next_trade_price_data(market)[0],
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

        print(market_open_order)

        # Retrieve open order details up to 5 times, otherwise do not proceed
        for i in range(5):

            open_order_details = self.fetch_order(
                market, market_open_order[1]["info"]["txid"][0]
            )
            if open_order_details[0]:
                break

            if i == 4:
                logger.error(
                    "%s: Unable to retrieve open order details, trade stopped.", market
                )
                return

            logger.warning(
                "%s: Unable to retrieve open order details, trying again...", market
            )

            time.sleep(15)

        # Calculate close price
        close_price = self.calculate_close_price(
            open_order_details[1]["average"],
        )

        # Calculate next trade price
        next_trade_price = self.calculate_next_trade_price(
            open_order_details[1]["average"],
        )
        update_next_trade_price = self.backend.update_one(
            "markets",
            market,
            {
                "next_trade_price": next_trade_price,
                "next_trade_price_updated_at": int(time.time()),
            },
            True,
        )
        if not update_next_trade_price[0]:
            logger.critical(
                "%s: Unable to update next trade price details to backend.", market
            )

        # Calculate trade value
        close_trade_value = profit_in_trade_value(
            self.profit_in,
            open_order_details[1]["filled"],
            open_order_details[1]["cost"],
            close_price,
        )

        # Create limit close order up to 5 times, otherwise do not proceed
        for i in range(5):

            limit_close_order = self.create_limit_order(
                market,
                close_trade_value,
                close_price,
            )
            if limit_close_order[0]:
                break

            if i == 4:
                logger.error(
                    "%s: Unable to create limit close order, trade stopped.", market
                )
                return

            logger.warning(
                "%s: Unable to create limit close order, trying again...", market
            )

        print(limit_close_order)

        # Insert data into database
        data = {
            "_id": limit_close_order[1]["info"]["txid"][0],
            "market": market,
            "open": open_order_details[1],
            "close": limit_close_order[1],
            "profit_in": self.profit_in,
            "profit_perc": self.perc_open,
            "base": self.base,
            "quote": self.quote,
            "profit_currency": self.quote if self.profit_in == "quote" else self.base,
            "status": "active",
        }
        insert = self.backend.insert_one("trades", data)
        if not insert[0]:
            logger.critical("%s: Unable to insert trade details to backend.", market)

        close_value = float(limit_close_order[1]["price"]) * float(close_trade_value)

        logger.info(
            "%s: Trade opened | Id: %s | Side: %s | Price: %s %s | Amount: %s %s | Cost: %s %s | Fee: %s %s",
            market,
            limit_close_order[1]["info"]["txid"][0],
            self.open_side,
            open_order_details[1]["average"],
            self.quote,
            open_order_details[1]["filled"],
            self.base,
            open_order_details[1]["cost"],
            self.quote,
            open_order_details[1]["fee"]["cost"],
            open_order_details[1]["fee"]["currency"],
        )
        self.notify.send(
            f"""<b>Trade opened</b>
            Id: {limit_close_order[1]["info"]["txid"][0]}
            Market: {market}
            Side: {self.open_side}
            Price: {open_order_details[1]['average']} {self.quote}
            Amount: {open_order_details[1]['filled']} {self.base}
            Cost: {open_order_details[1]['cost']} {self.quote}
            Fee: {open_order_details[1]["fee"]["cost"]} {open_order_details[1]["fee"]["currency"]}

            <b>Closing order</b>
            Side: {self.close_side}
            Price: {limit_close_order[1]['price']} {self.quote}
            Amount: {close_trade_value} {self.base}
            Value: {close_value} {self.quote}""",
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
                    else:
                        logger.critical(
                            "%s: Unable to update closed order details to backend.",
                            market,
                        )

                elif status == "active" and close_order["status"] == "closed":

                    profit = calculate_profit(profit_in, open_order, close_order)
                    fees = calculate_fees(open_order["fee"], close_order["fee"], profit_currency)

                    # Update close order and profit to backend
                    update = self.backend.update_one(
                        "trades",
                        close_order["id"],
                        {
                            "close": close_order,
                            "profit": profit,
                            "fees": fees,
                            "status": "finished",
                        },
                        False,
                    )
                    if update[0]:

                        logger.info(
                            "%s: Trade closed | Id: %s | Profit: %s %s (%s%%) | Open fee: %s %s | Close fee: %s %s",
                            market,
                            close_order["id"],
                            profit,
                            profit_currency,
                            profit_perc,
                            open_order["fee"]["cost"],
                            open_order["fee"]["currency"],
                            close_order["fee"]["cost"],
                            close_order["fee"]["currency"],
                        )
                        self.notify.send(
                            f"""<b>Trade closed</b>
                            Id: {close_order['id']}
                            Market: {market}
                            Profit (Ex. fees): {profit:.8f} {profit_currency} ({profit_perc:.2f}%)
                            Open fee: {open_order["fee"]["cost"]} {open_order["fee"]["currency"]}
                            Close fee: {close_order["fee"]["cost"]} {close_order["fee"]["currency"]}

                            <b>Statistics</b>
                            Active trades: {self.get_count("trades", {"status": "active"})}
                            Finished trades: {self.get_count("trades", {"status": "finished"})}

                            <b>Total profit (Ex. fees)</b>
                            {self.stringify_profit_aggregates()}

                            <b>Total fees spend</b>
                            {self.stringify_total_fees()}""",
                        )
                    else:
                        logger.critical(
                            "%s: Unable to update trade details to backend.", market
                        )
            else:
                pass
                # logger.critical("Unable to retrieve closed order details from backend.")
