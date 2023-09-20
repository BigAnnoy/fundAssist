from django.db import models

# Create your models here.
class funds(models.Model):
    fund_code=models.CharField(max_length=50,blank=True);
    fund_code_zh=models.CharField(max_length=50,blank=True);
    fund_cons=models.CharField(max_length=500,blank=True);