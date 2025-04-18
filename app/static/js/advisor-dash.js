
// Function to open the modal and fill details
function openModal(appointmentId, studentName, date, time) {
    document.getElementById("modal-appointment-id").value = appointmentId;
    document.getElementById("modal-student-name").innerText = studentName;
    document.getElementById("modal-date").innerText = date;
    document.getElementById("modal-time").innerText = time;
    
    document.getElementById("appointmentModal").style.display = "block";
}

// Function to close the modal
function closeModal() {
    document.getElementById("appointmentModal").style.display = "none";
}

// Change week navigation
function changeWeek(direction) {
    let currentWeekStart = new Date("{{ start_of_week }}");
    currentWeekStart.setDate(currentWeekStart.getDate() + (direction * 7));

    let formattedDate = currentWeekStart.toISOString().split("T")[0];
    window.location.href = `/advisor_dashboard?week=${formattedDate}`;
}

function goToWeek() {
    let selectedDate = document.getElementById("week-selector").value;
    if (selectedDate) {
        window.location.href = `/advisor_dashboard?week=${selectedDate}`;
    }
}

// Function to change the week using next/previous buttons
function changeWeek(direction) {
    let currentWeekStart = new Date("{{ start_of_week }}");
    currentWeekStart.setDate(currentWeekStart.getDate() + (direction * 7));

    let formattedDate = currentWeekStart.toISOString().split("T")[0];
    window.location.href = `/advisor_dashboard?week=${formattedDate}`;
}

// Function to jump to a selected week
function goToWeek() {
    let selectedDate = document.getElementById("week-selector").value;
    if (selectedDate) {
        window.location.href = `/advisor_dashboard?week=${selectedDate}`;
    }
}
