from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=32,verbose_name="姓名")
    age = models.IntegerField(verbose_name="年龄")
    email = models.CharField(max_length=32,verbose_name="邮箱")
    company = models.CharField(max_length=32,verbose_name="公司")

