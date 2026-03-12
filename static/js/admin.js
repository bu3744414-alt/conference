


async function loadAdminBookings(){
    document.getElementById("dashboardPanel").style.display="none";
    document.getElementById("availabilityPanel").style.display="none";
    document.getElementById("myBookingsPanel").style.display="none";
    document.getElementById("adminBookingsPanel").style.display="block";

    const date = document.getElementById("adminBookingDate").value;

    let url = "/admin_bookings";

    if(date){
        url += "?date=" + date;
    }

    

    const res = await fetch(url);
    const bookings = await res.json();

    const box = document.getElementById("adminBookingsList");
    box.innerHTML = "";

    if(bookings.length === 0){
        box.innerHTML = "<p>No bookings found</p>";
        return;
    }

    bookings.forEach(b => {
        
        
        const statusText = b.rescheduled == 1 ? "Rescheduled" : b.status;   
        const reasonText = b.rescheduled == 1 ? "Reschedule Reason" : "Purpose";

        const today = new Date().toISOString().split('T')[0];

        let cancelBtn = "";

        if(b.date >= today && b.status === "Booked"){
            cancelBtn = `
            <button class="cancel-btn" onclick="openCancel(${b.id})">
                Cancel
            </button>`;
        }
        
        // ⭐ Decide what text to show
        // ⭐ cancellation reason
    let cancelReasonText = "";

    if(b.status === "Cancelled" && b.cancel_reason){
        cancelReasonText = `
        <br>
        <small>Cancellation Reason: ${b.cancel_reason}</small>
        `;
    }

    let deptText = "";

    if(b.user_dept === "Admin"){
        deptText = `
        <small>Booked for: ${b.department}</small>
        <br>
        <small>Booked by: ${b.user} (ADMIN)</small>
        `;
    }
    else{
        deptText = `
        <small>Department: ${b.department}</small>
        <br>
        <small>Booked by: ${b.user}</small>
        `;
    }

        box.innerHTML += `
        <div class="booking-card">

            <div class="booking-left">
                ${b.hall}
                <br>
                ${deptText}
                <br>
                
                <small>${reasonText}: ${b.purpose}</small>
                ${cancelReasonText}
            </div>

            <div class="booking-middle">
                Date: ${b.date}<br>
                Time: ${b.start} - ${b.end}
            </div>

            <div class="booking-status ${statusText.toLowerCase()}">
                ${statusText}
            </div>

            <div class="booking-actions">
                ${cancelBtn}
            </div>

        </div>`;
    });
}


/* Cancel Booking  */
async function confirmCancel(){

    const reason = document.getElementById("cancelReason").value.trim();

    if(!reason){
        showPopup("Error","Please enter cancellation reason");
        return;
    }

    const fd = new FormData();
    fd.append("reason", reason);

    const res = await fetch(`/cancel/${cancelBookingId}`, {
        method: "POST",
        body: fd
    });

    const data = await res.json();

    showPopup("Cancelled", data.message);

    closeCancel();

    loadAdminBookings();   // reload admin bookings
}


let cancelBookingId = null;

function openCancel(id){
    cancelBookingId = id;
    document.getElementById("cancelReason").value = "";
    document.getElementById("cancelModal").style.display = "flex";
}

function closeCancel(){
    document.getElementById("cancelModal").style.display = "none";
}




async function addHall(){
    const name = document.getElementById("newHallName").value;
    if(!name) return alert("Enter hall name");

    const fd = new FormData();
    fd.append("name", name);

    await fetch("/add_hall", { method:"POST", body:fd });

    loadHalls();
}

async function deleteHall(name){
    const fd = new FormData();
    fd.append("name", name);

    await fetch("/delete_hall", { method:"POST", body:fd });

    loadHalls();
}

/* SETTINGS PANEL */
function openSettings(){
    document.getElementById("settingsModal").style.display = "flex";
}

function closeSettings(){
    document.getElementById("settingsModal").style.display = "none";
}


function openExport(){
    document.getElementById("exportModal").style.display = "flex";
}

function closeExport(){
    document.getElementById("exportModal").style.display = "none";
}


/* EXPORTBOOKINGS  */
async function exportReport(){

    const start = document.getElementById("exportStart").value;
    const end = document.getElementById("exportEnd").value;

    if(!start || !end){
        showPopup("Error", "Please select both dates");
        return;
    }

    const fd = new FormData();
    fd.append("start_date", start);
    fd.append("end_date", end);

    const res = await fetch("/export_excel", {
        method: "POST",
        body: fd
    });

    const blob = await res.blob();

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "bookings.xlsx";
    a.click();

    closeExport();
}


function openRenameModal(){
    document.getElementById("renameModal").style.display = "flex";
    loadHalls();
}

function closeRenameModal(){
    document.getElementById("renameModal").style.display = "none";
}

async function loadHalls(){

    const res = await fetch("/hall_stats");
    const halls = await res.json();

    const list = document.getElementById("hallList");
    list.innerHTML = "";

    Object.keys(halls).forEach(hall => {

        list.innerHTML += `
        <div class="hall-row">
            <span class="hall-name">${hall}</span>
            <button class="delete-btn" onclick="deleteHall('${hall}')">
                Delete
            </button>
        </div>`;
    });

}