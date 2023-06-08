from django.forms import ModelForm
from. models import *
from django import forms

class InstructorForm(ModelForm):
    class Meta:
        model = Instructor
        fields = [
            'uid',
            'name'
        ]
        
class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = [
            'uid',
            'name',
            'max_numb_students',
            'instructors'
        ]
        
        
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = [            
            'name',
            'capacity'
        ]

class MeetingTimeForm(ModelForm):
    class Meta:
        model = MeetingTime
        fields = [
            'pid',
            'start_time',
            'end_time',
            'day'
        ]
        widgets = {
            'pid': forms.TextInput(),
            'start_time': forms.Select(),
            'end_time': forms.Select(),
            'day': forms.Select(),
        }