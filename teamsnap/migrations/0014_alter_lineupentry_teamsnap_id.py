# Generated by Django 3.2.6 on 2021-11-21 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamsnap', '0013_remove_lineupentry_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineupentry',
            name='teamsnap_id',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]