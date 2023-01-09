#!/usr/bin/python3.10
# pylint: disable=broad-except,import-error
""" A wrapper that utilizes the ccxt library """

import ccxt
import config

import notifywrapper


class CCXTwrapper:
    """TO DO"""

    def __init__(self):
        """TO DO"""

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
        """TO DO"""

        try:
            result = self.exchange.fetchBalance()
            return True, result
        except Exception as error:
            self.notify.send(f"get_balances error: {error}", "ERROR")

        return False, None

    def get_ticker_data(self, market):
        """TO DO"""

        try:
            result = self.exchange.fetchTicker(market)
            return True, result
        except Exception as error:
            self.notify.send(f"{market}: get_ticker_data error: {error}", "ERROR")

        return False, None

    def get_open_orders(self):
        """TO DO"""

        try:
            result = self.exchange.fetchOpenOrders()
            return True, result
        except Exception as error:
            self.notify.send(f"get_open_orders error: {error}", "ERROR")

        return False, None

    def get_closed_orders(self):
        """TO DO"""

        try:
            result = self.exchange.fetchClosedOrders()
            return True, result
        except Exception as error:
            self.notify.send(f"get_closed_orders error: {error}", "ERROR")

        return False, None

    def fetch_order(self, market, orderid):
        """TO DO"""

        try:
            result = self.exchange.fetchOrder(orderid, market)
            return True, result
        except Exception as error:
            self.notify.send(f"{market}: fetch_order error: {error}", "ERROR")

        return False, None

    def create_limit_order(self, market, side, trade_value, price):
        """TO DO"""

        try:
            price = self.exchange.price_to_precision(market, float(price))
            trade_value = self.exchange.amount_to_precision(market, float(trade_value))
            result = self.exchange.createOrder(
                market, "limit", side, trade_value, price
            )
            return True, result
        except Exception as error:
            self.notify.send(f"{market}: create_limit_order error: {error}", "ERROR")

        return False, None

    def create_market_order(self, market, side, trade_value):
        """TO DO"""

        try:
            trade_value = self.exchange.amount_to_precision(market, float(trade_value))
            result = self.exchange.createOrder(market, "market", side, trade_value)
            return True, result
        except Exception as error:
            self.notify.send(f"{market}: create_market_order error: {error}", "ERROR")

        return False, None
