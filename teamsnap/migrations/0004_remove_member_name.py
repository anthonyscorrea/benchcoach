# Generated by Django 3.2.6 on 2021-11-21 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teamsnap', '0003_auto_20211121_1540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='name',
        ),
    ]
