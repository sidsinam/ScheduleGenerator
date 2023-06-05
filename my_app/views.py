from django.shortcuts import render, redirect
from .models import *
from .forms import *
from tabulate import tabulate
import random
# import numpy as np


NUM_CLASSES = 34  
min_course_class = 2                              
CLASS_TIMES = ["8-9am", "9-10am", "10-11am", "11am-12pm", "12-1pm", "1-2pm", "2-3pm"]
# ROOMS = ["Room A", "Room B", "Room C", "Room D", "Room E"]
# COURSES = ["Introduction to Programming", "Data Structures and Algorithms", "Computer Architecture", "Operating Systems", "Database Systems", "Computer Networks", "Software Engineering", "Web Development", "Machine Learning", "Artificial Intelligence", "Computer Graphics", "Computer Vision", "Natural Language Processing", "Cybersecurity", "Data Science", "Programming Languages", "Theory of Computation"]
# COURSE_INSTRUCTORS = {
#     "Introduction to Programming": ["John Smith", "Jane Doe"],
#     "Data Structures and Algorithms": ["Bob Johnson", "Sara Lee"],
#     "Computer Architecture": ["David Kim", "Amy Chen"],
#     "Operating Systems": ["Mike Davis", "Karen Brown"],
#     "Database Systems": ["Chris Lee", "Emily Wang"],
#     "Computer Networks": ["Alice Lee", "Kevin Chen"],
#     "Software Engineering": ["Tom Davis", "Grace Kim"],
#     "Web Development": ["Jim Lee", "Linda Chen"],
#     "Machine Learning": ["Peter Kim", "Rachel Lee"],
#     "Artificial Intelligence": ["Jenny Chen", "Tom Smith"],
#     "Computer Graphics": ["Sam Lee", "Kate Kim"],
#     "Computer Vision": ["Joe Smith", "Lisa Davis"],
#     "Natural Language Processing": ["Sarah Chen", "Mike Lee"],
#     "Cybersecurity": ["Susan Lee", "Chris Kim"],
#     "Data Science": ["Anna Chen", "Jason Smith"],
#     "Programming Languages": ["Kim Smith", "Mike Brown"],
#     "Theory of Computation": ["Lisa Lee", "John Kim"],
#}
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
# time_dict = {"8-9am": 1, "9-10am" : 2, "10-11am" : 3, "11am-12pm" : 4, "12-1pm" : 5, "1-2pm" :6, "2-3pm": 7}
weekday_dict = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}


# Create your views here.
def home(request):
    return render(request, 'home.html', {})


# Class definition
class Class:
    def __init__(self, course, instructor, room, day, time):
        self.instructor = instructor
        self.daytime = Daytime(day, time)
        self.course = course
        self.room = room
    
    def __str__(self):
        return f"{self.daytime} {self.room} {self.instructor} ({self.department}) {self.course}"

class Daytime:
    def __init__(self, day, time):
      self.day = day
      self.time = time
    def __str__(self):
        return f"{self.day} {self.time}"

# Fitness function
def get_fitness(schedule):
    # Initialize counters for conflicts and gaps
    conflicts = 0
    gaps = 0
    minclass = 0
    x = NUM_CLASSES // len(DAYS)
    extra_classes = NUM_CLASSES % len(DAYS)
    classes_per_day = [0] * len(DAYS)
    course_class_count = [0] * len(schedule.courses)
    # Check for conflicts and gaps in the schedule
    for i in range(NUM_CLASSES):
        for j in range(i + 1, NUM_CLASSES):
            if schedule.classes[i].daytime.time == schedule.classes[j].daytime.time and schedule.classes[i].daytime.day == schedule.classes[j].daytime.day and schedule.classes[i].room == schedule.classes[j].room:
                conflicts += 1
            if schedule.classes[i].instructor == schedule.classes[j].instructor and schedule.classes[i].daytime == schedule.classes[j].daytime:
                conflicts += 1
            if schedule.classes[i].daytime.day == schedule.classes[j].daytime.day and schedule.classes[i].daytime.time == schedule.classes[j].daytime.time:
                conflicts += 1
            # if schedule.classes[i].daytime.day == schedule.classes[j].daytime.day and abs(time_dict[schedule.classes[i].daytime.time] - time_dict[schedule.classes[j].daytime.time]) > 1:
            #       gaps += 1

        classes_per_day[weekday_dict[schedule.classes[i].daytime.day] - 1] += 1

        course_index = list(schedule.courses).index(schedule.classes[i].course)
        course_class_count[course_index] += 1
    

    for i in range(len(schedule.courses)):
        # print(course_class_count[COURSES.index(schedule.classes[i].course)])
        if course_class_count[i] < min_course_class:
             minclass += min_course_class - course_class_count[i] 

    balance_penalty = sum([abs(classes_per_day[i] - x) for i in range(len(DAYS))])
    if extra_classes > 0:
        balance_penalty -= classes_per_day.count(max(classes_per_day))

    #print(f"{minclass} , {conflicts}, {balance_penalty}")
    # Calculate fitness score using conflicts and gaps
    return 1 / (1 * conflicts + 1) * 1 / (0.01 * balance_penalty + 1) #* (1 / (0.01 * gaps + 1))

# Define the schedule class
class Schedule:
    def __init__(self, classes, courses):
        self.classes = classes
        self.courses = courses
        self.fitness = get_fitness(self)
        

    def __str__(self):
        self.classes = sorted(self.classes, key = lambda x: x.daytime.day, reverse =True)
        return self

# Define the genetic algorithm function
def genetic_algorithm(num_classes, instructors, class_days, class_times, rooms, courses, population_size, elite_size, mutation_rate, generations):
    # Create the initial population
    population = []
    for i in range(population_size):
        classes = []
        for j in range(num_classes):
            course = random.choice(courses)
            instructor = random.choice(instructors)
            room = random.choice(rooms)
            time = random.choice(class_times)
            day = random.choice(class_days)
            classes.append(Class(course, instructor, room, day, time))
        population.append(Schedule(classes, courses))

    
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
                    time = random.choice(class_times)
                    day = random.choice(class_days)
                    child[k] = Class(course, instructor, room, day, time)

            # Add the child to the new population
            new_population.append(Schedule(child,courses))

        # Set the population to the new population
        population = new_population

    # Print the best schedule in the final generation
    population = sorted(population, key=lambda x: x.fitness, reverse=True) 

    return population[0]
         
# Instructor
def addInstructor(request):
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
    if request.method == 'POST':
        form = CourseForm(request.POST)

        if form.is_valid():
            form.save()
            all_courses = Course.objects.all
            return render(request, 'add-course.html', {'all_courses': all_courses})

    else:
        all_courses = Course.objects.all
        return render(request, 'add-course.html', {'all_courses': all_courses})
    
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
def generateSchedule(request):
    INSTRUCTORS = Instructor.objects.values_list('name', flat=True)
    COURSES = Course.objects.values_list('name', flat=True)
    ROOMS = Room.objects.values_list('name', flat=True)
    #DAYS = MeetingTime.objects.all.day
    #TIMES = MeetingTime.object.all.time

    schedule = genetic_algorithm(NUM_CLASSES, INSTRUCTORS, DAYS, CLASS_TIMES, ROOMS, COURSES, population_size=9, elite_size=1, mutation_rate=0.05, generations=500)
    
    print_schedule(schedule)
    
    return render(request, 'generateSchedule.html', {
        'schedule': schedule,       
    })
    
def print_schedule(schedule):
    schedule.classes = sorted(schedule.classes, key = lambda x: (weekday_dict[x.daytime.day], 
    # time_dict[x.daytime.time],
     x.room))


    headers = ["ID", "Course", "Day", "Time", "Instructor", "Room", "Department"]
    table = []
    for i, scheduled_class in enumerate(schedule.classes):
        row = [i+1, scheduled_class.course, scheduled_class.daytime.day, scheduled_class.daytime.time, scheduled_class.instructor, scheduled_class.room]
        table.append(row)
    print(tabulate(table, headers=headers, tablefmt="grid"))