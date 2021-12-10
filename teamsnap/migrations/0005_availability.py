# Generated by Django 3.2.6 on 2021-11-21 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lineups', '0007_alter_positioning_position'),
        ('teamsnap', '0004_remove_member_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teamsnap_id', models.CharField(max_length=10, unique=True)),
                ('status_code', models.SmallIntegerField(null=True)),
                ('benchcoach_availability', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lineups.availability')),
                ('event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teamsnap.event')),
                ('member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teamsnap.member')),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teamsnap.team')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]