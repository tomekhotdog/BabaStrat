from django.contrib import admin
from .models import Framework, DataSet, DataTick, User, TradingSettings, Trade, Portfolio


admin.site.register(Framework)
admin.site.register(DataSet)
admin.site.register(DataTick)
admin.site.register(User)
admin.site.register(TradingSettings)
admin.site.register(Trade)
admin.site.register(Portfolio)