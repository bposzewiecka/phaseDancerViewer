# Generated by Django 3.1.13 on 2021-10-08 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0003_auto_20210115_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='assembly',
            name='iterations_left',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
