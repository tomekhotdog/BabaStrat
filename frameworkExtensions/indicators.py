import sys
from datetime import datetime, timedelta
from babaApp.models import DataSet, DataTick, Indicator
from babaApp.models import Indicator as IndicatorModel

# Indicators represent economic indicators that can
# be calculated from a DataSet of historical data.
#
# Guaranteed: define method 'calculate(DataSet)' which returns current float value


class Indicator:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Price(Indicator):
    def __init__(self):
        super().__init__('Price')

    def calculate(self, data_set, current_date=datetime.now()):
        tick = DataTick.objects.filter(dataset=data_set).order_by('-tick_time')[0]
        return get_price(tick.ask_price, tick.bid_price)


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
                                        tick_time__gte=start_date).order_by(''
                                                                            'tick_time')
        if len(ticks) == 0:
            return 0

        return get_price(ticks[0].bid_price, ticks[0].ask_price)


class Pivot(Indicator):
    def __init__(self):
        super().__init__('Pivot')
        self.high = DayHigh()
        self.low = DayLow()
        self.close = Close()

    def calculate(self, data_set, current_date=datetime.now()):
        high = self.high.calculate(data_set, current_date)
        low = self.close.calculate(data_set, current_date)
        close = self.close.calculate(data_set, current_date)
        return (high + low + close) / 3


# Resistance 1 level: Pivot + (Pivot - Low)
class R1(Indicator):
    def __init__(self):
        super().__init__('R1')
        self.pivot = Pivot()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return (2 * pivot) - low


# Resistance 2H level: Pivot + (High - Low)
class R2(Indicator):
    def __init__(self):
        super().__init__('R2')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot + (high - low)


class R3(Indicator):
    def __init__(self):
        super().__init__('R3')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return high + (2 * (pivot - low))


class S1(Indicator):
    def __init__(self):
        super().__init__('S1')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        return (2 * pivot) - high


class S2(Indicator):
    def __init__(self):
        super().__init__('S2')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot - (high - low)


class S3(Indicator):
    def __init__(self):
        super().__init__('S3')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return low - (2 * (high - pivot))


class WoodiePivot(Indicator):
    def __init__(self):
        super().__init__('WoodiePivot')
        self.high = DayHigh()
        self.low = DayLow()
        self.close = Close()

    def calculate(self, data_set, current_date=datetime.now()):
        high = self.high.calculate(data_set, current_date)
        low = self.close.calculate(data_set, current_date)
        close = self.close.calculate(data_set, current_date)
        return (high + low + (2 * close)) / 4


# Resistance 1 level: Pivot + (Pivot - Low)
class WoodieR1(Indicator):
    def __init__(self):
        super().__init__('WoodieR1')
        self.pivot = WoodiePivot()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return (2 * pivot) - low


# Resistance 2H level: Pivot + (High - Low)
class WoodieR2(Indicator):
    def __init__(self):
        super().__init__('WoodieWiR2')
        self.pivot = WoodiePivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot + (high - low)


class WoodieS1(Indicator):
    def __init__(self):
        super().__init__('WoodieS1')
        self.pivot = WoodiePivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        return (2 * pivot) - high


class WoodieS2(Indicator):
    def __init__(self):
        super().__init__('WoodieS2')
        self.pivot = WoodiePivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot - (high - low)


class FibonacciR1(Indicator):
    def __init__(self):
        super().__init__('FibonacciR1')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot + (0.382 * (high - low))


class FibonacciR2(Indicator):
    def __init__(self):
        super().__init__('FibonacciR2')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot + (0.618 * (high - low))


class FibonacciR3(Indicator):
    def __init__(self):
        super().__init__('FibonacciR3')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot + (1.0 * (high - low))


class FibonacciS1(Indicator):
    def __init__(self):
        super().__init__('FibonacciS1')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot - (0.382 * (high - low))


class FibonacciS2(Indicator):
    def __init__(self):
        super().__init__('FibonacciS2')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot - (0.618 * (high - low))


class FibonacciS3(Indicator):
    def __init__(self):
        super().__init__('FibonacciS3')
        self.pivot = Pivot()
        self.high = DayHigh()
        self.low = DayLow()

    def calculate(self, data_set, current_date=datetime.now()):
        pivot = self.pivot.calculate(data_set, current_date)
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        return pivot + (1.0 * (high - low))


class CamarillaR1(Indicator):
    def __init__(self):
        super().__init__('CamarillaR1')
        self.high = DayHigh()
        self.low = DayLow()
        self.close = Close()

    def calculate(self, data_set, current_date=datetime.now()):
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        close = self.close.calculate(data_set, current_date)
        return close + ((high - low) * (1.1 / 4))


class CamarillaR2(Indicator):
    def __init__(self):
        super().__init__('CamarillaR2')
        self.high = DayHigh()
        self.low = DayLow()
        self.close = Close()

    def calculate(self, data_set, current_date=datetime.now()):
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        close = self.close.calculate(data_set, current_date)
        return close + ((high - low) * (1.1 / 6))


class CamarillaR3(Indicator):
    def __init__(self):
        super().__init__('CamarillaR3')
        self.high = DayHigh()
        self.low = DayLow()
        self.close = Close()

    def calculate(self, data_set, current_date=datetime.now()):
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        close = self.close.calculate(data_set, current_date)
        return close + ((high - low) * (1.1 / 12))


class CamarillaS1(Indicator):
    def __init__(self):
        super().__init__('CamarillaS1')
        self.high = DayHigh()
        self.low = DayLow()
        self.close = Close()

    def calculate(self, data_set, current_date=datetime.now()):
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        close = self.close.calculate(data_set, current_date)
        return close - ((high - low) * (1.1 / 12))

class CamarillaS2(Indicator):
    def __init__(self):
        super().__init__('CamarillaS2')
        self.high = DayHigh()
        self.low = DayLow()
        self.close = Close()

    def calculate(self, data_set, current_date=datetime.now()):
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        close = self.close.calculate(data_set, current_date)
        return close - ((high - low) * (1.1 / 6))


class CamarillaS3(Indicator):
    def __init__(self):
        super().__init__('CamarillaS3')
        self.high = DayHigh()
        self.low = DayLow()
        self.close = Close()

    def calculate(self, data_set, current_date=datetime.now()):
        high = self.high.calculate(data_set, current_date)
        low = self.low.calculate(data_set, current_date)
        close = self.close.calculate(data_set, current_date)
        return close - ((high - low) * (1.1 / 4))


# Utility methods ############


# Create Indicator Objects
def create_indicator_objects():
    i = IndicatorModel(indicator_name='Price'); i.save()
    i = IndicatorModel(indicator_name='7DaySMA'); i.save()
    i = IndicatorModel(indicator_name='20DaySMA'); i.save()
    i = IndicatorModel(indicator_name='50DaySMA'); i.save()
    i = IndicatorModel(indicator_name='100DaySMA'); i.save()
    i = IndicatorModel(indicator_name='200DaySMA'); i.save()
    i = IndicatorModel(indicator_name='20DayEMA'); i.save()
    i = IndicatorModel(indicator_name='50DayEMA'); i.save()
    i = IndicatorModel(indicator_name='100DayEMA'); i.save()
    i = IndicatorModel(indicator_name='DayHigh'); i.save()
    i = IndicatorModel(indicator_name='DayLow'); i.save()
    i = IndicatorModel(indicator_name='Close'); i.save()
    i = IndicatorModel(indicator_name='Pivot'); i.save()
    i = IndicatorModel(indicator_name='R1'); i.save()
    i = IndicatorModel(indicator_name='R2'); i.save()
    i = IndicatorModel(indicator_name='R3'); i.save()
    i = IndicatorModel(indicator_name='S1'); i.save()
    i = IndicatorModel(indicator_name='S2'); i.save()
    i = IndicatorModel(indicator_name='S3'); i.save()
    i = IndicatorModel(indicator_name='WoodiePivot'); i.save()
    i = IndicatorModel(indicator_name='WoodieR1'); i.save()
    i = IndicatorModel(indicator_name='WoodieR2'); i.save()
    i = IndicatorModel(indicator_name='WoodieS1'); i.save()
    i = IndicatorModel(indicator_name='WoodieS2'); i.save()
    i = IndicatorModel(indicator_name='FibonacciR1'); i.save()
    i = IndicatorModel(indicator_name='FibonacciR2'); i.save()
    i = IndicatorModel(indicator_name='FibonacciR3'); i.save()
    i = IndicatorModel(indicator_name='FibonacciS1'); i.save()
    i = IndicatorModel(indicator_name='FibonacciS2'); i.save()
    i = IndicatorModel(indicator_name='FibonacciS3'); i.save()
    i = IndicatorModel(indicator_name='CamarillaR1'); i.save()
    i = IndicatorModel(indicator_name='CamarillaR2'); i.save()
    i = IndicatorModel(indicator_name='CamarillaR3'); i.save()
    i = IndicatorModel(indicator_name='CamarillaS1'); i.save()
    i = IndicatorModel(indicator_name='CamarillaS2'); i.save()
    i = IndicatorModel(indicator_name='CamarillaS3'); i.save()


# Arithmetic average of last n days
def calculate_simple_moving_average(dataset, days, current_date):
    start_date = get_start_date(days, current_date=current_date)
    ticks = DataTick.objects.filter(dataset=dataset,
                                    tick_time__gte=start_date)
    if len(ticks) == 0: return 0

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
    if len(ticks) == 0: return 0
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
    if len(ticks) == 0: return 0

    low = sys.maxsize
    for tick in ticks:
        price = get_price(tick.bid_price, tick.ask_price)
        low = min(price, low)

    return low


def calculate_day_high(data_set, current_date):
    start_date = get_start_date(1, current_date=current_date)
    ticks = DataTick.objects.filter(dataset=data_set,
                                    tick_time__gte=start_date)
    if len(ticks) == 0: return 0

    high = 0
    for tick in ticks:
        price = get_price(tick.bid_price, tick.ask_price)
        high = max(price, high)

    return high


def get_price(ask_price, bid_price):
    return (ask_price + bid_price) / 2
