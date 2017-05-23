from django.conf.urls import url

from . import views

app_name = 'babaApp'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^learn/$', views.learn, name='learn'),
    url(r'^settings/(?P<selected_framework>[\w-]+)/$', views.settings, name='settings'),
    url(r'^settings/$', views.settings_default, name='settings'),
    url(r'^reports/$', views.reports, name='reports'),
    url(r'^frameworks/(?P<framework_name>[\w-]+)/$', views.frameworks, name='frameworks'),
    url(r'^frameworks/$', views.frameworks_default, name='frameworks_default'),
    url(r'^marketdata/(?P<instrument_name>[\w-]+)/$', views.chart_data, name='chart_data')
]