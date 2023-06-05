from django.db import models

# Create your models here.
class Instructor(models.Model):
    uid = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.uid + " " + self.name
    
class Course(models.Model):
    uid = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.uid + " " + self.name
    
class Room(models.Model):    
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name + " " + self.capacity
    
# Meeting Time
time_slots = (
    ('9:30','9:30'),
    ('10:30','10:30'),
    ('11:30','11:30'),
    ('12:30','12:30'),
    ('2:30','2:30'),
    ('3:30','3:30'),
    ('4:30','4:30')
    # ('9:30 - 10:30', '9:30 - 10:30'),
    # ('10:30 - 11:30', '10:30 - 11:30'),
    # ('11:30 - 12:30', '11:30 - 12:30'),
    # ('12:30 - 1:30', '12:30 - 1:30'),
    # ('2:30 - 3:30', '2:30 - 3:30'),
    # ('3:30 - 4:30', '3:30 - 4:30'),
    # ('4:30 - 5:30', '4:30 - 5:30'),
)
DAYS_OF_WEEK = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)
    
class MeetingTime(models.Model):
    pid = models.CharField(max_length=4, primary_key=True)
    start_time = models.CharField(max_length=50, choices=time_slots[:-1], default='9:30')
    end_time = models.CharField(max_length=50, choices=time_slots[1:], default='4:30')
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)

    def __str__(self):
        return f'{self.pid} {self.day} {self.time}'
