document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('advisors_calendar');
    var selectedDateElement = null; // Store the currently selected date element
    
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        dateClick: function(info) {
            // Reset the color of the previous selected date
            if (selectedDateElement) {
                selectedDateElement.style.backgroundColor = ''; // Reset the color
            }

            // Set the background color of the clicked date
            info.dayEl.style.backgroundColor = "rgba(249, 4, 4, 0.714)";
            selectedDateElement = info.dayEl; // Update the selected date element

            // Display the selected date
            $("#selected-date").text("Selected Date: " + info.dateStr);

            // Show available time slots for the selected date
            generateTimeSlots(info.dateStr); // Pass the selected date to the function
        }
    });
    calendar.render();

    // Function to generate time slots dynamically
    function generateTimeSlots(selectedDate) {
        let timeSlotList = document.getElementById("time-slot-list");
        timeSlotList.innerHTML = ''; // Clear any previously generated time slots

        let startHour = 8;
        let endHour = 15; // 3:00 PM
        let timeInterval = 30; // 30 minutes interval

        for (let hour = startHour; hour <= endHour; hour++) {
            for (let min = 0; min < 60; min += timeInterval) {
                let hourFormatted = hour < 10 ? '0' + hour : hour;
                let minFormatted = min === 0 ? '00' : min;
                let timeString = `${hourFormatted}:${minFormatted} ${hour < 12 ? 'AM' : 'PM'}`;

                let timeSlotItem = document.createElement("div");
                timeSlotItem.classList.add("time-slot");
                timeSlotItem.innerHTML = `
                    <label>
                        <input type="radio" name="time" value="${timeString}" /> ${timeString}
                    </label>
                `;
                timeSlotList.appendChild(timeSlotItem);
            }
        }
    }

    document.getElementById("submitAvailability").addEventListener("click", function() {
        let selectedDate = document.getElementById("selected-date").textContent.split(": ")[1];
        let selectedTime = document.querySelector('input[name="time"]:checked')?.value;
        let advisorEmail = '{{ session.get("email") }}';  // Pull email from the session

        // Check if a time is selected
        if (!selectedTime) {
            alert("Please select a time.");
            return;
        }

        // Send the selected date, time, and email to the server
        fetch("/add_availability", {
            method: "POST",
            body: JSON.stringify({ date: selectedDate, time: selectedTime, email: advisorEmail }),  // Send email from session
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "Availability added successfully!") {
                alert("Availability Added!");
            } else {
                alert("There was an issue adding your availability.");
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert("Error occurred while adding availability.");
        });
    });

});