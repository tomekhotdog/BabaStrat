from django.conf.urls import url

from . import views

app_name = 'babaApp'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^learn/$', views.learn, name='learn'),
    url(r'^settings/update/(?P<selected_strategy_name>[\w_-|\W]+)/$', views.settings_update, name='settings'),
    url(r'^settings/(?P<selected_strategy_name>[\w_-|\W]+)/$', views.settings, name='settings'),
    url(r'^settings/$', views.settings_default, name='settings'),
    url(r'^reports/$', views.reports, name='reports'),
    url(r'^frameworks/(?P<market_name>[\w-]+)/(?P<strategy_name>[\w_-|\W]+)/$', views.frameworks, name='frameworks'),
    url(r'^frameworks/(?P<market_name>[\w-]+)/$', views.frameworks_with_market, name='frameworks_with_market'),
    url(r'^frameworks/$', views.frameworks_default, name='frameworks_default'),
    url(r'^analyse/(?P<username>[\w_-|\W]+)/(?P<strategy_name>[\w_-|\W]+)/$', views.analyse, name='analyse'),
    url(r'^marketdata/(?P<instrument_name>[\w-]+)/(?P<duration>[\w]+)/$', views.chart_data, name='chart_data'),
    url(r'^data/empty/$', views.empty, name='empty'),
    url(r'^data/performance/(?P<username>[\w_-|\W]+)/(?P<strategy_name>[\w_-|\W]+)/(?P<start_seconds>[\w\.]+)/(?P<end_seconds>[\w\.]+)/$', views.strategy_performance_data, name='strategy_performance_data'),
    url(r'^data/compare_performance/(?P<username>[\w_-|\W]+)/(?P<strategy_name>[\w_-|\W]+)/(?P<compare_strategy_name>[\w_-|\W]+)/(?P<start_seconds>[\w\.]+)/(?P<end_seconds>[\w\.]+)/$', views.compare_strategy_performance_data, name='strategy_performance_data'),
    url(r'^data/back_test/(?P<username>[\w_-|\W]+)/(?P<strategy_name>[\w_-|\W]+)/(?P<start_seconds>[\w\.]+)/(?P<end_seconds>[\w\.]+)/$', views.back_test_data, name='back_test_data'),
    url(r'^data/compare_back_test/(?P<username>[\w_-|\W]+)/(?P<strategy_name>[\w_-|\W]+)/(?P<compare_strategy_name>[\w_-|\W]+)/(?P<start_seconds>[\w\.]+)/(?P<end_seconds>[\w\.]+)/$', views.compare_back_test_data, name='strategy_performance_data'),
    url(r'^data/semantic_probability/(?P<username>[\w_-|\W]+)/(?P<strategy_name>[\w_-|\W]+)/(?P<sentence>[\w]+)/(?P<semantics>[\w])/$', views.semantic_probability, name='semantic_probability')
]