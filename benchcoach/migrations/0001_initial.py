# Generated by Django 3.2.6 on 2021-12-17 21:33

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('jersey_number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image', models.FileField(null=True, upload_to='images/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'svg'])])),
            ],
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='StatLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batting_avg', models.DecimalField(decimal_places=3, default=0, max_digits=4)),
                ('onbase_pct', models.DecimalField(decimal_places=3, default=0, max_digits=4)),
                ('slugging_pct', models.DecimalField(decimal_places=3, default=0, max_digits=4)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='benchcoach.player')),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='benchcoach.team'),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(null=True)),
                ('away_team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='away_team', to='benchcoach.team')),
                ('home_team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_team', to='benchcoach.team')),
                ('venue', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='benchcoach.venue')),
            ],
        ),
        migrations.CreateModel(
            name='Positioning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(blank=True, choices=[('EH', 'EH'), ('P', 'P'), ('C', 'C'), ('1B', '1B'), ('2B', '2B'), ('3B', '3B'), ('SS', 'SS'), ('LF', 'LF'), ('CF', 'CF'), ('RF', 'RF'), ('DH', 'DH')], default=None, max_length=2, null=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='benchcoach.event')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='benchcoach.player')),
            ],
            options={
                'unique_together': {('player', 'event')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='player',
            unique_together={('first_name', 'last_name')},
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.IntegerField(choices=[(2, 'Yes'), (0, 'No'), (1, 'Maybe'), (-1, 'Unknown')], default=-1)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='benchcoach.event')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='benchcoach.player')),
            ],
            options={
                'verbose_name_plural': 'availabilities',
                'unique_together': {('event', 'player')},
            },
        ),
    ]
