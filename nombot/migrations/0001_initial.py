# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('ingredient_id', models.IntegerField()),
                ('fat', models.FloatField()),
                ('carbohydrates', models.FloatField()),
                ('protein', models.FloatField()),
                ('name', models.CharField(max_length=255)),
                ('calories', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('calories', models.FloatField()),
                ('protein', models.FloatField()),
                ('fat', models.FloatField()),
                ('carbs', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='MealEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('date', models.DateTimeField()),
                ('meal', models.ForeignKey(to='nombot.Meal', related_name='meal_entries')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('recipe_id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.IntegerField(serialize=False, primary_key=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30, null=True)),
                ('gender', models.CharField(max_length=10, null=True)),
                ('height', models.IntegerField(null=True)),
                ('gametype', models.CharField(max_length=20, null=True)),
                ('initiation_step', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='WeightEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('weight', models.FloatField()),
                ('date', models.DateTimeField()),
                ('user', models.ForeignKey(to='nombot.User', related_name='weight_entries')),
            ],
        ),
        migrations.AddField(
            model_name='mealentry',
            name='user',
            field=models.ForeignKey(to='nombot.User', related_name='meal_entries'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='recipe',
            field=models.ForeignKey(to='nombot.Recipe', related_name='ingredients'),
        ),
    ]
