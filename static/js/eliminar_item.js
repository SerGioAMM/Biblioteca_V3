const botones_eliminar = document.querySelectorAll('.btn-eliminacion');
const botones_cancelar = document.querySelectorAll('.btn-cancelar-eliminacion');

// Mostrar motivo al hacer clic en "Eliminar"
botones_eliminar.forEach((boton) => {
    boton.addEventListener("click", () => {
        const contenedor = boton.closest('.frm-eliminar-libro, .frm-eliminar-prestamo').querySelector('.motivo_eliminacion');
        contenedor.classList.add("mostrar_motivo");
    });
});

// Ocultar motivo al hacer clic en "Cancelar"
botones_cancelar.forEach((boton) => {
    boton.addEventListener("click", () => {
        const contenedor = boton.closest('.frm-eliminar-libro, .frm-eliminar-prestamo').querySelector('.motivo_eliminacion');
        contenedor.classList.remove("mostrar_motivo");
    });
});

// Ocultar motivo si se hace clic fuera del formulario
document.addEventListener("click", (e) => {
    document.querySelectorAll('.frm-eliminar-libro, .frm-eliminar-prestamo').forEach(form => {
        const contenedorMotivo = form.querySelector('.motivo_eliminacion');

        if (!form.contains(e.target)) {
            contenedorMotivo.classList.remove("mostrar_motivo");
        }
    });
});


