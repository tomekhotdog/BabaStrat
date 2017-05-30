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

    def calculate(self, dataset):
        return calculate_simple_moving_average(dataset, 7)


class _20DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset):
        return calculate_simple_moving_average(dataset, 20)


class _50DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset):
        return calculate_simple_moving_average(dataset, 50)


class _100DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset):
        return calculate_simple_moving_average(dataset, 100)


class _200DaySMA(Indicator):
    def __init__(self):
        super().__init__('7DaySMA')

    def calculate(self, dataset):
        return calculate_simple_moving_average(dataset, 200)


class _20DayEMA(Indicator):
    def __init__(self):
        super().__init__('20DayEMA')

    def calculate(self, dataset):
        return calculate_exponential_moving_average(dataset, 20)


class _50DayEMA(Indicator):
    def __init__(self):
        super().__init__('50DayEMA')

    def calculate(self, dataset):
        return calculate_exponential_moving_average(dataset, 50)


class _100DayEMA(Indicator):
    def __init__(self):
        super().__init__('100DayEMA')

    def calculate(self, dataset):
        return calculate_exponential_moving_average(dataset, 100)


# Defines the highest value of the currency in the last 24h
class DayHigh(Indicator):
    def __init__(self):
        super().__init__('DayHigh')

    def calculate(self, dataset):
        return 0


# Defines the lowest value of the currency in the last 24h
class DayLow(Indicator):
    def __init__(self):
        super().__init__('DayHigh')

    def calculate(self, dataset):
        return 0


# Defines the value of the currency 24h in the past
class Close(Indicator):
    def __init__(self):
        super().__init__('DayHigh')

    def calculate(self, dataset):
        return 0


# Utility methods ############

# Arithmetic average of last n days
def calculate_simple_moving_average(dataset, days):
    start_date = get_start_date(days)
    ticks = DataTick.objects.filter(dataset=dataset,
                                    tick_time__gte=start_date)
    cumulative_sum = 0
    for tick in ticks:
        cumulative_sum += ((tick.ask_price + tick.bid_price) / 2)

    cumulative_sum /= len(ticks)
    return cumulative_sum


# Like simple moving average but weighs recent values (exponentially) more
def calculate_exponential_moving_average(dataset, days):
    return 0


# Returns a datetime object 'number_days' days in the past
def get_start_date(number_days):
    current_date = datetime.now()
    time_delta = timedelta(number_days)  # Default is week view

    return current_date - time_delta
