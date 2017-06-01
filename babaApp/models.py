from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.username


class Market(models.Model):
    market_name = models.CharField(max_length=200)
    symbol = models.CharField(default='', max_length=30)
    string_representation = models.TextField(default='.', blank=True)

    def __str__(self):
        return self.market_name


class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    strategy_name = models.CharField(default='', max_length=30)
    framework = models.TextField(default='.')

    def __str__(self):
        return '(' + self.market.market_name + ') ' + self.strategy_name


class DataSet(models.Model):
    dataset_name = models.CharField(max_length=50)

    def __str__(self):
        return self.dataset_name


class DataTick(models.Model):
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    tick_time = models.DateTimeField('tick_time')
    ask_price = models.FloatField()
    bid_price = models.FloatField()

    def __str__(self):
        return self.dataset.dataset_name + " " + str(self.tick_time) + \
               "Bid: " + str(self.bid_price) + ". Ask: " + str(self.ask_price)


#########################
#   Trading Settings    #
#########################

TRADING_OPTION_BUY = 0
TRADING_OPTION_SELL = 1
TRADING_OPTION_BOTH = 2


class TradingSettings(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    enable_trading = models.BooleanField(default=True)
    trading_options = models.IntegerField(default=2)
    buy_quantity = models.IntegerField(default=0)
    sell_quantity = models.IntegerField(default=0)
    required_trade_confidence = models.FloatField(default=100)
    close_position_yield = models.FloatField(default=5)
    close_position_loss_limit = models.FloatField(default=5)

    def __str__(self):
        return 'Settings for: ' + self.user.username + ", " + self.strategy.strategy_name


##############################
#    Trades and portfolios   #
##############################

class Portfolio(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    start_value = models.FloatField(default=10000)
    current_value = models.FloatField(default=10000)

    def __str__(self):
        return 'Portfolio for: ' + self.user.username


class Trade(models.Model):
    portfolio = models.ForeignKey(Portfolio, default=1, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    instrument_symbol = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    direction = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    close_price = models.FloatField(null=True, blank=True)
    open_position = models.BooleanField()
    position_opened = models.TimeField(null=True, blank=True)
    position_closed = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.instrument_symbol + ": " + str(self.quantity) + " @ " + str(self.price)

