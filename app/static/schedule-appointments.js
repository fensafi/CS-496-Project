document.addEventListener("DOMContentLoaded", function () {
    fetchAppointments();
    document.getElementById("cancel").addEventListener("click", function () {
        cancelAppointment();
    });
});

function fetchAppointments() {
    fetch('/api/appointments')
        .then(response => response.json())
        .then(data => {
            const appointmentsContainer = document.querySelector('.scheduled_appointments');
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
                appointmentsHTML += `
                    <li>
                        <input type="radio" name="appointment" value="${appointment.id}" id="appointment-${index}">
                        <label for="appointment-${index}">
                            <strong>Advisor:</strong> ${appointment.advisor_name}<br>
                            <strong>Advisor Email:</strong> <a href="mailto:${appointment.advisor_email}">${appointment.advisor_email}</a><br>
                            <strong>Office:</strong> ${appointment.advisor_office}<br>
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