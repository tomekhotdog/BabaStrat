from django.db import models


class Framework(models.Model):
    framework_name = models.CharField(max_length=200)
    creation_date = models.DateTimeField('Date created')
    string_representation = models.TextField(default='')

    def __str__(self):
        return self.framework_name
