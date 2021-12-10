# Generated by Django 3.2.6 on 2021-11-21 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamsnap', '0005_availability'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='status_code',
            field=models.SmallIntegerField(choices=[(1, 'Yes'), (0, 'No'), (2, 'Maybe'), (None, 'Unknown')], default=None, null=True),
        ),
    ]