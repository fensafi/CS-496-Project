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

    function generateTimeSlots(selectedDate) {
        let timeSlotList = document.getElementById("time-slot-list");
        timeSlotList.innerHTML = ''; // Clear previous time slots
    
        let startHour = 8;
        let endHour = 15; // Up to 3:00 PM
        let timeInterval = 30; // 30-minute slots
    
        for (let hour = startHour; hour <= endHour; hour++) {
            for (let min = 0; min < 60; min += timeInterval) {
                let displayHour = hour > 12 ? hour - 12 : hour; // Convert 24-hour to 12-hour format
                displayHour = displayHour === 0 ? 12 : displayHour; // Handle 12 AM case
                let minFormatted = min === 0 ? '00' : min;
                let period = hour < 12 ? 'AM' : 'PM'; // Set AM or PM
    
                let timeString = `${displayHour}:${minFormatted} ${period}`; // Correct 12-hour format
    
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
        let advisorEmail = document.getElementById('advisor-email').value;
    
        // Debugging output
        console.log("Sending Data:", { date: selectedDate, time: selectedTime, email: advisorEmail });
    
        if (!selectedTime) {
            alert("Please select a time.");
            return;
        }
    
        let datePattern = /^\d{4}-\d{2}-\d{2}$/;
        if (!datePattern.test(selectedDate)) {
            alert("Invalid date format.");
            return;
        }
    
        fetch("/add_availability", {
            method: "POST",
            body: JSON.stringify({
                date: selectedDate,
                time: selectedTime,
                email: advisorEmail
            }),
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response Data:", data); // Debugging output
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
