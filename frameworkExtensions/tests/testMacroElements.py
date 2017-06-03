import datetime, math
from django.test import TestCase
from babaApp.models import DataSet, DataTick
from frameworkExtensions import macroElements

ROUNDING = 10000
test_time = datetime.date(2017, 10, 30)

# Using the following values calculated and tests in /testIndicators.py
_7_day_simple = 1.20
_20_day_simple = 1.30
_50_day_simple = 1.40
_100_day_simple = 1.50
_200_day_simple = 1.75
_20_day_exponential = 1.3396
_50_day_exponential = 1.4534
_100_day_exponential = 1.5672


class MacroElementsTests(TestCase):
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
        DataTick.objects.create(dataset=dataset, tick_time=datetime.date(2017, 4, 28), ask_price=2.50, bid_price=2.30)  # -187 days

    def test_macro_expr_operator_parsing(self):
        operator = macroElements.MacroExprOperator('*')
        self.assertEqual(20, operator.calculate(4, 5))

        operator = macroElements.MacroExprOperator('-')
        self.assertEqual(10, operator.calculate(30, 20))

    def test_macro_boolean_operator_parsing(self):
        operator = macroElements.MacroBooleanOperator('and')
        self.assertTrue(operator.calculate(True, True))
        self.assertFalse(operator.calculate(True, False))

        operator = macroElements.MacroBooleanOperator('not')
        self.assertTrue(operator.calculate(False, None))
        self.assertFalse(operator.calculate(True, None))

    def test_macro_expr_parsing(self):
        data_set = DataSet.objects.get(dataset_name='test_set')

        operator = macroElements.MacroBooleanOperator('<=')
        self.assertTrue(operator.calculate(4, 5))
        self.assertTrue(operator.calculate(5, 5))
        self.assertFalse(operator.calculate(7, 5))

        operator = macroElements.MacroBooleanOperator('!=')
        self.assertTrue(operator.calculate(4, 5))
        self.assertFalse(operator.calculate(5, 5))

        operator = macroElements.MacroBooleanOperator('>')
        self.assertTrue(operator.calculate(5, 4))
        self.assertFalse(operator.calculate(-1, 1))

        expr = macroElements.MacroExpr('5.0')
        self.assertAlmostEqual(5.0, expr.calculate(data_set, test_time))
        self.assertNotEqual(4.0, expr.calculate(data_set, test_time))

        expr = macroElements.MacroExpr('7DaySMA')
        self.assertAlmostEqual(_7_day_simple, expr.calculate(data_set, test_time))

        expr = macroElements.MacroExpr('50DayEMA')
        self.assertAlmostEqual(_50_day_exponential, math.ceil(expr.calculate(data_set, test_time) * ROUNDING)/ROUNDING)

    def test_macro_boolean_expr_parsing(self):
        data_set = DataSet.objects.get(dataset_name='test_set')

        expr = macroElements.MacroBooleanExpr('5 < 6')
        self.assertTrue(expr.calculate(data_set, test_time))

        expr = macroElements.MacroBooleanExpr('7DaySMA >= 1.19')
        self.assertTrue(expr.calculate(data_set, test_time))

        expr = macroElements.MacroBooleanExpr('5 < 6 and 7DaySMA >= 1.19')
        self.assertTrue(expr.calculate(data_set, test_time))

        expr = macroElements.MacroBooleanExpr('not 2 < 7DaySMA')
        self.assertTrue(expr.calculate(data_set, test_time))

    def test_macro_rule(self):
        data_set = DataSet.objects.get(dataset_name='test_set')

        expr = macroElements.MacroRule('UpTrend :- 7DaySMA >= 1.19')
        self.assertTrue(expr.calculate(data_set, test_time))

        expr = macroElements.MacroRule('DownTrend :- 100DayEMA > 1.50 and 20DaySMA < 1.405')
        self.assertTrue(expr.calculate(data_set, test_time))

        expr = macroElements.MacroRule('Trend :- 50DayEMA > 1.5 or 100DaySMA >= 1.603')
        self.assertFalse(expr.calculate(data_set, test_time))

        expr = macroElements.MacroRule('Trend :- 50DayEMA * 2 < 3')
        self.assertTrue(expr.calculate(data_set, test_time))

        expr = macroElements.MacroRule('Trend :- 4 > 100DayEMA * 2')
        self.assertTrue(expr.calculate(data_set, test_time))
