# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-04 04:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dj_summary', '0002_auto_20160403_2330'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('incident_date', models.DateField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nick_name', models.CharField(max_length=75)),
                ('middle_name', models.CharField(max_length=75)),
                ('seniority_offset', models.IntegerField()),
                ('phone', models.CharField(max_length=15)),
                ('student_id', models.CharField(max_length=15)),
                ('access', models.CharField(choices=[('G', 'General'), ('M', 'Music Department'), ('E', 'Engineer'), ('A', 'All')], max_length=1)),
                ('exec', models.BooleanField()),
                ('active', models.BooleanField()),
                ('unsubscribe', models.BooleanField()),
                ('sub', models.BooleanField()),
                ('relationship', models.CharField(choices=[('S', 'Student'), ('A', 'Alum'), ('C', 'Community')], max_length=1)),
                ('semester_joined', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dj_summary.Semester')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('volunteer_date', models.DateField()),
                ('number_of_hours', models.DecimalField(decimal_places=2, max_digits=4)),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dj_summary.Semester')),
            ],
        ),
        migrations.RemoveField(
            model_name='membership',
            name='schedule',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='show',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='user',
        ),
        migrations.AddField(
            model_name='schedule',
            name='djs',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='show',
            name='semesters',
            field=models.ManyToManyField(through='dj_summary.Schedule', to='dj_summary.Semester'),
        ),
        migrations.DeleteModel(
            name='Membership',
        ),
    ]