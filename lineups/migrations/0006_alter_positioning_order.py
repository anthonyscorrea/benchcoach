# Generated by Django 3.2.6 on 2021-11-19 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lineups', '0005_alter_positioning_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='positioning',
            name='order',
            field=models.PositiveSmallIntegerField(default=0, null=True),
        ),
    ]
