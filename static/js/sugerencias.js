const input_lugar = document.querySelector('.input-lugar');
const caja_sugerencias = document.querySelector('.ul-contenedor-sugerencias');

/* Captura los datos del usuario (INPUT-LUGAR) */
input_lugar.onkeyup = (e) => {
  let datos_ingresados = e.target.value.toLocaleLowerCase();

  if (datos_ingresados) {
    fetch("/sugerencias")
      .then(response => response.json())
      .then(lugares => {
        // Limpiar sugerencias anteriores
        caja_sugerencias.innerHTML = "";

        // Filtrar
        let filtrados = lugares.filter(lugar =>
          lugar.toLowerCase().startsWith(datos_ingresados)
        );
        
        filtrados = filtrados.map(sugerencia => `<li onclick="seleccionar_Sugerencia('${sugerencia}')">${sugerencia}</li>`);

        // Mostrar sugerencias
        caja_sugerencias.classList.add('activar');
        mostrar_sugerencias(filtrados);

        /*
        filtrados.forEach(lugar => {
          let li = document.createElement("li");
          li.textContent = lugar.Lugar;
          li.classList.add("sugerencia-item"); // Para estilos si querés
          caja_sugerencias.appendChild(li);

          //! Opcional: al hacer clic en una sugerencia, la pone en el input
          li.onclick = () => {
            input_lugar.value = lugar;
            caja_sugerencias.innerHTML = "";
          };
        }); */

      })
      .catch(error => console.error("Error al obtener sugerencias:", error));
  } 
  else {
    // Limpia sugerencias si el input está vacío
    caja_sugerencias.innerHTML = ""; 
  }
};

const mostrar_sugerencias = list => {
  let datos_busqueda;

  if(!list.length){
    datos_ingresados = input_lugar.value;
    datos_busqueda = `<li>${datos_ingresados}</li>`;
  }
  else{
    datos_busqueda = list.join(' ');
  }
  caja_sugerencias.innerHTML = datos_busqueda;

}

function seleccionar_Sugerencia(sug) {
  input_lugar.value = sug;
  caja_sugerencias.innerHTML = "";
}

