const caja_sugerencias = document.querySelector('.ul-contenedor-sugerencias');
let inputActivo = null;

function moverSugerencias(input) {
  caja_sugerencias.style.top = (input.offsetTop + input.offsetHeight - 10) + 'px';
  caja_sugerencias.style.left = input.offsetLeft + 'px';
  caja_sugerencias.style.width = input.offsetWidth + 'px';
}

function mostrar_sugerencias(lista) {
  if (lista.length === 0) {
    caja_sugerencias.classList.remove('activar');
    caja_sugerencias.innerHTML = '';
  } else {
    caja_sugerencias.innerHTML = lista.join('');
    caja_sugerencias.classList.add('activar');
  }
}

function seleccionar_Sugerencia(sug) {
  if (inputActivo) inputActivo.value = sug;
  caja_sugerencias.classList.remove('activar');
  caja_sugerencias.innerHTML = '';
}

document.querySelectorAll('.input-lugar, .input-editorial').forEach(input => {
  input.addEventListener('focus', () => {
    inputActivo = input;
    moverSugerencias(input);

    caja_sugerencias.classList.remove('activar');
    caja_sugerencias.innerHTML = '';
  });

  input.addEventListener('keyup', (e) => {
    const texto = e.target.value.toLowerCase();
    if (!texto) {
      caja_sugerencias.innerHTML = '';
      caja_sugerencias.classList.remove('activar');
      return;
    }

    // Detectar el input
    let endpoint = '';
    if (input.classList.contains('input-lugar')) {
      endpoint = '/sugerencias-lugares';
    } else if (input.classList.contains('input-editorial')) {
      endpoint = '/sugerencias-editoriales';
    } 
    /*else if (input.classList.contains('input-autor')) {
      endpoint = '/sugerencias-autores';
    }*/

    fetch(endpoint)
      .then(r => r.json())
      .then(data => {
        const sugerencias = data
          .filter(d => d.toLowerCase().startsWith(texto))
          .map(s => `<li onclick="seleccionar_Sugerencia('${s}')">${s}</li>`);

        mostrar_sugerencias(sugerencias);
      });
  });
});


