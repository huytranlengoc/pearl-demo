# Generated by Django 4.1.7 on 2023-04-02 10:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_reset"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="tfa_secret",
            field=models.CharField(default="", max_length=255),
        ),
    ]