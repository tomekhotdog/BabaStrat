from django.contrib import admin
from .models import Framework, DataSet, DataTick


admin.site.register(Framework)
admin.site.register(DataSet)
admin.site.register(DataTick)
