async function actualizarEstado() {
    const res = await fetch('/api/estado');
    const data = await res.json();
    document.getElementById("energia").textContent = data.energia;
    document.getElementById("modo").textContent = data.modo;
    document.getElementById("fallas").textContent = data.fallas;
}

async function enviarAccion(accion) {
    await fetch('/api/control', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({accion})
    });
}

function cambiarCancha() {
    const tipo = document.getElementById('tipoCancha').value;
    enviarAccion(`modo_${tipo}`);
}

setInterval(actualizarEstado, 2000);
