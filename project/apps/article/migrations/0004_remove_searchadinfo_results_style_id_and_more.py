# Generated by Django 4.2.3 on 2024-05-08 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_searchadinfo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchadinfo',
            name='results_style_id',
        ),
        migrations.RemoveField(
            model_name='searchadinfo',
            name='terms_style_id',
        ),
    ]