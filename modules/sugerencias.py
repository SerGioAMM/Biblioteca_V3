from flask import Blueprint, jsonify
from config import conexion_BD

bp_sugerencias = Blueprint('sugerencias',__name__)

# ----------------------------------------------------- SUGERENCIAS DINAMICAS ----------------------------------------------------- #

@bp_sugerencias.route("/sugerencias-lugares")
def sugerencias_lugares():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select Lugar from lugares")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-editoriales")
def sugerencias_editoriales():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select editorial from editoriales")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-libros")
def sugerencias_libros():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select titulo from libros")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-autores")
def sugerencias_autores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select DISTINCT (nombre_autor || ' ' || apellido_autor) as NombreCompleto from autores;")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-libros-prestamos")
def sugerencias_libros_prestamos():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select (titulo || '(' || ano_publicacion || ')') from libros where numero_copias > 0")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-prestamo")
def sugerencias_prestamo():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select l.titulo || ' (' || p.nombre || ' ' || p.apellido || ')' 
                    from prestamos p
                    join libros l on l.id_libro = p.id_libro;
                    """)
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-lectores")
def sugerencias_lector():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT (nombre || ' ' || apellido) from prestamos;""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-usuarios")
def sugerencias_usuarios():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select usuario from administradores")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-prestamo-eliminado-administradores")
def sugerencias_prestamo_eliminado_administradores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT a.usuario from administradores a
                    join prestamos_eliminados pe on a.id_administrador = pe.id_administrador""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-prestamo-eliminado-libro")
def sugerencias_prestamo_eliminado_libro():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT titulo from prestamos_eliminados""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-libro-eliminado-administradores")
def sugerencias_libro_eliminado_administradores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT a.usuario from administradores a
                    join libros_eliminados le on a.id_administrador = le.id_administrador""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@bp_sugerencias.route("/sugerencias-libro-eliminado")
def sugerencias_libro_eliminado():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT titulo from libros_eliminados""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])
