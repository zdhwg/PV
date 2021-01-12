from django.db import models

# Create your models here.
class message(models.Model):
    I = models.CharField(max_length=1000)
    T = models.CharField(max_length=1000)
    Time = models.CharField(max_length=1000)
    predict_result = models.CharField(max_length=1000)
    