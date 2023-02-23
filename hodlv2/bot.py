#!/usr/bin/env python3
# pylint: disable=broad-except
"""
Main bot class
"""

import logging
import time

from hodlv2.backend.backend import Backend
from hodlv2.exchange.exchange import Exchange
from hodlv2.notify.notify import Notify

from hodlv2.misc import (  # isort:skip
    set_profit,  # isort:skip
    set_fees,  # isort:skip
    find_key,  # isort:skip
    calculate_next_trade_price,  # isort:skip
    calculate_close_price,  # isort:skip
    calculate_trade_value,  # isort:skip
    profit_in_trade_value,  # isort:skip
)  # isort:skip

logger = logging.getLogger(__name__)


class Bot:
    """
    TO DO
    """

    def __init__(self, config, init=False):
        """
        TO DO
        """

        # Variables
        self.settings = {}

        # Objects
        self.exchange = Exchange(config)
        self.notify = Notify(config)
        self.backend = Backend()

        # Variables
        self.markets_data = config["BotSettings"]

        self.orders = {
            "open_on_backend": self.backend.find("trades", {"status": "active"}, {"status":1, "market":1})[1],
            "open_on_exchange": self.exchange.get_open_orders(),
            "closed": self.exchange.get_closed_orders(),
        }

        if init:
            self.exchange.get_balances()
        self.exchange_health = self.exchange.health

    def bot_init(self, market):
        """
        TO DO
        """

        self.settings = {}
        self.settings["market"] = market
        self.settings["base"] = market.split("/")[0]
        self.settings["quote"] = market.split("/")[1]
        self.settings["trade_value"] = float(self.markets_data[market]["TradeValue"])
        self.settings["side"] = self.markets_data[market]["Side"]
        self.settings["max_trades"] = int(self.markets_data[market]["MaxTrades"])
        self.settings["perc_open"] = float(self.markets_data[market]["PercOpen"])
        self.settings["perc_close"] = float(self.markets_data[market]["PercClose"])
        self.settings["next_trade_price_reset"] = int(
            self.markets_data[market]["ResetNextTradePrice"]
        )
        self.settings["open_side"] = self.settings["side"]
        self.settings["close_side"] = (
            "sell" if self.settings["side"] == "buy" else "buy"
        )
        self.settings["profit_in"] = (
            "base"
            if self.markets_data[market]["TakeProfitIn"] == self.settings["base"]
            else "quote"
        )
        self.settings["open_orders"] = self.backend.find("trades", {"status": "active", "market":market}, {"status":1, "market":1})

    def get_balance(self, market, quote):
        """
        TO DO
        """

        balances = self.exchange.get_balances()
        if balances[0]:
            logger.info(
                "%s | Available %s balance: %s",
                market,
                quote,
                balances[1]["total"][quote],
            )
            return balances[1]["total"][quote]

        logger.error(
            "%s | Balance data unavailable, available %s balance set to 0.",
            market,
            quote,
        )
        return 0

    def no_open_orders(self, market):
        """
        TO DO
        """

        open_orders = "n/a"

        # If open orders is retrieved from exchange
        if self.settings["open_orders"][0]:

            open_orders = len(list(self.settings["open_orders"][1]))

            if open_orders == 0:
                logger.info("%s | OK: 0 open orders found.", market)
                return True

        if open_orders == "n/a":
            logger.info(
                "%s | NOT OK: %s open orders found.",
                market,
                open_orders,
            )
        else:
            logger.info(
                "%s | OK: %s open orders found.",
                market,
                open_orders,
            )
        return False

    def check_max_trades(self, market):
        """
        TO DO
        """

        if self.settings["open_orders"][0]:

            open_trades = len(list(self.settings["open_orders"][1]))

            if int(open_trades) < int(self.settings["max_trades"]):
                logger.info(
                    "%s | OK: The maximum amount of trades (%s) is not reached yet (%s).",
                    market,
                    self.settings["max_trades"],
                    open_trades,
                )
                return True

        logger.info(
            "%s | NOT OK: The max amount of trades (%s) is reached.",
            market,
            self.settings["max_trades"],
        )
        return False

    def check_trade_value(self, market_data):
        """
        TO DO
        """

        trade_value = calculate_trade_value(
            self.settings["trade_value"], market_data["ticker"]["last"]
        )

        # If min_trade_value exists
        if not isinstance(market_data["min_trade_value"], type(None)):

            # If trade_value is higher than min_trade_value
            if float(trade_value) >= float(market_data["min_trade_value"]):
                logger.info(
                    "%s: The trade value %s is higher than the minimum %s.",
                    market_data["market"],
                    trade_value,
                    market_data["min_trade_value"],
                )
                return True

            # If trade_value is lower than min_trade_value.
            logger.warning(
                "%s: The trade value %s is lower than the minimum %s, not starting a new trade.",
                market_data["market"],
                trade_value,
                market_data["min_trade_value"],
            )
            return False

        # If min_trade_value does not exist, force ok.
        logger.info(
            "%s: The trade value %s is higher than the minimum %s.",
            market_data["market"],
            trade_value,
            market_data["min_trade_value"],
        )
        return True

    def get_market_data(self, market):
        """
        TO DO
        """

        market_data = self.exchange.get_market_data(market)
        ticker_data = self.exchange.get_ticker_data(market)

        if market_data[0] and ticker_data[0]:

            logger.info("%s | OK: Market data retrieved successfully.", market)
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

        logger.info(
            "%s | NOT OK: Unable to retrieve required market data, trying again...",
            market,
        )
        return False, {}

    def check_balance(self, market, quote, required):
        """
        TO DO
        """

        balance = self.get_balance(market, quote)
        if float(balance) >= float(required):
            logger.info(
                "%s | OK: Got enough %s balance (%s).",
                market,
                quote,
                balance,
            )
            return True

        logger.info(
            "%s | NOT OK: Not enough %s balance (%s), required: %s.",
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

        # If next_trade_price can be retrieved from the backend and exists.
        if data[0]:
            if (
                "next_trade_price" in data[1]
                and "next_trade_price_updated_at" in data[1]
            ):
                return [
                    data[1]["next_trade_price"],
                    data[1]["next_trade_price_updated_at"],
                ]
        # If next_trade_price can retrieved from backend but does not exist.
        else:
            if isinstance(data[0], type(None)):
                logger.info(
                    "%s | next_trade_price not found yet, forcing next price to 999999999999999.",
                    market,
                )
                return [999999999999999, 999999999999999]

        # If backend is not accessible.
        logger.warning(
            "%s | Unable to retrieve next_trade_price data from backend.", market
        )
        return [0, 0]

    def check_next_trade_price(self, market, next_trade_price, last_price):
        """
        TO DO
        """

        if self.settings["open_side"] == "buy":
            if float(last_price) <= float(next_trade_price):
                logger.info(
                    "%s | OK: last_price (%s) is lower than next_trade_price (%s).",
                    market,
                    last_price,
                    next_trade_price,
                )
                return True
        else:
            if float(last_price) >= float(next_trade_price):
                logger.info(
                    "%s | OK: last_price (%s) is higher than next_trade_price (%s).",
                    market,
                    last_price,
                    next_trade_price,
                )
                return True

        logger.info(
            "%s | NOT OK: next_trade_price (%s) is not reached yet, the current price is %s.",
            market,
            next_trade_price,
            last_price,
        )
        return False

    def get_total_fees(self):
        """
        TO DO
        """

        fees = {}
        get_fees = self.backend.find("trades", {"fees": {"$exists": 1}}, {"fees": 1})

        if get_fees[0]:

            for fee in get_fees[1]:
                for order_type, fee_data in fee["fees"].items():
                    dummy = order_type
                    for currency, value in fee_data.items():

                        if currency not in fees:
                            fees[currency] = 0

                        if not isinstance(value, type(None)):
                            fees[currency] += float(value)

        return fees

    def stringify_total_fees(self):
        """
        TO DO
        """

        fees = []
        get_total_fees = self.get_total_fees()
        for quote, fee in get_total_fees.items():
            fees.append(f"{fee} {quote}")

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
            logger.error("Unable to retrieve aggregates from backend.")

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

        logger.error("Unable to retrieve document count from backend.")
        return "n/a"

    def check_next_trade_price_reset(self, market):
        """
        TO DO
        """

        next_trade_price_updated_at = self.get_next_trade_price_data(market)[1]

        if next_trade_price_updated_at != 0:

            reset_at = int(next_trade_price_updated_at) + (
                int(self.settings["next_trade_price_reset"]) * 86400
            )

            if int(time.time()) > int(reset_at):

                update_next_trade_price = self.backend.update_one(
                    "markets", market, {"next_trade_price": 999999999999}, True
                )
                if update_next_trade_price[0]:
                    logger.info("%s | OK: Next trade price have been reset.", market)
            else:
                logger.info(
                    "%s | OK: Next trade price reset is not required, next reset at %s.",
                    market,
                    time.strftime("%d-%m-%Y %H:%M", time.localtime(reset_at)),
                )

    def check_new_trade(self, market):
        """
        TO DO
        """

        # Retrieve market data
        market_data = self.get_market_data(market)
        if market_data[0]:

            # Last price to mongoDB for future reference
            self.backend.update_one(
                "markets", market, {"last": market_data[1]["ticker"]["last"]}, True
            )

            # Check if next trade price should be reset
            self.check_next_trade_price_reset(market)

            # If next trade price is reached or no open orders are found, give ok
            if self.no_open_orders(market) or self.check_next_trade_price(
                market,
                self.get_next_trade_price_data(market)[0],
                market_data[1]["ticker"]["last"],
            ):

                # Check if balance is sufficient
                check_balance = self.check_balance(
                    market, self.settings["quote"], self.settings["trade_value"]
                )

                # Check if max trades is reached
                max_trades = self.check_max_trades(market)

                # Check if trade value is above the minimum
                trade_value = self.check_trade_value(market_data[1])

                # If market data, balance and max trades are ok
                if check_balance and max_trades and trade_value:
                    logger.info(
                        "%s | FINAL: New trade required based on the criteria, lets go!",
                        market,
                    )
                    return True, market_data[1]

        logger.info("%s | FINAL: No new trade required based on the criteria.", market)
        return False, {}

    def new_trade(self, market, market_data):
        """
        TO DO
        """

        # Create market open order
        # If market order can not be created, do not proceed with the rest
        market_open_order = self.exchange.create_market_order(
            market,
            self.settings["open_side"],
            calculate_trade_value(
                self.settings["trade_value"],
                market_data["ticker"]["last"],
            ),
        )
        if not market_open_order[0]:
            logger.error(
                "%s | Unable to create market open order, trade stopped.", market
            )
            return

        # Retrieve open order details up to 5 times, otherwise do not proceed
        for i in range(5):

            open_order_details = self.exchange.fetch_order(
                market, market_open_order[1]["id"]
            )
            if open_order_details[0]:
                logger.info("%s | Open order details retrieved.", market)
                break

            if i == 4:
                logger.error(
                    "%s | Unable to retrieve open order details, trade stopped.", market
                )
                return

            logger.warning(
                "%s | Unable to retrieve open order details, trying again...", market
            )

            time.sleep(15)

        # Calculate close price
        close_price = calculate_close_price(
            open_order_details[1]["average"],
            self.settings["perc_open"],
            self.settings["open_side"],
        )

        # Calculate next trade price
        next_trade_price = calculate_next_trade_price(
            open_order_details[1]["average"],
            self.settings["perc_open"],
            self.settings["open_side"],
        )

        # Calculate trade value
        close_trade_value = profit_in_trade_value(
            self.settings["profit_in"],
            open_order_details[1]["filled"],
            open_order_details[1]["cost"],
            close_price,
        )

        # Create limit close order up to 5 times, otherwise do not proceed
        for i in range(5):

            limit_close_order = self.exchange.create_limit_order(
                market,
                self.settings["close_side"],
                close_trade_value,
                close_price,
            )
            if limit_close_order[0]:
                break

            if i == 4:
                logger.error(
                    "%s | Unable to create limit close order, trade stopped.", market
                )
                return

            logger.warning(
                "%s | Unable to create limit close order, trying again...", market
            )

            time.sleep(15)

        # Insert data into database
        data = {
            "_id": limit_close_order[1]["id"],
            "market": market,
            "open": open_order_details[1],
            "close": limit_close_order[1],
            "profit_in": self.settings["profit_in"],
            "profit_perc": self.settings["perc_open"],
            "base": self.settings["base"],
            "quote": self.settings["quote"],
            "profit_currency": self.settings["quote"]
            if self.settings["profit_in"] == "quote"
            else self.settings["base"],
            "status": "active",
        }
        insert = self.backend.insert_one("trades", data)
        if not insert[0]:
            error_msg = "Unable to insert trade details to backend."
            logger.critical(error_msg)
            self.notify.send(error_msg)
            return

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
            error_msg = "Unable to update next trade price details to backend."
            logger.critical(error_msg)
            self.notify.send(error_msg)
            return

        close_value = float(limit_close_order[1]["price"]) * float(close_trade_value)

        logger.info(
            """%s | Trade opened
Id: %s | Side: %s | Price: %s %s | Amount: %s %s | Cost: %s %s | Fee: %s %s

Closing order
Side: %s | Price: %s %s | Amount: %s %s | Value: %s %s""",
            market,
            limit_close_order[1]["id"],
            self.settings["open_side"],
            open_order_details[1]["average"],
            self.settings["quote"],
            open_order_details[1]["filled"],
            self.settings["base"],
            open_order_details[1]["cost"],
            self.settings["quote"],
            open_order_details[1]["fee"]["cost"],
            open_order_details[1]["fee"]["currency"],
            self.settings["close_side"],
            limit_close_order[1]["price"],
            self.settings["quote"],
            close_trade_value,
            self.settings["base"],
            close_value,
            self.settings["quote"],
        )
        self.notify.send(
            f"""<b>Trade opened</b>
            Id: {limit_close_order[1]["id"]}
            Market: {market}
            Side: {self.settings['open_side']}
            Price: {open_order_details[1]['average']} {self.settings['quote']}
            Amount: {open_order_details[1]['filled']} {self.settings['base']}
            Cost: {open_order_details[1]['cost']} {self.settings['quote']}
            Fee: {open_order_details[1]["fee"]["cost"]} {open_order_details[1]["fee"]["currency"]}

            <b>Closing order</b>
            Side: {self.settings['close_side']}
            Price: {limit_close_order[1]['price']} {self.settings['quote']}
            Amount: {close_trade_value} {self.settings['base']}
            Value: {close_value} {self.settings['quote']}""",
        )

    def single_check_order(self, order_id):

        fetch_order = self.exchange.fetch_order(
            self.settings["market"],
            order_id,
        )
        if fetch_order[0]:
            return fetch_order[1]

        return {}

    def check_closed_orders(self):
        """
        TO DO
        """

        closed_orders = self.orders["closed"]
        open_on_backend = list(self.orders["open_on_backend"])
        open_on_exchange = self.orders["open_on_exchange"]
        if closed_orders[1]:

            # Extend closed orders with active orders if needed
            if open_on_exchange[0] and len(open_on_backend) > 0:
                open_on_backend_count = len(open_on_backend)
                open_on_exchange_count = len(open_on_exchange[1])
                if open_on_backend_count > open_on_exchange_count:

                    logger.warning(
                        f'Found {open_on_backend_count-open_on_exchange_count} open trades that should have been closed already.'
                    )
                    logger.warning('Additionally checking all ({open_on_backend_count}) active orders on the exchange separately.')
                    logger.warning('This will take around ({open_on_backend_count}) seconds.')

                    extra_orders = []
                    for order in open_on_backend:
                        extra_orders.append(self.single_check_order(order["_id"]))
                        time.sleep(1)
                    closed_orders[1].extend(extra_orders)

            # Loop closed orders
            for close_order in closed_orders[1]:

                if 'id' in close_order:

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
                                    "%s | Trade closed (%s) | Id: %s",
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
                                error_msg = "Unable to update closed order details to backend."
                                logger.critical(error_msg)
                                self.notify.send(error_msg)

                        elif status == "active" and close_order["status"] == "closed":

                            profit = set_profit(profit_in, open_order, close_order)
                            fees = set_fees(open_order["fee"], close_order["fee"])

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
                                    """%s | Trade closed
Id: %s | Profit:     %s %s (%s%%) | Open fee: %s %s | Close fee: %s %s

Statistics
Active trades: %    s | Finished trades: %s
Total profit (Ex    . fees): %s
Total fees spend    : %s""",
                                    market,
                                    close_order["id"],
                                    profit,
                                    profit_currency,
                                    profit_perc,
                                    open_order["fee"]["cost"],
                                    open_order["fee"]["currency"],
                                    close_order["fee"]["cost"],
                                    close_order["fee"]["currency"],
                                    self.get_count("trades", {"status": "active"}),
                                    self.get_count("trades", {"status": "finished"}),
                                    self.stringify_profit_aggregates(),
                                    self.stringify_total_fees(),
                                )
                                self.notify.send(
                                    f"""<b>Trade closed</b>
                                    Id: {close_order['id']}
                                    Market: {market}
                                    Profit: {profit:.8f} {profit_currency} ({profit_perc:.2f}%)
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
                                error_msg = "Unable to update trade details to backend."
                                logger.critical(error_msg)
                                self.notify.send(error_msg)
