function toggleMenu() {
    const menuBtn = document.getElementById('menu-btn');
    const sideMenu = document.getElementById('sideMenu');

    // Toggle the "show" class to open/close the menu
    sideMenu.classList.toggle("show");

    // Close the menu when clicking outside
    document.addEventListener('click', function(event) {
        // Check if the click was outside the menu or menu button
        if (!sideMenu.contains(event.target) && !menuBtn.contains(event.target)) {
            sideMenu.classList.remove('show');  // Close the menu by removing 'show' class
        }
    });
}

function toggleForm() {
    var formSection = document.getElementById('createUserSection');
    formSection.classList.toggle('expanded');
}

// Show the fields based on user type selection
function showFields() {
    var userType = document.getElementById('user_type').value;
    
    // Hide all fields initially
    var dynamicFields = document.querySelectorAll('.dynamicFields');
    dynamicFields.forEach(function(field) {
        field.style.display = 'none';
    });

    // Show fields based on user type
    if (userType === 'student') {
        document.getElementById('studentFields').style.display = 'block';
    } else if (userType === 'advisor') {
        document.getElementById('advisorFields').style.display = 'block';
    } else if (userType === 'admin') {
        document.getElementById('adminFields').style.display = 'block';
    }
}