from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
from datetime import datetime
import math
from config import conexion_BD

app = Flask(__name__, template_folder="templates", static_folder="static")

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

            return redirect(url_for('prestamos'))
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

# ----------------------------------------------------- INSERTAR LIBROS ----------------------------------------------------- #

@app.route("/insertar", methods=["GET", "POST"])
def insertar_libro():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada

    #Abrir conexion con la base de datos
    conexion = conexion_BD()
    query = conexion.cursor()

    #Esta consulta devuelve la ultima seccion ingresada en RegistroLibros para que sea mas facil ingresar libros de manera ordenada
    #Si se ingresan por seccion no hace falta estar seleccionando nuevamente la seccion
    query.execute("select codigo_seccion from RegistroLibros order by id_registro desc limit 1")
    select_seccion = query.fetchone()

    if not select_seccion:
        ultima_seccion = "0"
    else:
        query.execute("""
        select codigo_seccion,seccion from SistemaDewey 
        where SistemaDewey.codigo_seccion = 
        (?)""",(select_seccion[0],))
        ultima_seccion = query.fetchall()
        

    #Consulta para mostrar un listado de todas las secciones del Sistema Dewey
    query.execute("select * from SistemaDewey")
    secciones = query.fetchall()

    #Verifica la accion que realiza el formulario en insertar.html
    if request.method == "POST":
        #Obtiene los datos del formulario en insertar.html
        Titulo = request.form["titulo"]
        NumeroPaginas = request.form["num_paginas"]
        ISBN = request.form["ISBN"]
        tomo = request.form["tomo"]
        NumeroCopias = request.form["num_copias"]
        NombreAutor = request.form["nombre_autor"]
        ApellidoAutor = request.form["apellido_autor"]
        editorial = request.form["editorial"]
        LugarPublicacion = request.form["lugar"]
        AnoPublicacion = request.form["anio"]
        
        SistemaDewey = request.form.get("sistema_dewey")

        #Variable para guardar la notacion interna
        _notacion = ""
        if editorial:
            Notacion = editorial[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres de la editorial
        elif (ApellidoAutor) and not editorial:
            editorial = "Otros"
            Notacion = ApellidoAutor[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres del apellido autor
        elif (NombreAutor) and not ApellidoAutor: #Para el extranio caso de que no exista ni editorial ni apellido de autor
            editorial = "Otros"
            ApellidoAutor = "-"
            Notacion = NombreAutor[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres del nombre del autor
        else: #No se agrega ni autor ni editorial notacion va a ser "OTR"
            editorial = "Otros"
            NombreAutor = "Otros"
            ApellidoAutor = "-"
            Notacion = "OTR"

        #!Fallo en ingreso de notacion cuando no hay editorial

        if editorial or ApellidoAutor or NombreAutor:
            for i in range (0,3): #Notacion es un arreglo, este for funciona para pasar ese arreglo a ser una variable
                _notacion = _notacion + Notacion[i]
                print(_notacion)

        #Cuado no se ingresa un lugar de publicacion se ingresa un lugar vacio(id_lugar 1 = "-")
        if LugarPublicacion=="":
            LugarPublicacion = "-"

        try:
            #? INSERT DE LIBROS
            query.execute(f"Insert into Libros (Titulo,ano_publicacion,numero_paginas,isbn,tomo,numero_copias) values (?,?,?,?,?,?)",(Titulo,AnoPublicacion,NumeroPaginas,ISBN,tomo,NumeroCopias))
            query.execute("Select id_libro from libros where titulo = ?",(Titulo,))
            id_libro = query.fetchone()[0]
            
            #?INSERT DE LUGARES
            #Si no existe insertar nuevo ya que columna lugar es UNIQUE
            query.execute("Insert or ignore into lugares (lugar) values (?)",(LugarPublicacion,))
            query.execute("Select id_lugar from lugares where lugar = ?",(LugarPublicacion,))
            id_lugar = query.fetchone()[0]

            #?INSERT DE AUTORES
            query.execute("insert or ignore into autores (nombre_autor,apellido_autor) values (?,?)", (NombreAutor,ApellidoAutor))
            query.execute("select id_autor from autores where nombre_autor = (?) AND apellido_autor = (?)",(NombreAutor,ApellidoAutor))
            id_autor = query.fetchone()[0]

            #? INSERT DE EDITORIALES
            query.execute("insert or ignore into Editoriales (editorial) values (?)",(editorial,))
            query.execute("select id_editorial from editoriales where editorial = (?)",(editorial,))
            id_editorial = query.fetchone()[0]

            #? INSERT DE NOTACIONES
            #Si no existe insertar nuevo ya que columna notacion es UNIQUE
            query.execute("Insert or ignore into notaciones (notacion,id_editorial,id_autor) values (?,?,?)",(_notacion,id_editorial,id_autor))
            query.execute("Select id_notacion from notaciones where notacion = (?) and id_autor = (?) and id_editorial = (?)",(_notacion,id_autor,id_editorial,))
            id_notacion = query.fetchone()[0]

            #? INSERT DE REGISTRO LIBROS
            #En registro libros, id_libro deberia ser unico? ya que se guarda un solo libro con el numero de copias
            query.execute("Insert into RegistroLibros(id_libro,id_notacion,id_lugar,codigo_seccion) values (?,?,?,?)",(id_libro,id_notacion,id_lugar,SistemaDewey))            
             
            #? Guardar cambios
            conexion.commit() 

            #Esta consulta devuelve la ultima seccion ingresada en RegistroLibros para que sea mas facil ingresar libros de manera ordenada
            #Si se ingresan por seccion no hace falta estar seleccionando nuevamente la seccion
            query.execute("select codigo_seccion from RegistroLibros order by id_registro desc limit 1")
            select_seccion = query.fetchone()
            
            if not select_seccion:
                ultima_seccion = "0"
            else:
                query.execute("""
                select * from SistemaDewey 
                where SistemaDewey.codigo_seccion = 
                (?)""",(select_seccion[0],))
                ultima_seccion = query.fetchall()

            
            registro_exitoso = "Libro registrado exitosamente."
            return render_template("insertar.html", secciones = secciones, ultima_seccion = ultima_seccion, registro_exitoso=registro_exitoso) 

        except Exception as e:
            print(f"Error: {e}")
            alerta = "Error al ingresar libro."
            return render_template("insertar.html", secciones = secciones, ultima_seccion = ultima_seccion, alerta=alerta) 
        finally:
            query.close()
            conexion.close()
    

    return render_template("insertar.html", secciones = secciones, ultima_seccion = ultima_seccion) #Devuelve variables para poder usarlas en insert.html


# ----------------------------------------------------- CATALOGO DE LIBROS ----------------------------------------------------- #

##! Para dividir los resultados del query usar offset y limit, con variable para el numero de pagina
##! VIDEO: https://www.youtube.com/watch?v=jUVPtMnbuv4

    #! Recordatorio de posible bug (04/04/2025)
    #TODO: El libro "Los 10 retos" se inserto sin autor, aunque el autor si se inserto correctamente, en la tabla notaciones se le fue asignado el autor X
    #TODO: El libro se inserto utilizando las facilidades de autorellenado del navegador Microsoft Edge
    #* Recordatorio: El commit estaba comentado en el primer intento de insert, este podria ser el origen del problema. 
    #* Observacion: El libro no tiene editorial, este tambien podria ser el origen del bug, pero en este caso lo dudo.

@app.route("/libros", methods=["GET", "POST"])
def libros():

    #Abrir conexion con la base de datos
    conexion = conexion_BD()
    query = conexion.cursor()

    pagina = request.args.get("pag", 1, type=int)
    libros_por_pagina = 16
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from Libros")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)

    #? Selecciona todos los libros disponibles
    # Consulta paginada
    query.execute("""
        select l.id_libro, Titulo, tomo, ano_publicacion, ISBN, numero_paginas, numero_copias,
        sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor, e.editorial, n.notacion,lu.lugar
        from Libros l
        join RegistroLibros r ON r.id_libro = l.id_libro
        join SistemaDewey sd ON sd.codigo_seccion = r.codigo_seccion 
        join notaciones n ON n.id_notacion = r.id_notacion
        join Autores a ON a.id_autor = n.id_autor
        join Editoriales e ON e.id_editorial = n.id_editorial
        join Lugares lu ON r.id_lugar = lu.id_lugar
        order by sd.codigo_seccion asc, Titulo asc
        LIMIT ? OFFSET ?
    """, (libros_por_pagina, offset))
    libros = query.fetchall()
    
    #? Selecciona todas las secciones del sistema dewey, para ser usados en los filtros
    query.execute("select * from SistemaDewey")
    categorias = query.fetchall()

    query.close()
    conexion.close()
    
    alerta = request.args.get("alerta", "")
    exito = request.args.get("exito", "")

    return render_template("libros.html",libros=libros,categorias=categorias,pagina=pagina,total_paginas=total_paginas,
                           alerta=alerta, exito = exito)

# ----------------------------------------------------- BUSCAR LIBROS ----------------------------------------------------- #

@app.route("/buscar_libro", methods=["GET","POST"])
def buscar_libro():
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar", "")
    filtro_busqueda = request.args.get("filtro-busqueda", "Titulo") 
    Seccion = request.args.get("categorias", "Todas") 
    alerta = request.args.get("alerta","")
    exito = request.args.get("exito","")


    pagina = request.args.get("pag", 1, type=int)
    libros_por_pagina = 16
    offset = (pagina - 1) * libros_por_pagina

    # Secciones Dewey para filtros
    query.execute("select * from SistemaDewey")
    categorias = query.fetchall()

    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f"where l.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f"where (a.nombre_autor || ' ' || a.apellido_autor) like '%{busqueda}%'")

    if not Seccion or Seccion == "Todas":
        SQL_where_seccion = ""
    else:
        SQL_where_seccion = (f" and sd.codigo_seccion = {Seccion}")

    filtro_total = SQL_where_busqueda + SQL_where_seccion

    # Conteo total para paginación
    query.execute(f"""
        select count(*) from Libros l
        join RegistroLibros r on r.id_libro = l.id_libro
        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
        join notaciones n on n.id_notacion = r.id_notacion
        join Autores a on a.id_autor = n.id_autor
        join Editoriales e on e.id_editorial = n.id_editorial
        join Lugares lu on r.id_lugar = lu.id_lugar
        {filtro_total}
    """)
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina) #Redondea el resultado hacia arriba, si hay (11 libros / 10 libros por pagina) = 1.1, math.ceil(1.1) = 2 paginas

    # Consulta paginada
    query.execute(f"""
        select l.id_libro, Titulo, tomo, ano_publicacion, ISBN, numero_paginas, numero_copias,
        sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor, e.editorial, n.notacion, lu.lugar
        from Libros l
        join RegistroLibros r on r.id_libro = l.id_libro
        join SistemaDewey sd on sd.codigo_seccion = r.codigo_seccion 
        join notaciones n on n.id_notacion = r.id_notacion
        join Autores a on a.id_autor = n.id_autor
        join Editoriales e on e.id_editorial = n.id_editorial
        join Lugares lu on r.id_lugar = lu.id_lugar
        {filtro_total}
        order by sd.codigo_seccion asc,Titulo asc
        limit ? offset ?
    """, (libros_por_pagina, offset))

    libros = query.fetchall()

    query.close()
    conexion.close()

    return render_template("libros.html", libros=libros, categorias=categorias,
                           pagina=pagina, total_paginas=total_paginas,
                           busqueda=busqueda, filtro_busqueda=filtro_busqueda, Seccion=Seccion, 
                           alerta = alerta, exito = exito)

# ----------------------------------------------------- ELIMINAR LIBROS ----------------------------------------------------- #

@app.route("/eliminar_libro", methods=["GET", "POST"])
def eliminar_libro():
    id_libro = request.form["id_libro"]
    motivo = request.form["motivo"]

    # Obtenre la fecha actual
    hoy = datetime.today().date()
    id_administrador = session.get("id_administrador")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select id_prestamo from prestamos where id_libro = ?",(id_libro,))
    libroprestado = query.fetchall()

    if(libroprestado):
        alerta = "Error, el libro está prestado."
        return redirect(url_for("libros",alerta = alerta))

    query.execute("select titulo from libros where id_libro = ?",(id_libro,))
    titulo_libro = query.fetchone()[0]

    query.execute("insert into libros_eliminados(id_administrador,id_libro,fecha,titulo,motivo) values(?,?,?,?,?)",(id_administrador,id_libro,hoy,titulo_libro,motivo))

    query.execute("delete from libros where id_libro = ?",(id_libro,))
    conexion.commit()

    query.close()
    conexion.close()

    exito = "Libro eliminado exitósamente."

    return redirect(url_for("libros",exito = exito))

# ----------------------------------------------------- SUGERENCIAS DINAMICAS ----------------------------------------------------- #

@app.route("/sugerencias-lugares")
def sugerencias_lugares():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select Lugar from lugares")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-editoriales")
def sugerencias_editoriales():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select editorial from editoriales")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-libros")
def sugerencias_libros():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select titulo from libros")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-autores")
def sugerencias_autores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select DISTINCT (nombre_autor || ' ' || apellido_autor) as NombreCompleto from autores;")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-libros-prestamos")
def sugerencias_libros_prestamos():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select (titulo || '(' || ano_publicacion || ')') from libros where numero_copias > 0")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-prestamo")
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

@app.route("/sugerencias-lectores")
def sugerencias_lector():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT (nombre || ' ' || apellido) from prestamos;""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-usuarios")
def sugerencias_usuarios():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select usuario from administradores")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-prestamo-eliminado-administradores")
def sugerencias_prestamo_eliminado_administradores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT a.usuario from administradores a
                    join prestamos_eliminados pe on a.id_administrador = pe.id_administrador""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-prestamo-eliminado-libro")
def sugerencias_prestamo_eliminado_libro():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT titulo from prestamos_eliminados""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-libro-eliminado-administradores")
def sugerencias_libro_eliminado_administradores():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT a.usuario from administradores a
                    join libros_eliminados le on a.id_administrador = le.id_administrador""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-libro-eliminado")
def sugerencias_libro_eliminado():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT titulo from libros_eliminados""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

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

@app.route("/prestamos",methods = ["GET","POST"])
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
    query.execute(f"""select strftime('%d-%m-%Y', p.fecha_prestamo), strftime('%d-%m-%Y', p.fecha_entrega_estimada), strftime('%d-%m-%Y', p.fecha_devolucion), l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, e.estado, p.id_prestamo
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

@app.route("/buscar_prestamo", methods = ["GET"])
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

    query_busqueda = (f"""select strftime('%d-%m-%Y', p.fecha_prestamo), strftime('%d-%m-%Y', p.fecha_entrega_estimada), strftime('%d-%m-%Y', p.fecha_devolucion), l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, e.estado, p.id_prestamo
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

@app.route("/devolver_prestamo", methods=["POST"])
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

@app.route("/eliminar_prestamo", methods=["GET", "POST"])
def eliminar_prestamo():
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

@app.route("/registro_prestamos", methods=["GET", "POST"])
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

# ----------------------------------------------------- REGISTRO USUARIOS ----------------------------------------------------- #

@app.route("/registrar_usuarios", methods=["GET", "POST"])
def registrar_usuarios():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("Select * from roles")
    roles = query.fetchall()

    #Verifica la accion que realiza el formulario en registro_usuairos.html
    if request.method == "POST":
        #Obtiene los datos del formulario en registro-prestamos.html
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]
        telefono = request.form["telefono"]
        rol = request.form["rol"]
  
        try:
            #? INSERT DE PRESTAMOS
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

@app.route("/usuarios",methods = ["POST","GET"])
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

@app.route("/eliminar_usuario", methods=["GET", "POST"])
def eliminar_usuario():
    id_usuario = request.form["id_usuario"]

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("delete from administradores where id_administrador = ?",(id_usuario,))
    conexion.commit()

    query.close()
    conexion.close()

    exito = "Usuario eliminado exiósamente."

    return redirect(url_for("usuarios",exito=exito))

# ----------------------------------------------------- BUSCAR Usuarios ----------------------------------------------------- #

@app.route("/buscar_usuario",methods = ["POST"])
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


# ----------------------------------------------------- Prestamos Eliminados ----------------------------------------------------- #

@app.route("/prestamos_eliminados",methods = ["POST","GET"])
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

@app.route("/buscar_prestamo_eliminado", methods = ["GET"])
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

# ----------------------------------------------------- Libros Eliminados ----------------------------------------------------- #

@app.route("/libros_eliminados",methods = ["POST","GET"])
def libros_eliminados():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    
    conexion = conexion_BD()
    query = conexion.cursor()

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from libros_eliminados")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha),le.titulo,le.motivo from libros_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            order by le.fecha desc
                            limit {libros_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    libros_eliminados = query.fetchall()

    query.close()
    conexion.close()


    return render_template("libros_eliminados.html",libros_eliminados=libros_eliminados,pagina=pagina,total_paginas=total_paginas)

# ----------------------------------------------------- Buscar Libro Eliminado ----------------------------------------------------- #

@app.route("/buscar_libro_eliminado", methods = ["GET"])
def buscar_libro_eliminado():
    if "usuario" not in session:
        return redirect("/") #Solo se puede acceder con session iniciada
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.args.get("buscar_libro_eliminado","")
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.args.get("filtro-busqueda","Titulo")

    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f" where le.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f" where a.usuario = '{busqueda}'")

    #Paginacion
    pagina = request.args.get("page", 1, type=int) #Recibe el parametro de la URL llamado page
    libros_por_pagina = 10
    offset = (pagina - 1) * libros_por_pagina

    # Consulta para contar todos los libros
    query.execute("select count(*) from libros_eliminados")
    total_libros = query.fetchone()[0]
    total_paginas = math.ceil(total_libros / libros_por_pagina)
    
    query_busqueda = (f"""select a.usuario,r.rol,strftime('%d-%m-%Y', le.fecha),le.titulo,le.motivo from libros_eliminados le
                            join Administradores a on le.id_administrador = a.id_administrador
                            join roles r on a.id_rol =  r.id_rol
                            {SQL_where_busqueda}
                            order by le.fecha desc
                            limit {libros_por_pagina} offset {offset}""")

    query.execute(query_busqueda)
    libros_eliminados = query.fetchall()

    query.close()
    conexion.close()


    return render_template("libros_eliminados.html",libros_eliminados=libros_eliminados,pagina=pagina,total_paginas=total_paginas,busqueda=busqueda,filtro_busqueda=filtro_busqueda)


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
