

document.addEventListener("DOMContentLoaded", () => {

    const today = new Date().toISOString().split('T')[0];

    const myDate = document.getElementById("myBookingDate");
    const adminDate = document.getElementById("adminBookingDate");

    if(myDate) myDate.value = today;
    if(adminDate) adminDate.value = today;

});


function showDashboard(){

    document.getElementById("dashboardPanel").style.display="block";

    document.getElementById("availabilityPanel").style.display="none";
    document.getElementById("myBookingsPanel").style.display="none";
    document.getElementById("adminBookingsPanel").style.display="none";
}


function toggleUserMenu(){
    const menu = document.getElementById("userMenu");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function showPopup(title, message){
    document.getElementById("popupTitle").innerText = title;
    document.getElementById("popupMessage").innerText = message;
    document.getElementById("popupOverlay").style.display = "flex";
}

function closePopup(){
    document.getElementById("popupOverlay").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {

    const today = new Date().toISOString().split('T')[0];

    const bookingDate = document.getElementById("bookingDate");
    const myBookingDate = document.getElementById("myBookingDate");
    const adminBookingDate = document.getElementById("adminBookingDate");
    const resDate = document.getElementById("resDate");
    const exportStart = document.getElementById("exportStart");
    const exportEnd = document.getElementById("exportEnd");

    const startTime = document.getElementById("startTime");
    const endTime = document.getElementById("endTime");

    if (bookingDate) {
        bookingDate.value = today;
        bookingDate.min = today;
    }

    if (myBookingDate) myBookingDate.value = today;
    if (adminBookingDate) adminBookingDate.value = today;

    if (resDate) {
        resDate.value = today;
        resDate.min = today;
    }

    if (exportStart) exportStart.value = today;
    if (exportEnd) exportEnd.value = today;

    if (startTime) startTime.value = "09:00";
    if (endTime) endTime.value = "18:00";

});

document.addEventListener("DOMContentLoaded", function () {

    const today = new Date().toISOString().split('T')[0];

    const dateInput = document.getElementById("bookingDate");
    const startInput = document.getElementById("startTime");
    const endInput = document.getElementById("endTime");

    const resDate = document.getElementById("resDate");

    if(resDate){
        resDate.value = today;
        resDate.min = today;
    }

    if (dateInput) {
        dateInput.value = today;
        dateInput.min = today;
    }

    if (startInput) startInput.value = "09:00";
    if (endInput) endInput.value = "18:00";

});


function showDashboard(){

    document.getElementById("dashboardPanel").style.display="block";

    document.getElementById("availabilityPanel").style.display="none";
    document.getElementById("myBookingsPanel").style.display="none";
    document.getElementById("adminBookingsPanel").style.display="none";
}

function toggleUserMenu(){
    const menu = document.getElementById("userMenu");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

/* POPUP */
function showPopup(title, message){
    document.getElementById("popupTitle").innerText = title;
    document.getElementById("popupMessage").innerText = message;
    document.getElementById("popupOverlay").style.display = "flex";
}

function closePopup(){
    document.getElementById("popupOverlay").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("myBookingDate").value =
        new Date().toISOString().split('T')[0];
});

document.addEventListener("DOMContentLoaded", () => {

    const today = new Date().toISOString().split('T')[0];

    const start = document.getElementById("exportStart");
    const end = document.getElementById("exportEnd");

    if(start) start.value = today;
    if(end) end.value = today;

});