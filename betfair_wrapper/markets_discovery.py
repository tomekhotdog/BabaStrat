from betfair_wrapper.betfair import Betfair
from betfair_wrapper.betfair.models import MarketFilter


class Market:
    def __init__(self, market_name, market_id, event_ids):
        self.market_name = market_name
        self.market_id = market_id
        self.event_ids = event_ids

    def __str__(self):
        return self.market_name


class SingleEvent:
    def __init__(self, market_name, market_id, event_name, event_id):
        self.market_name = market_name
        self.market_id = market_id
        self.event_name = event_name
        self.event_id = event_id
        self.last_price_traded = 0
        self.probability = 0

    def __str__(self):
        market_name_string = self.market_name.replace(' ', '')
        event_name_string = self.event_name.replace(' ', '')
        return market_name_string + '_' + event_name_string

    def set_last_price_traded(self, last_price_traded):
        self.last_price_traded = last_price_traded

    def set_probability(self, probability):
        self.probability = probability


def get_event_probabilities():
    APP_KEY = '5nE0ssbRgHiSejYG'
    PEM_LOCATION = 'betfair_wrapper/certs/client-2048.pem'

    USERNAME = None
    PASSWORD = None

    client = Betfair(APP_KEY, PEM_LOCATION)
    client.login(USERNAME, PASSWORD)

    client.keep_alive()

    markets = client.list_market_catalogue(
        filter=MarketFilter(text_query='Financial'), market_projection=['RUNNER_DESCRIPTION']
    )

    market_objects, event_objects = create_market_and_event_dictionaries(markets)

    market_ids = [market_id for (market_id, _) in market_objects.items()]
    market_books = client.list_market_book(market_ids=market_ids)

    decorate_event_objects_with_last_traded_prices(market_objects, event_objects, market_books)
    compute_probabilities(market_objects, event_objects)
    client.logout()

    return event_objects


def create_market_and_event_dictionaries(markets):
    market_objects = {}  # market_id: Market
    event_objects = {}  # selection_id: SingleEvent

    for market in markets:
        market_name = market.market_name
        market_id = market.market_id
        market_event_ids = []

        for runner in market.runners:
            event_name = runner.runner_name
            event_id = runner.selection_id

            event = SingleEvent(market_name, market_id, event_name, event_id)
            event_objects[event_id] = event

            market_event_ids.append(event_id)

        market = Market(market_name, market_id, market_event_ids)
        market_objects[market_id] = market

    return market_objects, event_objects


def decorate_event_objects_with_last_traded_prices(market_objects, event_objects, market_books):
    for market_book in market_books:

        for runner in market_book.runners:
            single_event = event_objects[runner.selection_id]

            if isinstance(runner.last_price_traded, float):
                single_event.set_last_price_traded(float(runner.last_price_traded))


def compute_probabilities(market_objects, event_objects):
    for _, market in market_objects.items():
        cumulative_reciprocals = 0

        event_ids = market.event_ids
        for event_id in event_ids:
            event = event_objects[event_id]
            if hasattr(event, 'last_price_traded'):
                price = event.last_price_traded
                reciprocal = (1 / event.last_price_traded) if price > 0 else 0
                cumulative_reciprocals += reciprocal

        if cumulative_reciprocals <= 0: continue
        for event_id in event_ids:
            event = event_objects[event_id]
            if hasattr(event, 'last_price_traded'):
                price = event.last_price_traded
                reciprocal = (1 / price) if price > 0 else 0
                event.set_probability(reciprocal / cumulative_reciprocals * 100)
            else:
                event.set_probability(0.0)