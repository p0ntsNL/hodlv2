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

        exchange_class = getattr(ccxt, self.config["ExchangeSettings"]["Exchange"])
        self.exchange = exchange_class(
            {
                "apiKey": self.config["ExchangeSettings"]["ExchangeKey"],
                "secret": self.config["ExchangeSettings"]["ExchangeSecret"],
                "password": self.config["ExchangeSettings"]["ExchangePassword"],
                "enableRateLimit": True,
            }
        )
        self.exchange.loadMarkets()

        # Notify
        self.notify = Notify(self.config)

    def get_market_data(self, market):
        """
        TO DO
        """

        try:
            result = self.exchange.market(market)
            return [True, result]
        except Exception as error:
            logger.debug("%s | load_markets error: %s", market, error)

        logger.error("%s | Unable to retrieve market data from exchange.", market)
        return [False, {}]

    def get_balances(self):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchBalance()
            return [True, result]
        except Exception as error:
            logger.debug("get_balances error: %s", error)

        logger.error("Unable to retrieve balance data from exchange.")
        return [False, {}]

    def get_ticker_data(self, market):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchTicker(market)
            return [True, result]
        except Exception as error:
            logger.debug("%s | get_ticker_data error: %s", market, error)

        logger.error("Unable to retrieve ticker data from exchange.")
        return [False, {}]

    def get_open_orders(self):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchOpenOrders()
            return [True, result]
        except Exception as error:
            logger.debug("get_open_orders error: %s", error)

        logger.error("Unable to retrieve open orders data from exchange.")
        return [False, {}]

    def get_closed_orders(self):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchClosedOrders()
            return [True, result]
        except Exception as error:
            logger.debug("get_closed_orders error: %s", error)

        logger.error("Unable to retrieve closed orders data from exchange.")
        return [False, {}]

    def fetch_order(self, market, orderid):
        """
        TO DO
        """

        try:
            result = self.exchange.fetchOrder(orderid, market)
            return [True, result]
        except Exception as error:
            logger.debug("%s | fetch_order error: %s", market, error)

        logger.error("%s | Unable to retrieve order data from exchange.", market)
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
            logger.debug("%s | create_limit_order error: %s", market, error)

        logger.error("%s | Unable to create limit order.", market)
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
            logger.debug("%s | create_market_order error: %s", market, error)

        logger.error("%s | Unable to create market order.", market)
        return [False, {}]
