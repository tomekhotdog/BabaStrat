from datetime import datetime, timedelta
from babaApp.models import DataTick, DataSet, Market
from babaApp.extras import applicationStrings

DAY = '1'
WEEK = '2'
MONTH = '3'
_3MONTHS = '4'
YEAR = '5'
THREE_YEARS = '6'


# Returns the JSON representation for a query of
# market data for the relevant symbol and time duration
def get_json(symbol, duration):

    start_date = get_start_date(duration)
    query = query_data(symbol, start_date)
    json = queryset_to_json(query, symbol)

    return json


def get_start_date(duration, current_date=datetime.now()):
    time_delta = timedelta(7)  # Default is week view

    if duration == DAY:
        time_delta = timedelta(1)
    elif duration == WEEK:
        time_delta = timedelta(7)
    elif duration == MONTH:
        time_delta = timedelta(30)
    elif duration == _3MONTHS:
        time_delta = timedelta(90)
    elif duration == YEAR:
        time_delta = timedelta(365)
    elif duration == THREE_YEARS:
        time_delta = timedelta(3 * 365)

    return current_date - time_delta


# Queries django database for DataTicks matching
# symbol and appearing after start_date
def query_data(symbol, start_date):
    return DataTick.objects.filter(dataset__dataset_name=symbol,
                                   tick_time__gte=start_date).order_by('tick_time')


def queryset_to_json(queryset, label):
    labels = []
    chart_data = []
    for res in queryset:
        # print(res) # access elements: res.tick_time, res.price

        labels.append(' ') # Empty label - do some custom logic here
        price_point = (res.bid_price + res.ask_price) / 2
        chart_data.append(str(price_point))

    datasets = [{
        'label': label,
        'fillColor': 'rgba(220,220,220,0.2)',
        'strokeColor': "rgba(220,220,220,1)",
        'pointColor': "rgba(226,118,137,1)",
        'pointStrokeColor': "#fff",
        'pointHighlightFill': "#fff",
        'pointHighlightStroke': "rgba(220,220,220,1)",
        'pointHoverBackgroundCover': "rgba(226, 118, 137, 1)",
        'pointHoverBorderColor': "rgba(226, 118, 137, 1)",
        'lineTension': 0,
        'cubicInterpolationMode': 'default',
        'data': chart_data
    }]

    data = {'labels': labels, 'datasets': datasets}

    return data


# Returns the first recorded price for a given direction integer, symbol and date
def get_symbol_price(symbol, date, direction):
    market = Market.objects.get(symbol=symbol)
    data_set = DataSet.objects.get(dataset_name=market.market_name)
    data_ticks = DataTick.objects.filter(dataset=data_set, tick_time__gte=date).order_by('tick_time')

    if len(data_ticks) > 0:
        if direction == applicationStrings.BUY_DIRECTION:
            return data_ticks[0].ask_price
        if direction == applicationStrings.SELL_DIRECTION:
            return data_ticks[0].bid_price

    raise MarketDataUnavailable('Market data unavailable for: ' + symbol + ', date: ' + str(date))


class MarketDataUnavailable(Exception):
    def __init__(self, message):
            self.message = message