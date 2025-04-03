fetch('/api/advisors')
    .then(response => response.json())
    .then(advisors => {
        const advisorContainer = document.getElementById('advisor-container');
        const title = document.createElement('h3');
        title.textContent = "";
        advisorContainer.appendChild(title);

        advisors.forEach(advisor => {
            const advisorElement = document.createElement('div');
            advisorElement.classList.add('list-group-item', 'list-group-item-action');
            advisorElement.textContent = `${advisor.first_name} ${advisor.last_name}`;
            advisorElement.setAttribute('data-advisor-email', advisor.email);

            advisorElement.addEventListener('click', function () {
                document.querySelectorAll('.list-group-item').forEach(item => item.classList.remove('selected-advisor'));
                this.classList.add('selected-advisor');

                // Retrieve Student Email from Hidden Input
                let studentEmailField = document.getElementById("student-email");
                if (!studentEmailField.value.trim()) {
                    fetch('/api/session/student-email')
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! Status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log("Student email from session:", data.student_email);
                            document.getElementById('student-email').value = data.student_email;
                        })
                        .catch(error => console.error("Error fetching student email from session:", error));

                }

                const advisorEmail = this.getAttribute('data-advisor-email') || "";
                if (!advisorEmail) {
                    console.error("Advisor email is missing from selection.");
                    return;
                }
                console.log("Selected Advisor Email:", advisorEmail);

                // Set the advisor's details in the hidden input fields
                document.getElementById('advisor-email').value = advisorEmail;
                document.getElementById('advisor-name').value = advisor.first_name;
                document.getElementById('advisor-last').value = advisor.last_name;
                document.getElementById('advisor-office').value = advisor.office;

                // Log hidden field values
                console.log("Hidden input fields updated:", {
                    email: document.getElementById('advisor-email').value,
                    name: document.getElementById('advisor-name').value,
                    last: document.getElementById('advisor-last').value,
                    office: document.getElementById('advisor-office').value,
                    student_email: document.getElementById('student-email').value
                });

                fetch(`/api/availability/${encodeURIComponent(advisorEmail.trim())}/dates`)
                    .then(response => response.json())
                    .then(advisorData => {
                        console.log("Fetched Advisor Data:", advisorData);
                        if (!advisorData || !advisorData.available_dates) {
                            console.error("Invalid advisor data received:", advisorData);
                            return;
                        }

                        updateCalendar(advisorData.available_dates);
                        generateTimeSlots("", advisorEmail);
                    })
                    .catch(error => console.error("Error fetching advisor details:", error));
            });

            advisorContainer.appendChild(advisorElement);
        });
    })
    .catch(error => console.error('Error fetching advisors:', error));


document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var selectedDateElement = null;


    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        events: [],
        eventClick: function (info) {
            let selectedDate = info.event.startStr;
            let selectedAdvisorEmail = document.getElementById('advisor-email').value;

            if (!selectedAdvisorEmail) {
                console.error("No advisor selected.");
                return;
            }

            if (selectedDateElement) {
                selectedDateElement.style.backgroundColor = '';
            }
            info.el.style.backgroundColor = "rgba(249, 4, 4, 0.714)";
            selectedDateElement = info.el;
            document.getElementById('selected-date').innerText = "Selected Date: " + selectedDate;

            console.log("Advisor Email Before Fetching Time Slots:", selectedAdvisorEmail);
            generateTimeSlots(selectedDate, selectedAdvisorEmail);
        }
    });
    calendar.render();
});

function updateCalendar(availableDates) {
    if (!calendar) {
        console.error("Calendar instance not found.");
        return;
    }
    calendar.removeAllEvents();
    let events = availableDates.map(date => ({
        title: "Available",
        start: date,
        backgroundColor: "red",
        borderColor: "red",
    }));
    calendar.addEventSource(events);
    calendar.render();
    console.log("Added events to calendar:", events);

    calendar.refetchEvents();
}

function generateTimeSlots(selectedDate, advisorEmail) {
    console.log("Generating time slots for date:", selectedDate, "and advisor:", advisorEmail);
    let timeSlotList = document.getElementById("time-slot-list");
    timeSlotList.innerHTML = '';

    if (!selectedDate || !advisorEmail) {
        console.error("Missing date or advisor email");
        return;
    }

    fetch(`/api/availability/times/${encodeURIComponent(advisorEmail)}/${encodeURIComponent(selectedDate)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Fetched time slots:", data);
            if (data.availableTimes && data.availableTimes.length > 0) {
                data.availableTimes.forEach(time => {
                    let timeSlotItem = document.createElement("div");
                    timeSlotItem.classList.add("time-slot");
                    timeSlotItem.innerHTML = `
                        <label>
                            <input type="radio" name="time" value="${time.time}" /> ${time.time}
                        </label>
                    `;
                    timeSlotList.appendChild(timeSlotItem);
                });
            } else {
                let noTimeMessage = document.createElement("div");
                noTimeMessage.textContent = "No available times for this date.";
                timeSlotList.appendChild(noTimeMessage);
            }
        })
        .catch(error => {
            console.error("Error fetching available times:", error);
            let errorMessage = document.createElement("div");
            errorMessage.textContent = `Error fetching time slots: ${error.message}`;
            timeSlotList.appendChild(errorMessage);
        });
}


document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('submitAppointment').addEventListener('click', function (e) {
        e.preventDefault();

        // Retrieve form values
        const studentEmail = document.getElementById('student-email').value.trim();
        const advisorEmail = document.getElementById('advisor-email').value.trim();
        const advisorName = document.getElementById('advisor-name').value.trim();
        const advisorLastName = document.getElementById('advisor-last').value.trim();
        const advisorOffice = document.getElementById('advisor-office').value.trim();
        let appointmentDate = document.getElementById('selected-date').textContent.trim();
        const studentNote = document.querySelector('.student-note').value.trim();

        // Capture the selected time
        const selectedTime = document.querySelector('input[name="time"]:checked');
        if (!selectedTime) {
            alert('Please select a time slot!');
            return;
        }
        const appointmentTime = selectedTime.value; // Get the selected time

        // Combine date and time
        appointmentDate = appointmentDate.replace('Selected Date: ', '').trim() + ' ' + appointmentTime;

        // Log data to the console
        console.log({
            studentEmail,
            advisorEmail,
            advisorName,
            advisorLastName,
            advisorOffice,
            appointmentDate,
            studentNote
        });

        // Validate inputs
        if (!studentEmail || !advisorEmail || !appointmentDate) {
            alert('Please fill out all required fields!');
            return;
        }

        // Create appointment data object
        const appointmentData = {
            student_email: studentEmail,
            advisor_email: advisorEmail,
            advisor_name: advisorName,
            advisor_last: advisorLastName,
            advisor_office: advisorOffice,
            datetime: appointmentDate,  // Send the complete datetime (date + time)
            note: studentNote
        };

        // Send data to the Flask backend via POST request
        fetch('/api/appointments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(appointmentData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Appointment successfully scheduled!');
                window.location.reload();
            } else {
                alert('Error scheduling appointment!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Something went wrong!');
        });
    });
});



