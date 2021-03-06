# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-07 09:56
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0038_mptt_to_tree'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lieu',
            options={'ordering': ('path',), 'permissions': (('can_change_status', 'Peut changer l’état'),), 'verbose_name': 'lieu ou institution', 'verbose_name_plural': 'lieux et institutions'},
        ),
        migrations.AlterModelOptions(
            name='oeuvre',
            options={'ordering': ('path',), 'permissions': (('can_change_status', 'Peut changer l’état'),), 'verbose_name': 'œuvre', 'verbose_name_plural': 'œuvres'},
        ),
        migrations.AddField(
            model_name='ensemble',
            name='isni',
            field=models.CharField(blank=True, help_text='Exemple\xa0: «\xa00000000115201575\xa0» pour Le Poème Harmonique.', max_length=16, validators=[django.core.validators.MinLengthValidator(16), django.core.validators.RegexValidator('^\\d{15}[\\dxX]$', 'Numéro d’ISNI invalide.')], verbose_name='Identifiant ISNI'),
        ),
        migrations.AddField(
            model_name='ensemble',
            name='sans_isni',
            field=models.BooleanField(default=False, verbose_name='sans ISNI'),
        ),
        migrations.AddField(
            model_name='individu',
            name='sans_isni',
            field=models.BooleanField(default=False, verbose_name='sans ISNI'),
        ),
    ]
