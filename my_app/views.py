from django.shortcuts import render, redirect
from .models import *
from .forms import *
from tabulate import tabulate
import random
from datetime import datetime, timedelta

from django.http import HttpResponse
# from bs4 import BeautifulSoup
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Table

# from django.template.loader import get_template
# from xhtml2pdf import pisa


# import numpy as np


NUM_CLASSES = 30
min_course_class = 2                             
weekday_dict = {'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6}


# Create your views here.
def home(request):
    return render(request, 'home.html', {})


# Class definition
class Class:
    def __init__(self, course, instructor, room, day, time):
        self.instructor = instructor
        self.day = day
        self.time = time
        self.course = course
        self.room = room
    
    def __str__(self):
        return f"{self.day} {self.time} {self.room} {self.instructor} ({self.department}) {self.course}"

class DayTimeSlot:
    def __init__(self):
        self.slots = {}

    def add_time_slot(self, day, start_time, end_time):
        if day not in self.slots:
            self.slots[day] = []
        time_slot = {'start_time': start_time, 'end_time': end_time}
        self.slots[day].append(time_slot)

    def __str__(self):
        return self

# Fitness function
def get_fitness(schedule):
    # Initialize counters for conflicts and gaps
    conflicts = 0
    same_class = 0
    minclass = 0
    x = NUM_CLASSES // len(list(schedule.time_slots))
    extra_classes = NUM_CLASSES % len(list(schedule.time_slots))
    classes_per_day = [0] * len(weekday_dict)
    course_class_count = [0] * len(schedule.courses)
    # Check for conflicts and gaps in the schedule
    for i in range(NUM_CLASSES):
        for j in range(i + 1, NUM_CLASSES):
            if schedule.classes[i].time == schedule.classes[j].time and schedule.classes[i].day == schedule.classes[j].day and schedule.classes[i].room == schedule.classes[j].room:
                conflicts += 1
            if schedule.classes[i].instructor == schedule.classes[j].instructor and schedule.classes[i].day == schedule.classes[j].day and schedule.classes[i].time == schedule.classes[j].time:
                conflicts += 1
            if schedule.classes[i].day == schedule.classes[j].day and schedule.classes[i].time == schedule.classes[j].time:
                conflicts += 1
            if schedule.classes[i].day == schedule.classes[j].day and schedule.classes[i].course == schedule.classes[j].course:
                same_class += 1

        classes_per_day[weekday_dict[schedule.classes[i].day] - 1] += 1

        course_index = list(schedule.courses).index(schedule.classes[i].course)
        course_class_count[course_index] += 1
    

    for i in range(len(schedule.courses)):
        # print(course_class_count[COURSES.index(schedule.classes[i].course)])
        if course_class_count[i] < min_course_class:
             minclass += min_course_class - course_class_count[i] 

    balance_penalty = sum([abs(classes_per_day[i] - x) for i in range(len(list(schedule.time_slots)))])
    if extra_classes > 0:
        balance_penalty -= classes_per_day.count(max(classes_per_day))

    #print(f"{minclass} , {conflicts}, {balance_penalty}")
    # Calculate fitness score using conflicts and gaps
    return 1 / (1 * conflicts + 1) * 1 / (0.01 * balance_penalty + 1) * (1 / (1 * same_class + 1))

# Define the schedule class
class Schedule:
    def __init__(self, classes, courses, time_slots):
        self.classes = classes
        self.courses = courses
        self.time_slots = time_slots
        self.fitness = get_fitness(self)
        
        

    def __str__(self):
        self.classes = sorted(self.classes, key = lambda x: x.daytime.day, reverse =True)
        return self

# Define the genetic algorithm function
def genetic_algorithm(num_classes, instructors, meeting_times, rooms, courses, population_size, elite_size, mutation_rate, generations):
    print("Inside genetic algorithm")
    slot = generate_day_time_slot(meeting_times)
    time_slots = slot.slots
    print(time_slots)
    # Create the initial population
    population = []
    for i in range(population_size):
        classes = []
        for j in range(num_classes):
            course = random.choice(courses)
            instructor = random.choice(instructors)
            room = random.choice(rooms)
            day = random.choice(list(time_slots))
            time = random.choice(time_slots[day])
            
            classes.append(Class(course, instructor, room, day, time))
        population.append(Schedule(classes, courses, time_slots))

    
    # Evolve the population for a given number of generations
    for i in range(generations):
        # Sort the population by fitness
        population = sorted(population, key=lambda x: x.fitness, reverse=True)

        # Print the best schedule in this generation
        # print(f"Generation {i+1}\n")
        # for x,scheduled_class in enumerate(population[0].classes):
        #     print(f"{x+1}\t{scheduled_class.course} {scheduled_class.instructor}\t{scheduled_class.daytime.time}\t{scheduled_class.daytime.day}\t{scheduled_class.course}\t{scheduled_class.room}\n")
        # print(f"\nFitness = {population[0].fitness}\n")
        # Select the elite members of the population
        elite = population[:elite_size]

        # Select the remaining members of the population by tournament selection
        tournament_size = 4
        non_elite = []
        for j in range(population_size - elite_size):
            tournament = random.sample(population, tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            non_elite.append(winner)

        # Create the next generation by crossover and mutation
        new_population = []

        # Add the elite members to the next generation
        new_population.extend(elite)

        # Create the remaining members by crossover and mutation
        for j in range(population_size - elite_size):
            # Select two parents by tournament selection
            parents = random.sample(non_elite, 2)
            parent1 = max(parents, key=lambda x: x.fitness)
            parents.remove(parent1)
            parent2 = max(parents, key=lambda x: x.fitness)

            # Perform crossover to create a child
            child = []
            for k in range(num_classes):
                if random.random() < 0.5:
                    child.append(parent1.classes[k])
                else:
                    child.append(parent2.classes[k])

            # Perform mutation on the child
            for k in range(num_classes):
                if random.random() < mutation_rate:
                    course = random.choice(courses)
                    instructor = random.choice(instructors)
                    room = random.choice(rooms)
                    day = random.choice(list(time_slots))
                    time = random.choice(time_slots[day])
                    child[k] = Class(course, instructor, room, day, time)

            # Add the child to the new population
            new_population.append(Schedule(child,courses,time_slots))

        # Set the population to the new population
        population = new_population

    # Print the best schedule in the final generation
    population = sorted(population, key=lambda x: x.fitness, reverse=True) 

    # print(population[0].classes[0].time['start_time'])
    population[0].classes = sorted(population[0].classes, key = lambda x: (weekday_dict[x.day],x.time['start_time'], x.room))
    return population[0]
         
# Instructor
def addInstructor(request):
    # instructors = [
    #     Instructor(uid='UID1', name='John Smith'),
    #     Instructor(uid='UID2', name='Jane Doe'),
    #     Instructor(uid='UID3', name='Michael Johnson'),
    #     Instructor(uid='UID4', name='Emily Brown'),
    #     Instructor(uid='UID5', name='David Davis'),
    #     Instructor(uid='UID6', name='Sarah Wilson'),
    #     Instructor(uid='UID7', name='Daniel Anderson'),
    #     Instructor(uid='UID8', name='Olivia Taylor'),
    #     Instructor(uid='UID9', name='Matthew Martinez'),
    #     Instructor(uid='UID10', name='Sophia Robinson'),
    #     Instructor(uid='UID11', name='Andrew Thompson'),
    #     Instructor(uid='UID12', name='Emma Lewis'),
    #     Instructor(uid='UID13', name='Christopher Green'),
    #     Instructor(uid='UID14', name='Ava Walker'),
    #     Instructor(uid='UID15', name='Joshua Hall'),
    # ]

    # # Save the instructors to the database
    # for instructor in instructors:
    #     instructor.save()
        
    if request.method == 'POST':
        form = InstructorForm(request.POST)

        if form.is_valid():
            form.save()
            all_instructors = Instructor.objects.all
            return render(request, 'add-instructor.html', {'all_instructors': all_instructors})

    else:
        all_instructors = Instructor.objects.all
        return render(request, 'add-instructor.html', {'all_instructors': all_instructors})


def deleteInstructor(request, instructor_id):
    item = Instructor.objects.get(pk=instructor_id)
    item.delete()
    return redirect('add-instructor')


# Course
def addCourse(request):
    # courses_data = [
    #     {'uid': 'CS1', 'name': 'Introduction to Computer Science', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS2', 'name': 'Data Structures and Algorithms', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS3', 'name': 'Programming in Python', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS4', 'name': 'Web Development', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS5', 'name': 'Database Management', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS6', 'name': 'Operating Systems', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS7', 'name': 'Computer Architecture', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS8', 'name': 'Software Engineering', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS9', 'name': 'Artificial Intelligence', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS10', 'name': 'Machine Learning', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS11', 'name': 'Data Mining', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS12', 'name': 'Computer Networks', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS13', 'name': 'Cybersecurity', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS14', 'name': 'Human-Computer Interaction', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS15', 'name': 'Mobile App Development', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS16', 'name': 'Cloud Computing', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS17', 'name': 'Big Data Analytics', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS18', 'name': 'Computer Graphics', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS19', 'name': 'Natural Language Processing', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS20', 'name': 'Blockchain Technology', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS21', 'name': 'Internet of Things', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS22', 'name': 'Parallel and Distributed Computing', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS23', 'name': 'Data Science', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS24', 'name': 'Computer Vision', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS25', 'name': 'Software Testing and Quality Assurance', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS26', 'name': 'Computer Ethics and Professionalism', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS27', 'name': 'Data Visualization', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS28', 'name': 'Information Retrieval', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS29', 'name': 'Robotics', 'max_numb_students': random.randint(30, 60)},
    #     {'uid': 'CS30', 'name': 'Quantum Computing', 'max_numb_students': random.randint(30, 60)},
    # ]
    
    # courses = []
    # for course_data in courses_data:
    #     course = Course(uid=course_data['uid'], name=course_data['name'], max_numb_students=str(course_data['max_numb_students']))
    #     course.save()
    #     courses.append(course)

    # # Assign 2 courses to each instructor
    # instructors = Instructor.objects.all()[:15]  # Get the first 15 instructors
    # for i, instructor in enumerate(instructors):
    #     courses_to_assign = courses[i * 2 : (i * 2) + 2]
    #     for course in courses_to_assign:
    #         course.instructors.add(instructor)


    form = CourseForm(request.POST or None)
    if request.method == 'POST':      

        if form.is_valid():
            form.save()
            all_courses = Course.objects.all    
            return render(request, 'add-course.html', {'all_courses': all_courses, 'form': form })        
    else:
        all_courses = Course.objects.all
        return render(request, 'add-course.html', {'all_courses': all_courses, 'form': form })          
    
    
def deleteCourse(request, course_id):
    item = Course.objects.get(pk=course_id)
    item.delete()
    return redirect('add-course')

# Room
def addRoom(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)

        if form.is_valid():
            form.save()
            all_rooms = Room.objects.all
            return render(request, 'add-room.html', {'all_rooms': all_rooms})

    else:
        all_rooms = Room.objects.all
        return render(request, 'add-room.html', {'all_rooms': all_rooms})
    
def deleteRoom(request, room_id):
    item = Room.objects.get(pk=room_id)
    item.delete()
    return redirect('add-room')

# Meeting Time
def addMeetingTime(request):
    form = MeetingTimeForm(request.POST or None)
    
    if request.method == 'POST':        

        if form.is_valid():
            form.save()
            all_meetingTimes = MeetingTime.objects.all
            return render(request, 'add-meetingTime.html', {'all_meetingTimes': all_meetingTimes, 'form': form })

    else:
        all_meetingTimes = MeetingTime.objects.all
        return render(request, 'add-meetingTime.html', {'all_meetingTimes': all_meetingTimes, 'form': form })

def deleteMeetingTime(request, item_pid):
    item = MeetingTime.objects.get(pk=item_pid)
    item.delete()
    return redirect('add-meetingTime')
    
# Generate Schedule
timetable = []
def generateSchedule(request):
    INSTRUCTORS = Instructor.objects.values_list('name', flat=True)
    COURSES = Course.objects.values_list('name', flat=True)
    ROOMS = Room.objects.values_list('name', flat=True)
    MeetingTimes = MeetingTime.objects.all()
    schedule = genetic_algorithm(NUM_CLASSES, INSTRUCTORS, MeetingTimes, ROOMS, COURSES, population_size=9, elite_size=1, mutation_rate=0.05, generations=500)
    print_schedule(schedule)
    
    timetable.append(schedule.classes)
    
    return render(request, 'generateSchedule.html', {
        'schedule': schedule,       
    })


def generate_day_time_slot(meeting_times):
    slots = DayTimeSlot()
    for meeting_time in meeting_times:
        day = meeting_time.day
        start_time = datetime.strptime(meeting_time.start_time, '%H:%M')
        end_time = datetime.strptime(meeting_time.end_time, '%H:%M')
        current_time = start_time
        while current_time < end_time:
            start = current_time.strftime('%H:%M')
            end = (current_time + timedelta(hours=1)).strftime('%H:%M')
            slots.add_time_slot(day, start, end) 
            current_time += timedelta(hours=1)
    return slots
    

def print_schedule(schedule):
    #schedule.classes = sorted(schedule.classes, key = lambda x: (weekday_dict[x.day], x.room))
    headers = ["ID", "Course", "Day", "Time", "Instructor", "Room", "Department"]
    table = []
    for i, scheduled_class in enumerate(schedule.classes):
        row = [i+1, scheduled_class.course, scheduled_class.day, scheduled_class.time, scheduled_class.instructor, scheduled_class.room]
        table.append(row)
    print(tabulate(table, headers=headers, tablefmt="grid"))
    
    
# def download_pdf(schedule):
#     # Create a response object with the appropriate MIME type
#     response = HttpResponse(content_type='application/pdf')

#     # Set the filename of the PDF
#     response['Content-Disposition'] = 'attachment; filename="table.pdf"'

#     # HTML content of the table
#     table_html = '''
#     <table>
#       <tr>
#         <th>#</th>
#         <th>Course</th>
#         <th>Instructor</th>
#         <th>Day</th>
#         <th>Start Time</th>
#         <th>Room</th>
#       </tr>
#       {% for item in schedule.classes %}
#         <tr>
#           <td>{{ forloop.counter }}</td>
#           <td>{{ item.course }}</td>
#           <td>{{ item.instructor }}</td>
#           <td>{{ item.day }}</td>
#           <td>{{ item.time.start_time }}</td>
#           <td>{{ item.room }}</td>
#         </tr>
#       {% endfor %}
#     </table>
#     '''

#     # Parse the HTML content using BeautifulSoup
#     soup = BeautifulSoup(table_html, 'html.parser')

#     # Extract the table rows and data
#     rows = soup.find_all('tr')
#     table_data = []
#     for row in rows:
#         cols = row.find_all('td')
#         row_data = [col.get_text() for col in cols]
#         table_data.append(row_data)

#     # Create a ReportLab SimpleDocTemplate with the response object and page size
#     doc = SimpleDocTemplate(response, pagesize=letter)

#     # Create a ReportLab Table from the extracted table data
#     table = Table(table_data)

#     # Add styling to the table
#     table.setStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), '#eeeeee'),
#         ('TEXTCOLOR', (0, 0), (-1, 0), '#333333'),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 12),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
#         ('GRID', (0, 0), (-1, -1), 1, '#cccccc'),
#     ])

#     # Build the PDF document with the table
#     elements = [table]
#     doc.build(elements)

#     return response

# def download_pdf(request):
#     # print_schedule(timetable)
#     template_path = 'time-table.html'  # Specify the path to your Django template

#     # Render the template with the provided context
#     template = get_template(template_path)
#     html = template.render({ 'timetable': timetable })

#     # Create a PDF object
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
#     pdf = pisa.CreatePDF(html, dest=response)

#     # If PDF generation successful, return the PDF as a response
#     if not pdf.err:        
#         return response

#     # If there was an error generating the PDF, return an error message
#     return HttpResponse('Error generating PDF', status=500)
