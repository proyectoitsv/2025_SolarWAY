const socket = io();

// Encendido individual
document.querySelectorAll(".led").forEach(led => {
    led.addEventListener("click", () => {
        socket.emit("toggle_led", {
            row: led.dataset.row,
            col: led.dataset.col
        });
    });
});

// Refrescar estados
socket.on("update_matrix", matrix => {
    document.querySelectorAll(".led").forEach(led => {
        const r = led.dataset.row;
        const c = led.dataset.col;

        if (matrix[r][c] === 1) led.classList.add("on");
        else led.classList.remove("on");
    });
});

// Botones encendido/apagado total
document.getElementById("btnOn").addEventListener("click", () => {
    socket.emit("set_all", 1);
});
document.getElementById("btnOff").addEventListener("click", () => {
    socket.emit("set_all", 0);
});

// Botones cancha
document.querySelectorAll(".sport-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        socket.emit("select_cancha", btn.dataset.cancha);
    });
});
