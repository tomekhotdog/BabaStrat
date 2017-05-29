import oandapy
import datetime
from BABAReasoning import credentials


class MarketDataSource:

    def __init__(self):
        self.oanda = oandapy.API(environment=credentials.oanda_environment,
                                 access_token=credentials.oanda_access_token)

    # Queries real time market data provider
    # for current best ask price (oanda)
    def request(self, symbol):
        response = self.oanda.get_prices(instruments=symbol)
        prices = response.get("prices")
        time = prices[0].get("time")
        ask_price = prices[0].get("ask")
        bid_price = prices[0].get("bid")

        return RealTimeTick(time, ask_price, bid_price)


class RealTimeTick:

    # time and asking_prices arguments are strings
    def __init__(self, time, ask_price, bid_price):
        self.time = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.ask_price = float(ask_price)
        self.bid_price = float(bid_price)
