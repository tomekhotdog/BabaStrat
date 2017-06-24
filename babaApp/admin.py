from django.contrib import admin
from .models import Market, DataSet, DataTick, User, TradingSettings, Trade, Portfolio, Strategy, SimulatedTrade, Indicator, ExchangeEvent


admin.site.register(Market)
admin.site.register(DataSet)
admin.site.register(DataTick)
admin.site.register(User)
admin.site.register(TradingSettings)
admin.site.register(Trade)
admin.site.register(SimulatedTrade)
admin.site.register(Portfolio)
admin.site.register(Strategy)
admin.site.register(Indicator)
admin.site.register(ExchangeEvent)