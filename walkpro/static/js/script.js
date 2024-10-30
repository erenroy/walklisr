<div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999;">
<button class="toggle-btns" onclick="closeNav()" style="
    margin: 5px; 
    background-color: rgb(43, 68, 124); 
    color: white; 
    border: none; 
    border-radius: 5px; 
    padding: 10px 15px; 
    font-size: 16px; 
    cursor: pointer; 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transition: background-color 0.3s, transform 0.3s;">
    &#8592; Close
</button>
<button class="toggle-btns" onclick="openNav()" style="
    margin: 5px; 
    background-color: rgb(43, 68, 124); 
    color: white; 
    border: none; 
    border-radius: 5px; 
    padding: 10px 15px; 
    font-size: 16px; 
    cursor: pointer; 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transition: background-color 0.3s, transform 0.3s;">
    Open &#8594;
</button>
</div>



function openNav() {
    document.getElementById("mySidebar").style.width = "300px";
    document.getElementById("main").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
}

function toggleDropdown() {
    var dropdown = document.getElementById("dropdown");
    if (dropdown.style.display === "block") {
        dropdown.style.display = "none"; // Hide the dropdown if it's already visible
    } else {
        dropdown.style.display = "block"; // Show the dropdown
    }
}

function checkScreenWidth() {
    if (window.innerWidth < 700) {
        closeNav(); // Close the sidebar if screen width is less than 700px
    }
}

// Add event listener for window resize
window.addEventListener('resize', checkScreenWidth);

// Initial check when the page loads
document.addEventListener('DOMContentLoaded', checkScreenWidth);

