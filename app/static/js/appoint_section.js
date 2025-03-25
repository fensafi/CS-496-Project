document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/appointments')
        .then(response => response.json())
        .then(data => {
            const appointmentsList = document.getElementById("appointments-list");
            data.forEach(appointment => {
                const appointmentDiv = document.createElement("div");
                appointmentDiv.classList.add("appointment");

                const appointmentDetails = `
                    <h3>${appointment.studentName}</h3>
                    <h3>${appointment.studentId}</h3>
                    <p><strong>Date:</strong> ${appointment.date}</p>
                    <p><strong>Time:</strong> ${appointment.time}</p>
                `;

                appointmentDiv.innerHTML = appointmentDetails;
                appointmentsList.appendChild(appointmentDiv);
            });
        })
        .catch(error => console.error('Error fetching appointments', error));
});