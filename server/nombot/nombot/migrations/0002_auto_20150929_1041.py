# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nombot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('recipe', models.ForeignKey(to='nombot.Recipe', related_name='recipe_entries')),
                ('user', models.ForeignKey(to='nombot.User', related_name='recipe_entries')),
            ],
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='calories',
            new_name='energy',
        ),
    ]
