# Generated by Django 4.2.5 on 2023-09-20 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataGetter", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="funds",
            name="fund_code",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="funds",
            name="fund_code_zh",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="funds",
            name="fund_cons",
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
