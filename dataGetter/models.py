from django.db import models

# Create your models here.
class funds(models.Model):
    fund_code=models.CharField;
    fund_code_zh=models.CharField;
    fund_cons=models.CharField;