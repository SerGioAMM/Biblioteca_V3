from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
import math

from config import conexion_BD
from libros import bp_libros
from prestamos import bp_prestamos
from usuarios import bp_usuarios
from sugerencias import bp_sugerencias

app = Flask(__name__, template_folder="templates", static_folder="static")
app.register_blueprint(bp_libros)
app.register_blueprint(bp_prestamos)
app.register_blueprint(bp_usuarios)
app.register_blueprint(bp_sugerencias)

#! RECORDATORIO: Agregar el id_libro para mostrarlo en prestamos eliminados y en libros eliminados

# Esta clave se usa para la gestion de usuarios de flask -> "from flask import session"
app.secret_key = "234_Clav3-Ant1H4ck3r$_1"

# ----------------------------------------------------- PRINCIPAL ----------------------------------------------------- #

@app.route("/", methods=["GET"])
def inicio():
    session.clear()

    conexion = conexion_BD()
    query = conexion.cursor()
    
    query.execute("""select l.id_libro,count(l.id_libro) as cantidad, n.notacion, l.Titulo, a.nombre_autor, a.apellido_autor, l.ano_publicacion, sd.codigo_seccion, sd.seccion, l.numero_copias
                    from Prestamos p
					join libros l on p.id_libro = l.id_libro
                    join RegistroLibros r on r.id_libro = l.id_libro
                    join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
                    join notaciones n on n.id_notacion = r.id_notacion
                    join Autores a on a.id_autor = n.id_autor
                    group by p.id_libro
                    order by cantidad desc
                    limit 4;""")
    libros_destacados = query.fetchall()

    query.close()
    conexion.close()

    return render_template("index.html",libros_destacados=libros_destacados)

# ----------------------------------------------------- LOGOUT ----------------------------------------------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))

# ----------------------------------------------------- LOGIN ----------------------------------------------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    alerta= request.args.get("alerta", "")


    conexion = conexion_BD()
    query = conexion.cursor()
    
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        query.execute("""Select a.id_administrador,a.usuario,r.rol from Administradores a 
                    Join roles r on a.id_rol = r.id_rol
                    where usuario = ? and contrasena = ?""", (usuario, password))
        login_usuario = query.fetchone()

        if (login_usuario):
            # Guardar datos en session
            session["id_administrador"] = login_usuario[0] 
            session["usuario"] = login_usuario[1]
            session["rol"] = login_usuario[2]         

            return redirect(url_for('prestamos.prestamos'))
        else:
            alerta = "Datos incorrectos"
            session["rol"] = "false"

    query.close()
    conexion.close()

    return render_template("login.html", alerta = alerta)

# ----------------------------------------------------- ACERCA DE ----------------------------------------------------- #

@app.route("/acercade")
def acercade():

    return render_template('nosotros.html')

# ----------------------------------------------------- Descargar BD ----------------------------------------------------- #

@app.route('/descargar-bd')
def descargar_bd():
    if ("usuario" not in session) or (session["rol"]  != 'Administrador'):
        return redirect("/") #Solo se puede acceder con session iniciada

    return send_file('Data/Biblioteca_GM.db', as_attachment=True)

# ----------------------------------------------------- APP ----------------------------------------------------- #

if __name__ == "__main__":
    #app.run()
    app.run(debug=True,port=5000)
