#!/usr/bin/python3.10

import importlib
import json
import sys
import time

import config

import ccxtwrapper
import notifywrapper


class Bot:
    def __init__(self):

        # Load config
        self.config = config

        # CCXT Wrapper
        self.ccxt = ccxtwrapper.CCXTwrapper()

        # Notify
        self.notify = notifywrapper.Notify()

    def calculate_trade_value(self, last_price):

        return float(self.config.TRADE_VALUE) / float(last_price)

    def calculate_close_price(self, open_price):

        if self.open_side == "buy":
            return float(open_price) + (
                (float(open_price) / 100) * float(self.config.PERC_CLOSE)
            )
        else:
            return float(open_price) - (
                (float(open_price) / 100) * float(self.config.PERC_CLOSE)
            )

    def calculate_next_open_price(self, open_price):

        if self.open_side == "buy":
            return float(open_price) - (
                (float(open_price) / 100) * float(self.config.PERC_OPEN)
            )
        else:
            return float(open_price) + (
                (float(open_price) / 100) * float(self.config.PERC_OPEN)
            )

    def count_open_orders(self, orders):

        count = 0
        for o in orders:
            if o["symbol"] == self.market:
                count += 1

        return count

    def balance_check(self, balance, required):

        if float(balance) >= float(required):
            return True
        else:
            return False

    def check_next_price(self, next_price, current_price):

        if self.open_side == "buy":
            if current_price <= next_price:
                return True
        else:
            if current_price >= next_price:
                return True

        return False

    def load_local_data(self):

        # Open local data
        with open("data.json", "r") as f:

            data = json.load(f)

            if "active_trades" not in data:
                data["active_trades"] = {}
                data["active_trades"][self.market] = {}
            else:
                if self.market not in data["active_trades"]:
                    data["active_trades"][self.market] = {}

            if "next_price" not in data:
                data["next_price"] = {}
                data["next_price"][self.market] = 0
            else:
                if self.market not in data["next_price"]:
                    data["next_price"][self.market] = 0

            if "finished_trades" not in data:
                data["finished_trades"] = {}
                data["finished_trades"][self.market] = {}
            else:
                if self.market not in data["finished_trades"]:
                    data["finished_trades"][self.market] = {}

            if "profits" not in data:
                data["profits"] = {}
                data["profits"][self.market] = {}
            else:
                if self.market not in data["profits"]:
                    data["profits"][self.market] = {}

            return data

    def add_trade_to_local_data(self, local_data, open_order, close_order):

        if self.market not in local_data["active_trades"]:
            local_data["active_trades"][self.market] = {}

        local_data["active_trades"][self.market][close_order["info"]["txid"][0]] = {
            "open": open_order,
            "close": close_order,
            "profit_in": self.config.PROFIT_IN,
        }

        with open("data.json", "w") as f:
            json.dump(local_data, f)

        self.local_data = local_data

    def save_local_data(self, local_data):

        with open("data.json", "w") as f:
            json.dump(local_data, f)

        self.local_data = local_data

    def add_next_price_to_local_data(self, local_data, next_price):

        if self.market not in local_data["next_price"]:
            local_data["next_price"][self.market] = {}

        local_data["next_price"][self.market] = float(next_price)

        with open("data.json", "w") as f:
            json.dump(local_data, f)

        self.local_data = local_data

    def profit_in_trade_value(self, profit_in, open_amount, open_cost, close_price):

        if profit_in == "quote":
            return float(open_amount)
        elif profit_in == "base":
            return float(open_cost) / float(close_price)

    def calculate_profit(self, profit_in, open_order, close_order):

        if profit_in == "quote":
            profit = (close_order["filled"] * close_order["price"]) - open_order["cost"]
            profit_currency = self.quote

        elif profit_in == "base":
            profit = open_order["filled"] - close_order["filled"]
            profit_currency = self.base

        return profit, profit_currency

    def calculate_total_profit(self):

        profits = {}

        for market, market_data in self.local_data["profits"].items():
            for id, profit_data in market_data.items():

                if profit_data["profit_currency"] not in profits:
                    profits[profit_data["profit_currency"]] = 0
                profits[profit_data["profit_currency"]] += float(profit_data["profit"])

        return profits

    def return_total_profit(self, profits):

        msg = "<b>Total profit</b>"
        for currency, profit in profits.items():

            prof = "<br>{:.8f} {}".format(float(profit), currency)
            msg = msg + prof

        return msg

    def run(self):

        self.notify.send("Starting bot", "INFO", logging_only=True)

        while True:

            # Reload config
            importlib.reload(config)

            # Variables
            self.ok = True
            self.new = False
            self.open_side = self.config.SIDE
            self.close_side = "sell" if self.open_side == "buy" else "buy"

            # If open and closed orders are received from exchange
            self.open_orders = self.ccxt.get_open_orders()
            self.closed_orders = self.ccxt.get_closed_orders()
            if self.open_orders[0] and self.closed_orders[0] and self.ok:

                # Set open and closed orders
                self.open_orders = self.open_orders[1]
                self.closed_orders = self.closed_orders[1]

                # Loop markets
                for m in self.config.MARKETS:

                    # Market specific variables
                    self.ok = True
                    self.new = False
                    self.market = m
                    self.base = self.market.split("/")[0]
                    self.quote = self.market.split("/")[1]

                    # Local data
                    self.local_data = self.load_local_data()
                    self.next_price = float(self.local_data["next_price"][self.market])

                    # Retrieve exchange data
                    self.ticker_data = self.ccxt.get_ticker_data(self.market)
                    if self.ticker_data[0] and self.ok:

                        # Set ticker data
                        self.ticker_data = self.ticker_data[1]

                        # Check if there are open orders to set self.new
                        if self.count_open_orders(self.open_orders) == 0:
                            self.new = True

                        # Check price for reset
                        if (
                            self.check_next_price(
                                float(self.next_price), float(self.ticker_data["last"])
                            )
                            and self.ok
                        ):
                            self.new = True

                        # Initiate new trade if required
                        if self.new and self.ok:

                            self.balances = self.ccxt.get_balances()
                            if self.balances[0] and self.ok:

                                self.balances = self.balances[1]["total"]
                                self.base_balance = float(self.balances[self.base])
                                self.quote_balance = float(self.balances[self.quote])

                                # Check if there is enough quote value available vs trade value
                                if self.balance_check(
                                    self.quote_balance, self.config.TRADE_VALUE
                                ):

                                    self.trade_value = self.calculate_trade_value(
                                        self.ticker_data["last"]
                                    )
                                    self.market_order = self.ccxt.create_market_order(
                                        self.market, self.open_side, self.trade_value
                                    )
                                    if self.market_order[0] and self.ok:

                                        self.open_order_id = self.market_order[1][
                                            "info"
                                        ]["txid"][0]
                                        self.open_order_details = self.ccxt.fetch_order(
                                            self.market, self.open_order_id
                                        )

                                        if self.open_order_details[0] and self.ok:

                                            self.open_order_details = (
                                                self.open_order_details[1]
                                            )

                                            self.close_price = (
                                                self.calculate_close_price(
                                                    self.open_order_details["average"]
                                                )
                                            )
                                            self.next_price = (
                                                self.calculate_next_open_price(
                                                    self.open_order_details["average"]
                                                )
                                            )

                                            self.close_trade_value = (
                                                self.profit_in_trade_value(
                                                    self.config.PROFIT_IN,
                                                    self.open_order_details["filled"],
                                                    self.open_order_details["cost"],
                                                    self.close_price,
                                                )
                                            )

                                            self.close_limit_order = (
                                                self.ccxt.create_limit_order(
                                                    self.market,
                                                    self.close_side,
                                                    self.close_trade_value,
                                                    self.close_price,
                                                )
                                            )
                                            if self.close_limit_order[0] and self.ok:

                                                self.close_order_details = (
                                                    self.close_limit_order[1]
                                                )

                                                self.add_trade_to_local_data(
                                                    self.local_data,
                                                    self.open_order_details,
                                                    self.close_order_details,
                                                )
                                                self.add_next_price_to_local_data(
                                                    self.local_data, self.next_price
                                                )

                                                self.notify.send(
                                                    "<b>Trade opened</b><br>Market: {}<br>Side: {}<br>Price: {} {}<br>Amount: {} {}<br>Cost: {} {}<br><br><b>Closing order</b><br>Close price: {} {}<br>Close amount: {} {}<br>Close cost: {} {}".format(
                                                        self.market,
                                                        self.open_side,
                                                        self.open_order_details[
                                                            "average"
                                                        ],
                                                        self.quote,
                                                        self.open_order_details[
                                                            "filled"
                                                        ],
                                                        self.base,
                                                        self.open_order_details["cost"],
                                                        self.quote,
                                                        self.close_order_details[
                                                            "price"
                                                        ],
                                                        self.quote,
                                                        self.close_trade_value,
                                                        self.base,
                                                        (
                                                            float(
                                                                self.close_order_details[
                                                                    "price"
                                                                ]
                                                            )
                                                            * float(
                                                                self.close_trade_value
                                                            )
                                                        ),
                                                        self.quote,
                                                    ),
                                                    "INFO",
                                                )

                                            else:
                                                self.notify.end(
                                                    "{}: Unable to create limit order...".format(
                                                        self.market
                                                    ),
                                                    "ERROR",
                                                )

                                        else:
                                            self.notify.send(
                                                "{}: Unable to fetch market order data...".format(
                                                    self.market
                                                ),
                                                "ERROR",
                                            )

                                    else:
                                        self.notify.send(
                                            "{}: Unable to create market order...".format(
                                                self.market
                                            ),
                                            "ERROR",
                                        )

                                else:
                                    pass
                                    # self.notify.send('{}: Insufficient balance...'.format(self.market), 'ERROR')

                        # Check closed orders for profit
                        for o in self.closed_orders:

                            if o["id"] in self.local_data["active_trades"][self.market]:

                                self.local_data["active_trades"][self.market][o["id"]][
                                    "close"
                                ] = o
                                self.save_local_data(self.local_data)

                                if (
                                    o["status"] == "canceled"
                                    or o["status"] == "expired"
                                    or o["status"] == "rejected"
                                ):

                                    del self.local_data["active_trades"][self.market][
                                        o["id"]
                                    ]
                                    self.save_local_data(self.local_data)

                                    self.notify.send(
                                        "<b>Trade closed ({})</b><br>Market: {}".format(
                                            o["status"], self.market
                                        ),
                                        "WARNING",
                                    )

                                elif o["status"] == "closed":

                                    self.closed_open_order = self.local_data[
                                        "active_trades"
                                    ][self.market][o["id"]]["open"]
                                    self.closed_close_order = self.local_data[
                                        "active_trades"
                                    ][self.market][o["id"]]["close"]
                                    self.profit_in = self.local_data["active_trades"][
                                        self.market
                                    ][o["id"]]["profit_in"]

                                    self.profit = self.calculate_profit(
                                        self.profit_in,
                                        self.closed_open_order,
                                        self.closed_close_order,
                                    )

                                    self.local_data["finished_trades"][self.market][
                                        o["id"]
                                    ] = self.local_data["active_trades"][self.market][
                                        o["id"]
                                    ]
                                    self.local_data["profits"][self.market][o["id"]] = {
                                        "profit": self.profit[0],
                                        "profit_currency": self.profit[1],
                                    }
                                    del self.local_data["active_trades"][self.market][
                                        o["id"]
                                    ]
                                    self.save_local_data(self.local_data)

                                    # Calculate total profit of the profit currency
                                    self.total_profit = self.calculate_total_profit()
                                    self.total_profit_pretty = self.return_total_profit(
                                        self.total_profit
                                    )

                                    self.notify.send(
                                        "<b>Trade closed</b><br>Market: {}<br>Profit:{:.8f} {}<br><br>{}".format(
                                            self.market,
                                            self.profit[0],
                                            self.profit[1],
                                            self.total_profit_pretty,
                                        ),
                                        "INFO",
                                    )

                    else:
                        self.notify.send(
                            "{}: Unable to retrieve ticker data from exchange...".format(
                                self.market
                            ),
                            "ERROR",
                        )

            else:
                self.notify.send(
                    "{}: Unable to retrieve open and closed order data from exchange...".format(
                        self.market
                    ),
                    "ERROR",
                )

            # Custom sleep after all markets are looped through (10s per market)
            time.sleep(len(self.config.MARKETS) * 10)


if __name__ == "__main__":

    bot = Bot()
    bot.run()
