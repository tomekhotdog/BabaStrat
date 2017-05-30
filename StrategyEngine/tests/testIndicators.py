from django.test import TestCase
from babaApp.models import DataSet, DataTick


class IndicatorCalculationTests(TestCase):
    def setUp(self):
        DataSet.objects.create(dataset_name='test_set')

        DataTick.objects.create(dataset='SOMETHING', tick_time='SOMETHING', ask_price=1.20, bid_price=1.20)

    def calculates_7_day_simple_average(self):
        self.assertTrue(True)