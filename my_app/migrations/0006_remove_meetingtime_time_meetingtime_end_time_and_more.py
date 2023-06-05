# Generated by Django 4.1.7 on 2023-06-03 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0005_meetingtime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meetingtime',
            name='time',
        ),
        migrations.AddField(
            model_name='meetingtime',
            name='end_time',
            field=models.CharField(choices=[('10:30', '10:30'), ('11:30', '11:30'), ('12:30', '12:30'), ('2:30', '2:30'), ('3:30', '3:30'), ('4:30', '4:30')], default='4:30', max_length=50),
        ),
        migrations.AddField(
            model_name='meetingtime',
            name='start_time',
            field=models.CharField(choices=[('9:30', '9:30'), ('10:30', '10:30'), ('11:30', '11:30'), ('12:30', '12:30'), ('2:30', '2:30'), ('3:30', '3:30')], default='9:30', max_length=50),
        ),
    ]
