# Generated by Django 3.2.6 on 2021-11-21 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lineups', '0006_alter_positioning_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='positioning',
            name='position',
            field=models.CharField(blank=True, choices=[('EH', 'EH'), ('P', 'P'), ('C', 'C'), ('1B', '1B'), ('2B', '2B'), ('3B', '3B'), ('SS', 'SS'), ('LF', 'LF'), ('CF', 'CF'), ('RF', 'RF'), ('DH', 'DH')], default=None, max_length=2, null=True),
        ),
    ]
