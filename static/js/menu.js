const menu = document.querySelector(".barra-lateral");
const abrir = document.querySelector(".boton-lateral");
const cerrar = document.querySelector(".boton-lateral-cerrar");

abrir.addEventListener("click", () => {
    menu.classList.add("barra-lateral-visible");
    cerrar.classList.add("boton-lateral-visible");
})

cerrar.addEventListener("click", () => {
    menu.classList.remove("barra-lateral-visible");
    cerrar.classList.remove("boton-lateral-visible");
})