document.addEventListener("DOMContentLoaded", function () {
    console.log("DOMContentLoaded event triggered"); // Log when DOM is ready
    fetchAppointments();
    document.getElementById("cancel").addEventListener("click", function () {
        cancelAppointment();
    });
});

function fetchAppointments() {
    console.log("Fetching appointments..."); // Log before the fetch call
    fetch('/api/appointments/advisor')
        .then(response => response.json())
        .then(data => {
            console.log("API Response:", data);
            const appointmentsContainer = document.querySelector('.advisors_scheduled_appointments');
            appointmentsContainer.innerHTML = ''; // Clear previous content

            if (data.error) {
                appointmentsContainer.innerHTML = `<p>${data.error}</p>`;
                return;
            }

            if (data.length === 0) {
                appointmentsContainer.innerHTML = "<p>You have no upcoming appointments.</p>";
                return;
            }

            let appointmentsHTML = '<ul>';
            data.forEach((appointment, index) => {
                console.log("Appointment Object:", appointment); // Log each individual appointment
                appointmentsHTML += `
                    <li>
                        <input type="radio" name="appointment" value="${appointment.id}" id="appointment-${index}">
                        <label for="appointment-${index}">
                            <strong>Student:</strong> ${appointment.student_name} ${appointment.student_last_name}<br>
                            <strong>Student Email:</strong> <a href="mailto:${appointment.student_email}">${appointment.student_email}</a><br>
                            <strong>Student ID:</strong> ${appointment.student_id}<br>
                            <strong>Date & Time:</strong> ${appointment.datetime}<br>
                            <strong>Note:</strong> ${appointment.note}
                        </label>
                    </li>`;
            });
            appointmentsHTML += '</ul>';

            appointmentsContainer.innerHTML = appointmentsHTML;
        })
        .catch(error => {
            console.error('Error fetching appointments:', error);
        });
}

function cancelAppointment() {
    const selectedAppointment = document.querySelector('input[name="appointment"]:checked');
    if (!selectedAppointment) {
        alert("Please select an appointment to cancel.");
        return;
    }

    const appointmentId = selectedAppointment.value;

    fetch(`/api/appointments/${appointmentId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchAppointments(); // Refresh the list after deletion
    })
    .catch(error => {
        console.error('Error canceling appointment:', error);
    });
}