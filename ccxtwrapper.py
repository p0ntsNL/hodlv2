#!/usr/bin/python3.10

import ccxt
import config

import notifywrapper


class CCXTwrapper:
    def __init__(self):

        # Load config
        self.config = config

        exchange_class = getattr(ccxt, self.config.EXCHANGE)
        self.exchange = exchange_class(
            {
                "apiKey": self.config.EXCHANGE_KEY,
                "secret": self.config.EXCHANGE_SECRET,
                "password": self.config.EXCHANGE_PASSWORD,
                "enableRateLimit": True,
            }
        )

        # Notify
        self.notify = notifywrapper.Notify()

    def get_balances(self):

        try:
            result = self.exchange.fetchBalance()
            return True, result
        except Exception as e:
            self.notify.send("get_balances error: {}".format(e), "ERROR")
            self.ok = False

        return False, None

    def get_ticker_data(self, market):

        try:
            result = self.exchange.fetchTicker(market)
            return True, result
        except Exception as e:
            self.notify.send("{}: get_ticker_data error: {}".format(market, e), "ERROR")
            self.ok = False

        return False, None

    def get_open_orders(self):

        try:
            result = self.exchange.fetchOpenOrders()
            return True, result
        except Exception as e:
            self.notify.send("get_open_orders error: {}".format(e), "ERROR")
            self.ok = False

        return False, None

    def get_closed_orders(self):

        try:
            result = self.exchange.fetchClosedOrders()
            return True, result
        except Exception as e:
            self.notify.send("get_closed_orders error: {}".format(e), "ERROR")
            self.ok = False

        return False, None

    def fetch_order(self, market, orderid):

        try:
            result = self.exchange.fetchOrder(orderid, market)
            return True, result
        except Exception as e:
            self.notify.send("{}: fetch_order error: {}".format(market, e), "ERROR")
            self.ok = False

        return False, None

    def create_limit_order(self, market, side, trade_value, price):

        try:
            price = self.exchange.price_to_precision(market, float(price))
            trade_value = self.exchange.amount_to_precision(market, float(trade_value))
            result = self.exchange.createOrder(
                market, "limit", side, trade_value, price
            )
            return True, result
        except Exception as e:
            self.notify.send(
                "{}: create_limit_order error: {}".format(market, e), "ERROR"
            )
            self.ok = False

        return False, None

    def create_market_order(self, market, side, trade_value):

        try:
            trade_value = self.exchange.amount_to_precision(market, float(trade_value))
            result = self.exchange.createOrder(market, "market", side, trade_value)
            return True, result
        except Exception as e:
            self.notify.send(
                "{}: create_market_order error: {}".format(market, e), "ERROR"
            )
            self.ok = False

        return False, None
