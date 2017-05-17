from django.contrib import admin
from .models import Framework, Sentence, Assumption, RandomVariable, Rule


admin.site.register(Framework)
admin.site.register(Sentence)
admin.site.register(Assumption)
admin.site.register(RandomVariable)
admin.site.register(Rule)

