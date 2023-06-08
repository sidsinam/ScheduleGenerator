from django.db import models
from datetime import datetime, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from datetime import timedelta, date

# Create your models here.
class Instructor(models.Model):
    uid = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.uid + " " + self.name
    
class Course(models.Model):
    uid = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    max_numb_students = models.CharField(max_length=65, default=40)
    instructors = models.ForeignKey(Instructor, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.uid + " " + self.name
    
class Room(models.Model):    
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name + " " + self.capacity
    
time_slots = []

# Start at 00:00 and go until 23:00
current_time = datetime.strptime('00:00', '%H:%M')
end_time = datetime.strptime('23:00', '%H:%M')

while current_time <= end_time:
    time_slot = (current_time.strftime('%H:%M'), current_time.strftime('%H:%M'))
    time_slots.append(time_slot)
    current_time += timedelta(hours=1)

# Add the last time slot at 24:00
time_slots.append(('24:00', '24:00'))

DAYS_OF_WEEK = (
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
)
    
class MeetingTime(models.Model):
    pid = models.CharField(max_length=4, primary_key=True)
    start_time = models.CharField(max_length=50, choices=time_slots[:], default='10:00')
    end_time = models.CharField(max_length=50, choices=time_slots[:], default='16:00')
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)

    def __str__(self):
        return f'{self.pid} {self.day} {self.start_time} {self.end_time}'
