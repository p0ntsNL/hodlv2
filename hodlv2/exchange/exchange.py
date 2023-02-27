# pylint: disable=broad-except
"""
Exchange class.
The exchange class connects to the configured exchange through CCXT.
"""

import logging

import ccxt

from hodlv2.notify.notify import Notify

logger = logging.getLogger(__name__)


class Exchange:
    """
    Exchange class
    """

    def __init__(self, config):
        """
        Init all variables and objects the class needs to work
        """

        # Variables
        self.health = True
        self.config = config

        # Objects
        self.notify = Notify(self.config)

        try:
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
        except Exception as error:
            msg = f"Unable to connect to {self.config['ExchangeSettings']['Exchange']}: {error}"
            logger.critical(msg)
            self.health = False

    def healthcheck(self):
        """
        Return self.health
        """
        return self.health

    def get_market_data(self, market):
        """
        Retrieves market data from the exchange.
        :param market: name of the market to query for
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
        Retrieves all balance data from the exchange.
        """

        try:
            result = self.exchange.fetchBalance()
            return [True, result]
        except Exception as error:
            logger.debug("get_balances error: %s", error)

        logger.error("Unable to retrieve balance data from exchange.")
        self.health = False
        return [False, {}]

    def get_ticker_data(self, market):
        """
        Retrieves ticker data from the exchange.
        :param market: name of the market to query for
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
        Retrieves open orders from the exchange.
        """

        try:
            result = self.exchange.fetchOpenOrders()
            return [True, result]
        except Exception as error:
            logger.debug("get_open_orders error: %s", error)

        logger.error("Unable to retrieve open orders data from exchange.")
        self.health = False
        return [False, {}]

    def get_closed_orders(self):
        """
        Retrieves closed orders from the exchange.
        """

        try:
            result = self.exchange.fetchClosedOrders()
            return [True, result]
        except Exception as error:
            logger.debug("get_closed_orders error: %s", error)

        logger.error("Unable to retrieve closed orders data from exchange.")
        self.health = False
        return [False, {}]

    def fetch_order(self, market, orderid):
        """
        Retrieves order data from a specific order.
        :param market: name of the market to query for
        :param orderid: the orderid to query for
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
        Initiate a limit order on the exchange.
        :param market: name of the market
        :param side: buy or sell
        :param trade_value: trade value of the order
        :param price: price of the order
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
        Initiate a market order on the exchange.
        :param market: name of the market
        :param side: buy or sell
        :param trade_value: trade value of the order
        """

        try:
            trade_value = self.exchange.amount_to_precision(market, float(trade_value))
            result = self.exchange.createOrder(market, "market", side, trade_value)
            return [True, result]
        except Exception as error:
            logger.debug("%s | create_market_order error: %s", market, error)

        logger.error("%s | Unable to create market order.", market)
        return [False, {}]
