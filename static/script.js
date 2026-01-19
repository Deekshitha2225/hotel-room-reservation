async function loadRooms(selectedRooms = []) {
    const res = await fetch('/rooms');
    const rooms = await res.json();

    const floorsDiv = document.getElementById("floors");
    floorsDiv.innerHTML = "";

    const floorMap = {};

    rooms.forEach(room => {
        if (!floorMap[room.floor]) floorMap[room.floor] = [];
        floorMap[room.floor].push(room);
    });

    Object.keys(floorMap).sort((a, b) => a - b).forEach(floor => {
        const floorDiv = document.createElement("div");
        floorDiv.className = "floor";

        const label = document.createElement("div");
        label.className = "floor-label";
        label.innerText = "Floor " + floor;
        floorDiv.appendChild(label);

        floorMap[floor].sort((a, b) => a.position - b.position);

        floorMap[floor].forEach(room => {
            const div = document.createElement("div");
            div.className = "room " + (room.booked ? "booked" : "available");

            if (selectedRooms.includes(room.number)) {
                div.classList.add("selected");
            }

            div.innerText = room.number;
            floorDiv.appendChild(div);
        });

        floorsDiv.appendChild(floorDiv);
    });
}

async function resetRooms() {
    await fetch('/reset', { method: "POST" });
    document.getElementById("info").innerHTML = "";
    loadRooms();
}

async function randomRooms() {
    await fetch('/random', { method: "POST" });
    document.getElementById("info").innerHTML = "";
    loadRooms();
}

async function bookRooms() {
    const count = document.getElementById("roomCount").value;

    if (!count || count < 1 || count > 5) {
        alert("Enter a number between 1 and 5");
        return;
    }

    const res = await fetch('/book', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count })
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
    } else {
        const selectedNumbers = data.rooms.map(r => r.number);
        loadRooms(selectedNumbers);

        document.getElementById("info").innerHTML = `
            <b>Rule Used:</b> ${data.rule} <br>
            <b>Total Travel Time:</b> ${data.travel_time} minutes <br>
            <b>Rooms:</b> ${selectedNumbers.join(", ")}
        `;
    }
}

loadRooms();
