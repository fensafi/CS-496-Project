document.addEventListener('DOMContentLoaded', function () {

    // Initialize the calendar
    const calendarEl = document.getElementById('calendar');
    window.calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        events: []
    });
    window.calendar.render();  // Render the calendar

    // Fetch global availability on load
    fetch('/api/availabilities/summary')
    .then(response => response.json())
    .then(dates => {
        updateCalendarWithCounts(dates);
    })
    .catch(error => console.error("Error fetching global availability:", error));

    // Fetch advisors and display them
    fetchAdvisors();

    // Event listener for calendar date selection
    window.calendar.on('dateClick', function (info) {
        document.getElementById('selected-date').innerText = "Selected Date: " + info.dateStr;
        generateTimeSlots(info.dateStr);
    });

    // Event listener for time slot selection
    document.getElementById('time-slot-list').addEventListener('change', function (event) {
        document.getElementById('selected-time').value = event.target.value;
    });

    // Event listener for submitting the appointment
    document.getElementById("submitAppointment").addEventListener("click", function () {
        const advisorName = document.querySelector('input[name="advisor_name"]').value;
        const advisorId = document.querySelector('input[name="advisor_id"]').value;
        const studentEmail = document.getElementById("student-email").value;
        const date = document.getElementById("selected-date").textContent.replace("Selected Date: ", "").trim();
        const time = document.getElementById("selected-time").value;
        const note = document.querySelector('.student-note').value;

        fetch("/api/appointments", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                advisor_name: advisorName,
                advisor_id: advisorId,
                student_email: studentEmail,
                date: date,
                time: time,
                note: note
            })
        })
        .then(res => res.json())
        .then(data => {
            console.log("Appointment response:", data);
            alert(data.message);
        })
        .catch(error => {
            console.error("Error submitting appointment:", error);
        });
    });
});

// Fetching and displaying advisors
function fetchAdvisors() {
    fetch('/api/advisors')
        .then(response => response.json())
        .then(advisors => {
            console.log("Fetched advisors:", advisors);
            populateAdvisorList(advisors);
        })
        .catch(error => console.error('Error fetching advisors:', error));
}

function populateAdvisorList(advisors) {
    const advisorContainer = document.getElementById('advisor-container');
    const title = document.createElement('h3');
    title.textContent = "Select an Advisor";
    advisorContainer.appendChild(title);

    advisors.forEach(advisor => {
        if (!advisor.first_name || !advisor.last_name) {
            console.warn("Advisor missing first or last name:", advisor);
            return;
        }

        const fullName = `${advisor.first_name} ${advisor.last_name}`;
        const advisorId = advisor.advisor_id; // Fallback to name if ID is not available
        const advisorElement = document.createElement('div');
        advisorElement.classList.add('list-group-item', 'list-group-item-action');
        advisorElement.textContent = fullName;
        advisorElement.dataset.advisorName = fullName;

        advisorElement.addEventListener('click', () => onAdvisorClick(advisorElement, advisorId));
        advisorContainer.appendChild(advisorElement);
    });
}

function onAdvisorClick(advisorElement, advisorId) {
    console.log("Advisor clicked:", advisorId); // Debugging line
    document.querySelectorAll('.list-group-item').forEach(item =>
        item.classList.remove('selected-advisor')
    );
    advisorElement.classList.add('selected-advisor');

    fetchAdvisorDetails(advisorId);
}


function fetchAdvisorDetails(advisorId) {
    fetch(`/api/advisors/${encodeURIComponent(advisorId)}`)
        .then(response => response.json())
        .then(advisorData => {
            console.log("Received advisor data:", advisorData);
            if (advisorData.advisor_id) {
                updateAdvisorInfo(advisorData);
                fetchAvailabilityDates(advisorData.advisor_id);
            } else {
                console.error('Incomplete advisor data received:', advisorData);
            }
        })
        .catch(error => console.error('Error fetching advisor:', error));
}

function updateAdvisorInfo(advisorData) {
    const full = advisorData.name || `${advisorData.first_name} ${advisorData.last_name}`;
    document.getElementById('advisor-name').value = full;
    document.getElementById('advisor-email').value = advisorData.email;
    document.getElementById('advisor-id').value = advisorData.advisor_id;
    document.getElementById('advisor-office').value = advisorData.office;
}

function fetchAvailabilityDates(advisorId) {
    console.log("Fetching availability dates for:", advisorId);
    fetch(`/api/availability/${encodeURIComponent(advisorId)}/dates`)
        .then(response => response.json())
        .then(datesResponse => {
            console.log("Received availability dates:", datesResponse);
            updateCalendar(datesResponse); // Pass the full response here
            updateTimeSlots([]); // Reset time slots, you can update this later as per your logic
        })
        .catch(error => console.error('Error fetching availability dates:', error));
}

function updateTimeSlots(slots) {
    const timeSlotList = document.getElementById('time-slot-list');
    timeSlotList.innerHTML = ''; // Clear the previous slots

    if (slots && slots.length > 0) {
        slots.forEach(slot => {
            let timeSlotItem = document.createElement('div');
            timeSlotItem.classList.add('time-slot');
            timeSlotItem.innerHTML = `
                <label>
                    <input type="radio" name="time" value="${slot}" />
                    ${slot}
                </label>`;
            timeSlotList.appendChild(timeSlotItem);
        });
    } else {
        let noTimeMessage = document.createElement('div');
        noTimeMessage.textContent = "No available times for this advisor.";
        timeSlotList.appendChild(noTimeMessage);
    }
}

function updateCalendar(datesResponse) {
    const dates = datesResponse.dates; // Access the dates array from the response
    console.log("Updating calendar with dates:", dates);
    const calendar = window.calendar;
    calendar.removeAllEvents();  // Remove all old events

    if (dates && dates.length > 0) {
        dates.forEach(date => {
            console.log(`Adding event for ${date}`);
            // Convert to YYYY-MM-DD regardless of the input format
            const localDate = new Date(date).toISOString().split('T')[0];
            calendar.addEvent({
                title: 'Available',
                start: localDate,
                allDay: true
            });

        });
    } else {
        console.log("No availability dates for this advisor.");
    }
}


function generateTimeSlots(selectedDate) {
    const date = new Date(selectedDate);
    const isoDate = date.toISOString().split('T')[0];  // This gives 'YYYY-MM-DD'
    
    fetch(`/api/availability/times/${encodeURIComponent(selectedDate)}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch available times');
        }
        return response.json();
    })
    .then(data => {
        populateTimeSlots(data.availableTimes);
    })
    .catch(error => {
        console.error("Error fetching available times:", error);
        alert('An error occurred while fetching available times.');
    });
}



function populateTimeSlots(slots) {
    const timeSlotList = document.getElementById("time-slot-list");
    timeSlotList.innerHTML = ''; // Clear previous slots

    if (slots && slots.length > 0) {
        slots.forEach(time => {
            let timeSlotItem = document.createElement("div");
            timeSlotItem.classList.add("time-slot");
            timeSlotItem.innerHTML = `
                <label>
                    <input type="radio" name="time" value="${time}" />
                    ${time}
                </label>`;
            timeSlotList.appendChild(timeSlotItem);
        });
    } else {
        let noTimeMessage = document.createElement("div");
        noTimeMessage.textContent = "No available times for this date.";
        timeSlotList.appendChild(noTimeMessage);
    }
}



function updateCalendarWithCounts(dateCounts) {
    console.log("Updating calendar with date counts:", dateCounts);
    const calendar = window.calendar;
    calendar.removeAllEvents();

    dateCounts.forEach(({start, title}) => {
        const formattedDate = new Date(start).toISOString();  // Ensure FullCalendar recognizes the date
       // Convert to YYYY-MM-DD regardless of the input format
        const localDate = new Date(start).toISOString().split('T')[0];
        calendar.addEvent({
            title: 'Available',
            start: localDate,
            allDay: true
        });

    });
}
