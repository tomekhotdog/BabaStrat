import datetime
import math

from django.test import TestCase

from babaApp.models import DataSet, DataTick
from frameworkExtensions import indicators

ROUNDING = 10000
test_time_1 = datetime.date(2017, 10, 30)
test_time_2 = tick_time=datetime.datetime(2015, 6, 21, 0, 0, 0)

_7_day_simple = 1.20
_20_day_simple = 1.30
_50_day_simple = 1.40
_100_day_simple = 1.50
_200_day_simple = 1.75
_20_day_exponential = 1.3396
_50_day_exponential = 1.4534
_100_day_exponential = 1.5672

day_high = 1.9
day_low = 1.0
day_close = 1.4


class IndicatorCalculationTests(TestCase):
    def setUp(self):
        DataSet.objects.create(dataset_name='test_set')
        dataset = DataSet.objects.get(dataset_name='test_set')

        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 10, 30), ask_price=1.20, bid_price=1.00)  # Current date for test
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 10, 29), ask_price=1.30, bid_price=1.10)  # -1 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 10, 28), ask_price=1.40, bid_price=1.20)  # -2 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 10, 20), ask_price=1.50, bid_price=1.30)  # -10 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 10, 21), ask_price=1.60, bid_price=1.40)  # -11 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 9, 30), ask_price=1.70, bid_price=1.50)  # -30 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 9, 29), ask_price=1.80, bid_price=1.60)  # -31 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 8, 31), ask_price=1.90, bid_price=1.70)  # -60 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 8, 30), ask_price=2.00, bid_price=1.80)  # -61 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 6, 30), ask_price=2.10, bid_price=1.90)  # -143 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 6, 29), ask_price=2.20, bid_price=2.00)  # -144 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 4, 30), ask_price=2.30, bid_price=2.10)  # -185 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 4, 29), ask_price=2.40, bid_price=2.20)  # -186 days
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 4, 28), ask_price=2.50, bid_price=2.30) # -187 days

        DataSet.objects.create(dataset_name='test_set_2')
        dataset_2 = DataSet.objects.get(dataset_name='test_set_2')
        DataTick.objects.create(dataset=dataset_2, tick_time=datetime.datetime(2015, 6, 20, 12, 0, 0), ask_price=1.20, bid_price=1.20)
        DataTick.objects.create(dataset=dataset_2, tick_time=datetime.datetime(2015, 6, 20, 11, 0, 0), ask_price=1.10, bid_price=1.10)
        DataTick.objects.create(dataset=dataset_2, tick_time=datetime.datetime(2015, 6, 20, 10, 0, 0), ask_price=1.0, bid_price=1.0)
        DataTick.objects.create(dataset=dataset_2, tick_time=datetime.datetime(2015, 6, 20, 9, 0, 0), ask_price=1.70, bid_price=1.70)
        DataTick.objects.create(dataset=dataset_2, tick_time=datetime.datetime(2015, 6, 20, 8, 0, 0), ask_price=1.90, bid_price=1.90)
        DataTick.objects.create(dataset=dataset_2, tick_time=datetime.datetime(2015, 6, 20, 7, 0, 0), ask_price=1.40, bid_price=1.40)

    def test_calculates_7_day_simple_average(self):
        data_set = DataSet.objects.get(dataset_name='test_set')
        indicator = indicators._7DaySMA()
        result = indicator.calculate(data_set, test_time_1)
        self.assertAlmostEqual(_7_day_simple, result)

    def test_calculates_20_day_simple_average(self):
        data_set = DataSet.objects.get(dataset_name='test_set')
        indicator = indicators._20DaySMA()
        result = indicator.calculate(data_set, test_time_1)
        self.assertAlmostEqual(_20_day_simple, result)

    def test_calculates_50_day_simple_average(self):
        data_set = DataSet.objects.get(dataset_name='test_set')
        indicator = indicators._50DaySMA()
        result = indicator.calculate(data_set, test_time_1)
        self.assertAlmostEqual(_50_day_simple, result)

    def test_calculates_100_day_simple_average(self):
        data_set = DataSet.objects.get(dataset_name='test_set')
        indicator = indicators._100DaySMA()
        result = indicator.calculate(data_set, test_time_1)
        self.assertAlmostEqual(_100_day_simple, result)

    def test_calculates_200_day_simple_average(self):
        data_set = DataSet.objects.get(dataset_name='test_set')
        indicator = indicators._200DaySMA()
        result = indicator.calculate(data_set, test_time_1)
        self.assertAlmostEqual(_200_day_simple, result)

    def test_calculates_20_day_exponential_average(self):
        data_set = DataSet.objects.get(dataset_name='test_set')
        indicator = indicators._20DayEMA()
        result = indicator.calculate(data_set, test_time_1)
        self.assertAlmostEqual(_20_day_exponential, math.ceil(result*ROUNDING)/ROUNDING)

    def test_calculates_50_day_exponential_average(self):
        data_set = DataSet.objects.get(dataset_name='test_set')
        indicator = indicators._50DayEMA()
        result = indicator.calculate(data_set, test_time_1)
        self.assertAlmostEqual(_50_day_exponential, math.ceil(result*ROUNDING)/ROUNDING)

    def test_calculates_100_day_exponential_average(self):
        data_set = DataSet.objects.get(dataset_name='test_set')
        indicator = indicators._100DayEMA()
        result = indicator.calculate(data_set, test_time_1)
        self.assertAlmostEqual(_100_day_exponential, math.ceil(result*ROUNDING)/ROUNDING)

    def test_calculates_day_low(self):
        data_set = DataSet.objects.get(dataset_name='test_set_2')
        indicator = indicators.DayLow()
        result = indicator.calculate(data_set, test_time_2)
        self.assertAlmostEqual(day_low, result)

    def test_calculates_day_high(self):
        data_set = DataSet.objects.get(dataset_name='test_set_2')
        indicator = indicators.DayHigh()
        result = indicator.calculate(data_set, test_time_2)
        self.assertAlmostEqual(day_high, result)

    def test_calculates_day_close(self):
        data_set = DataSet.objects.get(dataset_name='test_set_2')
        indicator = indicators.Close()
        result = indicator.calculate(data_set, test_time_2)
        self.assertAlmostEqual(day_close, result)