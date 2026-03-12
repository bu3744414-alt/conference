

function openAvailability(){

    document.getElementById("dashboardPanel").style.display="none";
    document.getElementById("myBookingsPanel").style.display="none";
    document.getElementById("adminBookingsPanel").style.display="none";

    document.getElementById("availabilityPanel").style.display="block";

    loadHallCards();
}


async function loadHallCards(){

    const res = await fetch("/hall_stats");
    const halls = await res.json();

    const container = document.getElementById("hallCards");
    container.innerHTML = "";

    Object.keys(halls).forEach(hall => {

        const card = document.createElement("div");
        card.className = "availability-card";
        card.innerHTML = `<b>${hall}</b>`;
        card.onclick = () => loadSlots(hall)

        container.appendChild(card);
    });
}



async function loadSlots(hall){

    const today = new Date().toISOString().split('T')[0];

    const res = await fetch(`/availability?hall=${hall}&date=${today}`);
    const slots = await res.json();

    const box = document.getElementById("slotDetails");

    let html = `<h3 style="margin-top:20px">${hallNames[hall] || hall}</h3>`;

    // office hours
    let startDay = 9 * 60;   // 09:00
    let endDay   = 18 * 60;  // 18:00

    function toMinutes(t){
        let [h,m] = t.split(":").map(Number);
        return h*60+m;
    }

    function toTime(m){
        let h = Math.floor(m/60);
        let min = m%60;
        return `${String(h).padStart(2,'0')}:${String(min).padStart(2,'0')}`;
    }

    if(slots.length === 0){
        html += `<div class="free-card">Fully Available</div>`;
    } else {

        let lastEnd = startDay;

        html += `<div class="slot-row">`;

        slots.forEach(slot => {

            let s = toMinutes(slot[0]);
            let e = toMinutes(slot[1]);

            // show free time before booking
            if(s > lastEnd){
                html += `
                <div class="free-card">
                    Available<br>
                    ${toTime(lastEnd)} - ${toTime(s)}
                </div>`;
            }

            // booked slot
            html += `
            <div class="busy-card">
                <b>${slot[2]}</b><br>
                ${slot[0]} - ${slot[1]}<br>
                <small>${slot[3]}</small>
            </div>`;

            lastEnd = e;
        });

        // free time after last booking
        if(lastEnd < endDay){
            html += `
            <div class="free-card">
                Available<br>
                ${toTime(lastEnd)} - ${toTime(endDay)}
            </div>`;
        }

        html += `</div>`;
    }

    box.innerHTML = html;
}

const hallNames = {
    "101": "First Floor Conference",
    "102": "First Floor Conference Small",
    "201": "Second Floor Conference",
    "301": "Third Floor Conference",
    "401": "Fourth Floor Conference"
};
