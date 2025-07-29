
from flask import Blueprint, session, redirect, request,render_template,url_for
from datetime import datetime
import math
from config import conexion_BD

bp_prestamos = Blueprint('prestamos',__name__)

# ----------------------------------------------------- Verificar prestamos vencidos ----------------------------------------------------- #

def verificar_vencidos():
    conexion = conexion_BD()
    query = conexion.cursor()
    # Obtenre la fecha actual
    hoy = datetime.today().date()

    # Buscar prestamos para verificar si estan vencidos
    query.execute("""select id_prestamo, fecha_entrega_estimada
                    from Prestamos
                    where id_estado = 2""")  # Solo prestamos que esten activos (no revisaremos los que ya esten devueltos o vencidos)
    prestamos_para_verificar = query.fetchall()

    #Verifica que si existan prestamos activos
    if prestamos_para_verificar:
        # for para revisar cada prestamo
        for prestamo in prestamos_para_verificar:
            id_prestamo = prestamo[0]
            fecha_entrega_estimada = datetime.strptime(prestamo[1], "%Y-%m-%d").date()

            #Actualiza el estado de los prestamos a vencidos cuando se pasan dela fecha estimada de entrega
            if fecha_entrega_estimada < hoy:
                query.execute("""update Prestamos
                                set id_estado = 1
                                where id_prestamo = ?""", (id_prestamo,)) #Establece estado vencido
                conexion.commit()  # Guardamos los cambios

    query.close()
    conexion.close()

# ----------------------------------------------------- PRESTAMOS ----------------------------------------------------- #

@bp_prestamos.route("/prestamos",methods = ["GET","POST"])
def prestamos():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    estados = request.args.get("estados", "Todos")
    exito = request.args.get("exito","")
    devuelto = request.args.get("devuelto","")

    verificar_vencidos()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 7
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from prestamos")
    total_prestamos = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos / prestamos_por_pagina)

    # Consulta para mostrar los prestamos en tarjetas de prestamos.html
    query.execute(f"""select strftime('%d-%m-%Y', p.fecha_prestamo), strftime('%d-%m-%Y', p.fecha_entrega_estimada), strftime('%d-%m-%Y', p.fecha_devolucion), l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, e.estado, p.id_prestamo, l.id_libro
                    from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados e on p.id_estado = e.id_estado
                  order by e.id_estado asc, p.fecha_prestamo desc
                  limit ? offset ?""",(prestamos_por_pagina,offset))
    prestamos = query.fetchall()
    
    query.execute("Select Count(*) from prestamos where id_estado = 1") #Prestamos vencidos
    prestamos_vencidos = query.fetchone()[0]

    query.execute("Select Count(*) from prestamos where id_estado = 2") #Prestamos activos
    prestamos_activos = query.fetchone()[0]

    query.execute("Select Count(*) from prestamos where id_estado = 3") #Prestamos devueltos
    prestamos_devueltos = query.fetchone()[0]

    query.close()
    conexion.close()

    return render_template("prestamos.html",prestamos=prestamos,estados=estados,pagina=pagina,total_paginas=total_paginas,
                           prestamos_activos=prestamos_activos,prestamos_devueltos=prestamos_devueltos,prestamos_vencidos=prestamos_vencidos,
                           exito = exito, devuelto = devuelto)

# ----------------------------------------------------- BUSCAR Prestamo ----------------------------------------------------- #

@bp_prestamos.route("/buscar_prestamo", methods = ["GET"])
def buscar_prestamo():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar_prestamo","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")
    estados = request.args.get("estados","Todos")
    exito = request.args.get("exito","")
    devuelto = request.args.get("devuelto","")

    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f" where l.titulo || ' (' || p.nombre || ' ' || p.apellido || ')' like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f" where p.nombre || ' ' || p.apellido like '%{busqueda}%'")
    
    if estados == "Todos":
        SQL_where_estado =" "
    else:
        SQL_where_estado = (f" and e.id_estado = {estados}")

    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 7
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los libros conforme a la busqueda
    query.execute(f"""select count(*) from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados e on p.id_estado = e.id_estado 
                    {SQL_where_busqueda}{SQL_where_estado}""")
    
    total_prestamos = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos / prestamos_por_pagina) #Calculo para cantidad de paginas, redondeando hacia arriba (ej, 2.1 = 3)

    query_busqueda = (f"""select strftime('%d-%m-%Y', p.fecha_prestamo), strftime('%d-%m-%Y', p.fecha_entrega_estimada), strftime('%d-%m-%Y', p.fecha_devolucion), l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, e.estado, p.id_prestamo,l.id_libro
                    from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados e on p.id_estado = e.id_estado 
                    {SQL_where_busqueda}{SQL_where_estado}
                    order by e.id_estado asc, p.fecha_prestamo desc
                    limit {prestamos_por_pagina} offset {offset}""")

    query.execute("Select Count(*) from prestamos where id_estado = 1") #Prestamos vencidos
    prestamos_vencidos = query.fetchone()[0]

    query.execute("Select Count(*) from prestamos where id_estado = 2") #Prestamos activos
    prestamos_activos = query.fetchone()[0]

    query.execute("Select Count(*) from prestamos where id_estado = 3") #Prestamos devueltos
    prestamos_devueltos = query.fetchone()[0]

    query.execute(query_busqueda)
    prestamos = query.fetchall()

    query.close()
    conexion.close()

    return render_template("prestamos.html",prestamos=prestamos,estados=estados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda,
                           prestamos_activos=prestamos_activos,prestamos_devueltos=prestamos_devueltos,prestamos_vencidos=prestamos_vencidos,
                           exito = exito, devuelto = devuelto)

# ----------------------------------------------------- Devolver Prestamo ----------------------------------------------------- #

@bp_prestamos.route("/devolver_prestamo", methods=["POST"])
def devolver_prestamo():
    id_prestamo = request.form["id_prestamo"]

    # Obtenre la fecha actual
    hoy = datetime.today().date()

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("update prestamos set fecha_devolucion = (?) where id_prestamo = (?)",(hoy,id_prestamo,))

    #Pone el prestamo en estado 3 (devuelto)
    query.execute("update prestamos set id_estado = 3 where id_prestamo = (?)",(id_prestamo,))

    query.execute("select id_libro from prestamos where id_prestamo = ?",(id_prestamo,))
    id_libro = query.fetchone()[0]

    query.execute("update libros set numero_copias = (numero_copias + 1) where id_libro = ?",(id_libro,))
    conexion.commit() #Guarda la actualizacion de estado del prestamo

    query.close()
    conexion.close()

    devuelto = "Libro devuelto exitósamente."

    return redirect(url_for("prestamos",devuelto=devuelto))

# ----------------------------------------------------- Eliminar Prestamo ----------------------------------------------------- #

@bp_prestamos.route("/eliminar_prestamo", methods=["GET", "POST"])
def eliminar_prestamo():
    #! RECORDATORIO: Agregar el id_libro para mostrarlo en prestamos eliminados y en libros eliminados
    id_prestamo = request.form["id_prestamo"]
    motivo = request.form["motivo"]

    # Obtenre la fecha actual
    hoy = datetime.today().date()
    id_administrador = session.get("id_administrador")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select (nombre || ' ' || apellido) from prestamos where id_prestamo = ?",(id_prestamo,))
    lector = query.fetchone()[0]

    query.execute("select l.titulo from libros l join prestamos p on l.id_libro = p.id_libro where p.id_prestamo = ?",(id_prestamo,))
    libro = query.fetchone()[0]

    query.execute("insert into prestamos_eliminados(id_administrador,id_prestamo,fecha,nombre_lector,titulo,motivo) values(?,?,?,?,?,?)",(id_administrador,id_prestamo,hoy,lector,libro,motivo))

    query.execute("delete from prestamos where id_prestamo = ?",(id_prestamo,))
    conexion.commit()

    query.close()
    conexion.close()

    exito = "Préstamo eliminado exitósamente."

    return redirect(url_for("prestamos",exito=exito))

# ----------------------------------------------------- REGISTRO PRESTAMOS ----------------------------------------------------- #

@bp_prestamos.route("/registro_prestamos", methods=["GET", "POST"])
def registro_prestamos():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

        #Verifica la accion que realiza el formulario en registro-prestamos.html
    if request.method == "POST":
        #Obtiene los datos del formulario en registro-prestamos.html
        DPI = request.form["DPI"]
        NombreLector = request.form["nombre_lector"]
        ApellidoLector = request.form["apellido_lector"]
        Direccion = request.form["direccion"]
        Telefono = request.form["num_telefono"]
        Libro = request.form["libro"]
        GradoEstudio = request.form["grado"]
        fecha_prestamo = request.form["fecha_prestamo"]
        fecha_entrega_estimada = request.form["fecha_entrega_estimada"]
        Estado = 2 #Activo
            
        try:
            # Verificar si el libro existe y tiene al menos 1 copia
            query.execute("select id_libro, numero_copias from Libros where (titulo || '(' || ano_publicacion || ')') = ?", (Libro,))
            libro_data = query.fetchone()

            if libro_data is None:
                # El libro no existe
                alerta = "El libro no existe."
                return render_template("registro_prestamos.html", alerta=alerta,
                       DPI=DPI, nombre_lector=NombreLector, apellido_lector=ApellidoLector,
                       direccion=Direccion, num_telefono=Telefono, libro=Libro,
                       grado=GradoEstudio, fecha_prestamo=fecha_prestamo,
                       fecha_entrega_estimada=fecha_entrega_estimada)


            id_libro, numero_copias = libro_data

            if numero_copias < 1:
                # No hay copias disponibles
                alerta = "No hay copias disponibles de este libro"
                return render_template("registro_prestamos.html", alerta=alerta,
                       DPI=DPI, nombre_lector=NombreLector, apellido_lector=ApellidoLector,
                       direccion=Direccion, num_telefono=Telefono, libro=Libro,
                       grado=GradoEstudio, fecha_prestamo=fecha_prestamo,
                       fecha_entrega_estimada=fecha_entrega_estimada)
            
            #? INSERT DE PRESTAMOS
            query.execute(f"""Insert into Prestamos
                          (dpi_usuario,nombre,apellido,direccion,num_telefono,id_libro,grado,id_estado,fecha_prestamo,fecha_entrega_estimada,fecha_devolucion)
                          values (?,?,?,?,?,?,?,?,?,?,NULL)""",
                          (DPI,NombreLector,ApellidoLector,Direccion,Telefono,id_libro,GradoEstudio,Estado,fecha_prestamo,fecha_entrega_estimada))

            query.execute(f"update Libros set numero_copias = (numero_copias-1) where id_libro = ?",(id_libro,))

            #? Guardar cambios
            conexion.commit()  

            registro_exitoso = "Préstamo registrado exitósamente."

            return render_template("registro_prestamos.html", registro_exitoso=registro_exitoso)
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            query.close()
            conexion.close()


    return render_template("registro_prestamos.html")

# ----------------------------------------------------- Prestamos Eliminados ----------------------------------------------------- #

@bp_prestamos.route("/prestamos_eliminados",methods = ["POST","GET"])
def prestamos_eliminados():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 10
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from prestamos_eliminados")
    total_prestamos = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos / prestamos_por_pagina)
    
    _query = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', pe.fecha),pe.nombre_lector,pe.titulo,pe.motivo from prestamos_eliminados pe
                        join Administradores a on pe.id_administrador = a.id_administrador
                        join roles r on a.id_rol =  r.id_rol
                        order by pe.fecha desc
                        limit {prestamos_por_pagina} offset {offset}""")

    query.execute(_query)
    prestamos_eliminados = query.fetchall()

    query.close()
    conexion.close()


    return render_template("prestamos_eliminados.html",prestamos_eliminados=prestamos_eliminados,pagina=pagina,total_paginas=total_paginas)


# ----------------------------------------------------- BUSCAR Prestamo Eliminado ----------------------------------------------------- #

@bp_prestamos.route("/buscar_prestamo_eliminado", methods = ["GET"])
def buscar_prestamo_eliminado():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar_prestamo_eliminado","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")

    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f" where pe.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f" where a.usuario = '{busqueda}'")

    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    prestamos_por_pagina = 10
    offset = (pagina - 1) * prestamos_por_pagina

    # Consulta para contar todos los prestamos conforme a la busqueda
    query.execute(f"""select count(*) from prestamos_eliminados pe
                        join administradores a on pe.id_administrador = a.id_administrador
                        {SQL_where_busqueda}""")
    total_prestamos_eliminados = query.fetchone()[0]
    total_paginas = math.ceil(total_prestamos_eliminados / prestamos_por_pagina) #Calculo para cantidad de paginas, redondeando hacia arriba (ej, 2.1 = 3)

    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', pe.fecha),pe.nombre_lector,pe.titulo,pe.motivo from prestamos_eliminados pe
                            join Administradores a on pe.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            {SQL_where_busqueda}
                            order by pe.fecha desc
                            limit {prestamos_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    prestamos_eliminados = query.fetchall()

    query.close()
    conexion.close()

    return render_template("prestamos_eliminados.html",prestamos_eliminados=prestamos_eliminados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


