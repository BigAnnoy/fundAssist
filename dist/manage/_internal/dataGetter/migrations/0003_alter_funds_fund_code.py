# Generated by Django 4.2.5 on 2023-09-21 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataGetter", "0002_funds_fund_code_funds_fund_code_zh_funds_fund_cons"),
    ]

    operations = [
        migrations.AlterField(
            model_name="funds",
            name="fund_code",
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
    ]
