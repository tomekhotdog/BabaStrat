import sys
from datetime import datetime, timedelta
from babaApp.models import DataSet, DataTick

# Indicators represent economic indicators that can
# be calculated from a DataSet of historical data.
#
# Guaranteed: define method 'calculate(DataSet)' which returns current float value


class Indicator:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class _7DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_simple_moving_average(dataset, 7, current_date)


class _20DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_simple_moving_average(dataset, 20, current_date)


class _50DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_simple_moving_average(dataset, 50, current_date)


class _100DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_simple_moving_average(dataset, 100, current_date)


class _200DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_simple_moving_average(dataset, 200, current_date)


class _20DayEMA(Indicator):
    def __init__(self):
        super().__init__('20DayEMA')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_exponential_moving_average(dataset, 20, current_date)


class _50DayEMA(Indicator):
    def __init__(self):
        super().__init__('50DayEMA')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_exponential_moving_average(dataset, 50, current_date)


class _100DayEMA(Indicator):
    def __init__(self):
        super().__init__('100DayEMA')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_exponential_moving_average(dataset, 100, current_date)


# Defines the highest value of the currency in the last 24h
class DayHigh(Indicator):
    def __init__(self):
        super().__init__('DayHigh')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_day_high(dataset, current_date)


# Defines the lowest value of the currency in the last 24h
class DayLow(Indicator):
    def __init__(self):
        super().__init__('DayLow')

    def calculate(self, dataset, current_date=datetime.now()):
        return calculate_day_low(dataset, current_date)


# Defines the value of the currency 24h in the past
class Close(Indicator):
    def __init__(self):
        super().__init__('DayClose')

    def calculate(self, data_set, current_date=datetime.now()):
        start_date = get_start_date(1, current_date=current_date)
        ticks = DataTick.objects.filter(dataset=data_set,
                                        tick_time__gte=start_date).order_by('tick_time')
        if len(ticks) == 0:
            return 0

        return get_price(ticks[0].bid_price, ticks[0].ask_price)


# Utility methods ############

# Arithmetic average of last n days
def calculate_simple_moving_average(dataset, days, current_date):
    start_date = get_start_date(days, current_date=current_date)
    ticks = DataTick.objects.filter(dataset=dataset,
                                    tick_time__gte=start_date)
    cumulative_sum = 0
    for tick in ticks:
        cumulative_sum += get_price(tick.ask_price, tick.bid_price)

    cumulative_sum /= len(ticks)
    return cumulative_sum


# Like simple moving average but weighs recent values (exponentially) more
# EMA = (t * k) + (y * (1 - k) ), k = 2 / (N + 1)
# EMA = exponential moving average, t = today price, y = yesterday price, N = number of time points
def calculate_exponential_moving_average(dataset, days, current_date):
    start_date = get_start_date(days, current_date=current_date)
    ticks = DataTick.objects.filter(dataset=dataset,
                                    tick_time__gte=start_date)
    number_ticks = len(ticks)
    last_day_ema = None
    multiplier = 2 / (number_ticks + 1)
    for tick in ticks:
        if last_day_ema is None:
            last_day_ema = get_price(tick.ask_price, tick.bid_price)
        else:
            last_day_ema += ((get_price(tick.ask_price, tick.bid_price) - last_day_ema) * multiplier)

    return last_day_ema


# Returns a datetime object 'number_days' days in the past
def get_start_date(number_days, current_date=datetime.now()):
    time_delta = timedelta(number_days)
    return current_date - time_delta


def calculate_day_low(data_set, current_date):
    start_date = get_start_date(1, current_date=current_date)
    ticks = DataTick.objects.filter(dataset=data_set,
                                    tick_time__gte=start_date)
    low = sys.maxsize
    for tick in ticks:
        price = get_price(tick.bid_price, tick.ask_price)
        low = min(price, low)

    return low


def calculate_day_high(data_set, current_date):
    start_date = get_start_date(1, current_date=current_date)
    ticks = DataTick.objects.filter(dataset=data_set,
                                    tick_time__gte=start_date)
    high = 0
    for tick in ticks:
        price = get_price(tick.bid_price, tick.ask_price)
        high = max(price, high)

    return high


def get_price(ask_price, bid_price):
    return (ask_price + bid_price) / 2
