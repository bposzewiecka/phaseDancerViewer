# Generated by Django 3.1.5 on 2021-01-15 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0002_auto_20210115_1146'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assembly',
            old_name='iteration_right',
            new_name='iterations_right',
        ),
    ]
