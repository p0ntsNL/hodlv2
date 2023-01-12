# pylint: disable=broad-except
"""
TO DO
"""

import logging

import ccxt

from hodlv2.notify.notify import Notify

logger = logging.getLogger(__name__)


class Exchange:
    """
    TO DO
    """

    def __init__(self, config):
        """
        TO DO
        """

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
        self.notify = Notify(self.config)

    def get_balances(self):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchBalance()
            return [True, result]
        except Exception as error:
            logger.error(f"get_balances error: {error}")

        return [False, {}]

    def get_ticker_data(self, market):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchTicker(market)
            return [True, result]
        except Exception as error:
            logger.error(f"{market}: get_ticker_data error: {error}")

        return [False, {}]

    def get_open_orders(self):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchOpenOrders()
            return [True, result]
        except Exception as error:
            logger.error(f"get_open_orders error: {error}")

        return [False, {}]

    def get_closed_orders(self):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchClosedOrders()
            return [True, result]
        except Exception as error:
            logger.error(f"get_closed_orders error: {error}")

        return [False, {}]

    def fetch_order(self, market, orderid):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchOrder(orderid, market)
            return [True, result]
        except Exception as error:
            logger.error(f"{market}: fetch_order error: {error}")

        return [False, {}]

    def create_limit_order(self, market, side, trade_value, price):
        """
        TO DO
        """

        try:
            price = self.exchange.price_to_precision(market, float(price))
            trade_value = self.exchange.amount_to_precision(market, float(trade_value))
            result = self.exchange.createOrder(
                market, "limit", side, trade_value, price
            )
            return [True, result]
        except Exception as error:
            logger.error(f"{market}: create_limit_order error: {error}")

        return [False, {}]

    def create_market_order(self, market, side, trade_value):
        """
        TO DO
        """

        try:
            trade_value = self.exchange.amount_to_precision(market, float(trade_value))
            result = self.exchange.createOrder(market, "market", side, trade_value)
            return [True, result]
        except Exception as error:
            logger.error(f"{market}: create_market_order error: {error}")

        return [False, {}]
