# Sistema de Gestión Bibliotecario

Este proyecto es un sistema de gestión bibliotecario desarrollado con Flask y SQLite, que permite administrar un catálogo de libros utilizando el Sistema Decimal Dewey.

## Características

- Catálogo completo de libros organizado según el Sistema Decimal Dewey
- Registro de información detallada de libros (título, autor, editorial, etc.)
- Control de disponibilidad de ejemplares
- Interfaz web fácil de usar para insertar y consultar libros

## Tecnologías utilizadas

- **Backend**: Flask (Python)
- **Base de datos**: SQLite
- **Frontend**: HTML, CSS, JavaScript

## Estructura de la base de datos

El sistema utiliza las siguientes tablas:
- `SistemaDewey`: Almacena las secciones de clasificación decimal Dewey
- `Libros`: Información básica de los libros
- `Autores`: Datos de los autores
- `Editoriales`: Registro de editoriales
- `Lugares`: Lugares de publicación
- `Notaciones`: Sistema de notación interna (basado en editorial o autor)
- `RegistroLibros`: Tabla que relaciona todas las anteriores

## Instalación y configuración

1. Clona este repositorio: `git clone https://github.com/tu-usuario/sistema-biblioteca.git`
2. Entra en el directorio del proyecto: `cd sistema-biblioteca`
3. Instala las dependencias: `pip install -r requirements.txt`
4. Inicia la aplicación: `flask run`
5. Accede a la aplicación en tu navegador: `http://localhost:5000`

## Uso

### Inserción de libros
Para insertar un nuevo libro en el sistema, navega a la sección "Insertar" y completa el formulario con los datos requeridos.

### Consulta de libros
Puedes buscar libros por título, autor, sección Dewey o disponibilidad desde la sección "Consultar".

## Contribuciones

Las contribuciones son bienvenidas. Si encuentras un error o tienes una sugerencia, no dudes en abrir un issue o enviar un pull request.

## Licencia
Todos los derechos reservados -Sergio Murcia -2025
