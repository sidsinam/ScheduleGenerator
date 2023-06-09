from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-instructor', views.addInstructor, name='add-instructor'),
    path('delete-instructor/<instructor_id>', views.deleteInstructor, name='delete-instructor'),
    path('add-course', views.addCourse, name='add-course'),    
    path('delete-course/<course_id>', views.deleteCourse, name='delete-course'),
    path('add-room', views.addRoom, name='add-room'),
    path('delete-room/<room_id>', views.deleteRoom, name='delete-room'),
    path('add-meetingTime', views.addMeetingTime, name='add-meetingTime'),
    path('delete-meetingTime/<item_pid>', views.deleteMeetingTime, name='delete-meetingTime'),
    path('generateSchedule', views.generateSchedule, name='generateSchedule'),
<<<<<<< HEAD
    # path('download-pdf', views.download_pdf, name='download-pdf'),
=======
    path('download-pdf', views.download_pdf, name='download-pdf'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
>>>>>>> 9883e03316082401cf9de5d653adf1cb0b11ad81
]
