from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from config import conexion_BD

bp_usuarios = Blueprint('usuarios',__name__)

# ----------------------------------------------------- REGISTRO USUARIOS ----------------------------------------------------- #

@bp_usuarios.route("/registrar_usuarios", methods=["GET", "POST"])
def registrar_usuarios():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("Select * from roles")
    roles = query.fetchall()

    #Verifica la accion que realiza el formulario en registro_usuairos.html
    if request.method == "POST":
        #Obtiene los datos del formulario en registro-usuarios.html
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]
        telefono = request.form["telefono"]
        rol = request.form["rol"]
  
        try:
            #? INSERT DE USUARIOS
            query.execute(f"""Insert into Administradores(usuario,contrasena,telefono,id_rol)
                          values (?,?,?,?)""",(usuario,contrasena,telefono,rol))

            #? Guardar cambios
            conexion.commit()  
            
            registro_exitoso = "El usuario se registró exitósamente."
            return render_template("registro_usuarios.html",roles=roles,registro_exitoso=registro_exitoso)
            

        except Exception as e:
            print(f"Error: {e}")
            alerta = "Error al ingresar el nuevo usuario"
            return render_template("registro_usuarios.html",roles=roles,alerta=alerta)
        finally:
            query.close()
            conexion.close()


    return render_template("registro_usuarios.html",roles=roles)

# ----------------------------------------------------- USUARIOS ----------------------------------------------------- #

@bp_usuarios.route("/usuarios",methods = ["POST","GET"])
def usuarios():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    exito = request.args.get("exito","")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""Select a.id_rol,r.rol,a.usuario,a.contrasena,a.telefono,a.id_administrador from administradores a
                    join roles r on a.id_rol = r.id_rol""")
    usuarios = query.fetchall()

    query.close()
    conexion.close()

    return render_template("usuarios.html",usuarios = usuarios,exito=exito)

# ----------------------------------------------------- Eliminar USUARIO ----------------------------------------------------- #

@bp_usuarios.route("/eliminar_usuario", methods=["GET", "POST"])
def eliminar_usuario():
    id_usuario = request.form["id_usuario"]

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("delete from administradores where id_administrador = ?",(id_usuario,))
    conexion.commit()

    query.close()
    conexion.close()

    exito = "Usuario eliminado exiósamente."

    return redirect(url_for("usuarios.usuarios",exito=exito))

# ----------------------------------------------------- BUSCAR Usuarios ----------------------------------------------------- #

@bp_usuarios.route("/buscar_usuario",methods = ["POST"])
def buscar_usuario():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    exito = request.args.get("exito","")
    
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.form["buscar_usuario"]
    #Obtiene los datos del formulario filtros en usuarios.html
    filtro_rol = request.form["filtro-busqueda"]
    
    if filtro_rol != "Todos":
        SQL_where_rol = (f"and r.rol = '{filtro_rol}'")
    else:
        SQL_where_rol = " "

    query_busqueda = (f"""Select a.id_rol,r.rol,a.usuario,a.contrasena,a.telefono,a.id_administrador from administradores a
                    join roles r on a.id_rol = r.id_rol
                    where a.usuario like '%{busqueda}%' """)

    query_busqueda = query_busqueda + SQL_where_rol

    query.execute(query_busqueda)
    usuarios = query.fetchall()

    query.close()
    conexion.close()


    return render_template("usuarios.html",usuarios=usuarios,exito=exito)
