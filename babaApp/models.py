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
