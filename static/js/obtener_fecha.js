// Obtener la fecha de hoy
const hoy = new Date();
const yyyy = hoy.getFullYear();
const mm = String(hoy.getMonth() + 1).padStart(2, '0'); // los meses van de 0 a 11
const dd = String(hoy.getDate()).padStart(2, '0');
const fechaHoy = `${yyyy}-${mm}-${dd}`;

// Obtener la fecha dentro de 7 dias
const sieteDias = new Date(hoy);
sieteDias.setDate(hoy.getDate() + 7);
const yyyy7 = sieteDias.getFullYear();
const mm7 = String(sieteDias.getMonth() + 1).padStart(2, '0');
const dd7 = String(sieteDias.getDate()).padStart(2, '0');
const fechaSiete = `${yyyy7}-${mm7}-${dd7}`;



document.getElementById('fecha_prestamo').value = fechaHoy;
document.getElementById('fecha_entrega_estimada').value = fechaSiete;