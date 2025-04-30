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

    console.log("Advisor clicked:", advisorId);

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
            updateCalendar(datesResponse);
            updateTimeSlots([]);
        })
        .catch(error => console.error('Error fetching availability dates:', error));
}

function updateTimeSlots(slots) {
    const timeSlotList = document.getElementById('time-slot-list');
    timeSlotList.innerHTML = '';

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
    const isoDate = date.toISOString().split('T')[0];
    
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

// Start of chatbot.js
const messageInput = document.querySelector(".message-input");
const chatBody = document.querySelector(".chat-body");
const sendMessageButton = document.querySelector("#send-message");

const chatbotToggler = document.querySelector("#chatbot-toggler");

const closeChatbot = document.querySelector("#close-chatbot");

const userData = {
    meessage: null
}

const initialInputHeight = messageInput.scrollHeight;

//Create message element with dynamic classes and return it
const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;
}

// Send message to backend API and process response
const generateBotResponse = async (userMessage) => {
    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Server error');
        }
        
        // Find the thinking message and replace it with the actual response
        const thinkingMessage = document.querySelector(".bot-message.thinking");
        if (thinkingMessage) {
            const responseText = document.createElement("div");
            responseText.className = "message-text";
            
            // Format the response - replace newlines with <br> tags
            responseText.innerHTML = data.response.replace(/\n/g, '<br>');
            
            // Replace the thinking indicator with the actual response
            thinkingMessage.classList.remove("thinking");
            thinkingMessage.querySelector(".message-text").replaceWith(responseText);
        }
        
        // Scroll to the bottom of chat
        chatBody.scrollTop = chatBody.scrollHeight;
        
    } catch (error) {
        console.error('Error:', error);
        
        // Show error message
        const thinkingMessage = document.querySelector(".bot-message.thinking");
        if (thinkingMessage) {
            const responseText = document.createElement("div");
            responseText.className = "message-text";
            responseText.textContent = "Sorry, I encountered an error. Please try again.";
            
            thinkingMessage.classList.remove("thinking");
            thinkingMessage.querySelector(".message-text").replaceWith(responseText);
        }
    }
}

// Handle outgoing user messages 
const handleOutGoingMessage = (e) => {
    e.preventDefault();
    messageInput.dispatchEvent(new Event("input"));

    userData.message = messageInput.value.trim();
    
    // Don't process empty messages
    if (!userData.message) return;
    
    messageInput.value = "";
    // Create and display user message 
    const messageContent = `<div class="message-text"></div>`;

    const outgoingMessageDiv = createMessageElement(messageContent, "user-message");
    outgoingMessageDiv.querySelector(".message-text").textContent = userData.message;
    chatBody.appendChild(outgoingMessageDiv);
    
    // Scroll to the bottom of chat after adding user message
    chatBody.scrollTop = chatBody.scrollHeight;

    // Simulate bot response with thinking indicator after a delay
    setTimeout(() => {
        const messageContent = `<svg class="bot-avatar" xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 1024 1024">
                    <path 
                    d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 
                    47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 
                    41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9zM351.7 
                    448.2c0-29.5 23.9-53.5 53.5-53.5s53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5-53.5-23.9-53.5-53.5zm157.9 
                    267.1c-67.8 0-123.8-47.5-132.3-109h264.6c-8.6 61.5-64.5 109-132.3 109zm110-213.7c-29.5 0-53.5-23.9-53.5-53.5s23.9-53.5 
                    53.5-53.5 53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5zM867.2 644.5V453.1h26.5c19.4 0 35.1 15.7 35.1 35.1v121.1c0 19.4-15.7 
                    35.1-35.1 35.1h-26.5zM95.2 609.4V488.2c0-19.4 15.7-35.1 35.1-35.1h26.5v191.3h-26.5c-19.4 0-35.1-15.7-35.1-35.1zM561.5 149.6c0 
                    23.4-15.6 43.3-36.9 49.7v44.9h-30v-44.9c-21.4-6.5-36.9-26.3-36.9-49.7 0-28.6 23.3-51.9 51.9-51.9s51.9 23.3 51.9 51.9z"></path>
                </svg>
                <div class="message-text">
                    <div class="thinking-indicator">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                </div>`;

        const incomingMessageDiv = createMessageElement(messageContent, "bot-message", "thinking");
        chatBody.appendChild(incomingMessageDiv);
        
        // Scroll after DOM updates
       chatBody.scrollTo({top: chatBody.scrollHeight, behavior: "smooth"});
        
        // Send the message to the backend and process the response
        generateBotResponse(userData.message);
    }, 600);
}


// Handle enter key press for sending message
messageInput.addEventListener("keydown", (e) => {
    const userMessage = e.target.value.trim();
    if(e.key === "Enter" && userMessage && !e.shiftKey && window.innerWidth > 768) {
        handleOutGoingMessage(e);
    }
});

// Adjust input field height dynamically 
messageInput.addEventListener("input", () => {
    messageInput.style.height = `${initialInputHeight}px`;
    messageInput.style.height = `${messageInput.scrollHeight}px`;
    document.querySelector(".chat-form").style.borderRadius = messageInput.scrollHeight > initialInputHeight ? "15px" : "32px";
});

sendMessageButton.addEventListener("click", (e) => handleOutGoingMessage(e))
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
closeChatbot.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
