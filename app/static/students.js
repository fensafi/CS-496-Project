// Fetch advisors and display them in a flexbox
fetch('/api/advisors')
    .then(response => response.json())
    .then(advisors => {
        const advisorContainer = document.getElementById('advisor-container');

        // Add a title inside the container
        const title = document.createElement('h3');
        title.textContent = "";
        advisorContainer.appendChild(title);

        advisors.forEach(advisor => {
            const advisorElement = document.createElement('div');
            advisorElement.classList.add('list-group-item', 'list-group-item-action');
            advisorElement.textContent = advisor.name;

            advisorElement.setAttribute('data-advisor-name', advisor.name);

            // Click event to select an advisor
            advisorElement.addEventListener('click', function () {
                // Reset selection styles
                document.querySelectorAll('.list-group-item').forEach(item => {
                    item.classList.remove('selected-advisor');
                });

                // Highlight selected advisor
                this.classList.add('selected-advisor');

                const advisorName = this.getAttribute('data-advisor-name');

                // Fetch advisor details from API
                fetch(`/api/advisors/${encodeURIComponent(advisorName)}`)
                    .then(response => response.json())
                    .then(advisorData => {
                        console.log("Advisor Selected:", advisorData.name, advisorData.email, advisorData.office);

                        // Set hidden input fields
                        document.getElementById('advisor-name').value = advisorData.name;
                        document.getElementById('advisor-email').value = advisorData.email;
                        document.getElementById('advisor-office').value = advisorData.office;

                        // Fetch advisor availability
                        fetch(`/api/availability/${encodeURIComponent(advisorName)}/dates`)
                            .then(response => response.json())
                            .then(dates => {
                                updateCalendar(dates);
                                updateTimeSlots([]);
                            })
                            .catch(error => console.error("Error fetching availability:", error));
                    })
                    .catch(error => console.error("Error fetching advisor details:", error));
            });

            advisorContainer.appendChild(advisorElement);
        });
    })
    .catch(error => console.error('Error fetching advisors:', error));

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var selectedDateElement = null; // Store the currently selected date element

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        events: [] // Initially, no events are loaded
    });
    calendar.render();
    
    // Handle date click on the calendar
    calendar.on('dateClick', function(info) {
        // Reset the color of the previous selected date
        if (selectedDateElement) {
            selectedDateElement.style.backgroundColor = ''; // Reset the color
        }
        
        // Set the background color of the clicked date
        info.dayEl.style.backgroundColor = "rgba(249, 4, 4, 0.714)";
        selectedDateElement = info.dayEl; // Update the selected date element
        
        // Display the selected date
        document.getElementById('selected-date').innerText = "Selected Date: " + info.dateStr;
        
        // Fetch available time slots for this date
        generateTimeSlots(info.dateStr); // Pass the selected date to the function
    });

    // Function to generate time slots dynamically
    function generateTimeSlots(selectedDate) {
        let timeSlotList = document.getElementById("time-slot-list");
        timeSlotList.innerHTML = ''; // Clear any previously generated time slots

        // Fetch available time slots from the server
        fetch(`/api/availability/times/${encodeURIComponent(selectedDate)}`)
            .then(response => response.json())
            .then(data => {
                console.log("Fetched time slots:", data); // Debugging

                if (data && data.availableTimes.length > 0) {
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
                errorMessage.textContent = "Error fetching time slots.";
                timeSlotList.appendChild(errorMessage);
            });
    }

});

// Other functions remain the same...
