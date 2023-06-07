from datetime import datetime, timedelta
start_time = "9:00"
end_time = "15:00"

# Define the start and end times
start_time = datetime.strptime(start_time, '%H:%M')
end_time = datetime.strptime(end_time, '%H:%M')

# Generate 1-hour time slots
time_slots = []
current_time = start_time
while current_time < end_time:
    time_slots.append(current_time.strftime('%H:%M'))
    current_time += timedelta(hours=1)

# Print the time slots
for slot in time_slots:
    print(slot)


# Meeting Time
def addMeetingTime(request):
    form = MeetingTimeForm(request.POST or None)
    all_meetingTimes = MeetingTime.objects.all
    
    if request.method == 'POST':        

        if form.is_valid():
            # Get the values from the form
            start_time = datetime.strptime(form.cleaned_data['start_time'], '%H:%M')
            end_time = datetime.strptime(form.cleaned_data['end_time'], '%H:%M')
            day = form.cleaned_data['day']

            # Generate time slots with the corresponding day
            current_time = start_time
            while current_time < end_time:
                time_slot = {
                    'day': day,
                    'time': current_time.strftime('%H:%M')
                }
                time_slots.append(time_slot)
                current_time += timedelta(hours=1)

            # Save the MeetingTime objects with the time slots
            for slot in time_slots:
                meeting_time = form.save(commit=False)
                meeting_time.day = slot['day']
                meeting_time.start_time = datetime.strptime(slot['time'], '%H:%M').time()
                meeting_time.end_time = (datetime.strptime(slot['time'], '%H:%M') + timedelta(hours=1)).time()
                meeting_time.save()
            
            
            return render(request, 'add-meetingTime.html', {'all_meetingTimes': all_meetingTimes, 'form': form })

    else:
        form = MeetingTimeForm()

        return render(request, 'add-meetingTime.html', {'all_meetingTimes': all_meetingTimes, 'form': form })