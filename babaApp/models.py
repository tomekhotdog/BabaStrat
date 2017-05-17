from django.db import models


class Framework(models.Model):
    framework_name = models.CharField(max_length=200)
    creation_date = models.DateTimeField('Date created')

    def __str__(self):
        return self.framework_name


class Sentence(models.Model):
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class Assumption(models.Model):
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class RandomVariable(models.Model):
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class BayesianNetwork(models.Model):
    randomVariable = models.ForeignKey(RandomVariable, on_delete=models.CASCADE)
    probability = models.DecimalField(max_digits=7, decimal_places=6)


class Rule(models.Model):
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
    rule_head = models.ForeignKey(Sentence, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.rule_head) + " |- {}"
