from django.db import models


class Framework(models.Model):
    framework_name = models.CharField(max_length=200)
    creation_date = models.DateTimeField('Date created')
    string_representation = models.TextField(default='.', blank=True)

    def __str__(self):
        return self.framework_name


class DataSet(models.Model):
    dataset_name = models.CharField(max_length=50)

    def __str__(self):
        return self.dataset_name


class DataTick(models.Model):
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    tick_time = models.DateTimeField('tick_time')
    price = models.DecimalField(max_digits=8, decimal_places=6)

    def __str__(self):
        return self.dataset.dataset_name + " " + str(self.tick_time) + " " + str(self.price)


#########################
#   Trading Settings    #
#########################

TRADING_OPTION_BUY = 0
TRADING_OPTION_SELL = 1
TRADING_OPTION_BOTH = 2


class TradingSettings(models.Model):
    framework_name = models.ForeignKey(Framework, on_delete=models.CASCADE)
    enable_trading = models.BooleanField()
    trading_options = models.IntegerField(default=2)
    required_trade_confidence = models.FloatField()
    close_position_yield = models.FloatField()
    close_position_loss_limit = models.FloatField()


##############################
#    Trades and portfolios   #
##############################

class Portfolio(models.Model):
    start_value = models.FloatField()


class Trade(models.Model):
    framework_name = models.ForeignKey(Framework, on_delete=models.CASCADE)
    instrument_symbol = models.CharField(max_length=50)
    quantity = models.IntegerField()
    value = models.FloatField()
    open_position = models.BooleanField()
