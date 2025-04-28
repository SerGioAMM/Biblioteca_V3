from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from config import conexion_BD
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "1234"

# !Se puede montar esta app en la nube?
# *Se puede en RENDER HOSTING

# ----------------------------------------------------- PRINCIPAL ----------------------------------------------------- #

@app.route("/", methods=["GET", "POST"])
def inicio():
    #TODO: Idea descartada, Libros destacados, donde el libro que se presta aparecia como destacado

    return render_template("index.html")

# ----------------------------------------------------- LOGIN ----------------------------------------------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    login = True

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

            print(session)

            login = True

            return redirect(url_for('prestamos'))
        else:
            login = False

    query.close()
    conexion.close()

    return render_template("login.html", login = login)

# ----------------------------------------------------- INSERTAR LIBROS ----------------------------------------------------- #

@app.route("/insertar", methods=["GET", "POST"])
def insertar_libro():

    #Abrir conexion con la base de datos
    conexion = conexion_BD()
    query = conexion.cursor()

    #Esta consulta devuelve la ultima seccion ingresada en RegistroLibros para que sea mas facil ingresar libros de manera ordenada
    #Si se ingresan por seccion no hace falta estar seleccionando nuevamente la seccion
    query.execute("select codigo_seccion from RegistroLibros order by id_registro desc limit 1")
    select_seccion = query.fetchone()

    query.execute("select * from SistemaDewey where SistemaDewey.codigo_seccion = (?)",(select_seccion[0],))
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
            #for caracter in editorial: #!TOMAR INICIALES DE EDITORIAL COMPUESTA
                #if caracter == ' ':
                    #print("ESPACIO")
            Notacion = editorial[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres de la editorial

        elif ApellidoAutor:
            editorial = "Otros"
            Notacion = ApellidoAutor[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres del apellido autor
        
        elif NombreAutor: #Para el extranio caso de que no exista ni editorial ni apellido de autor
            editorial = "Otros"
            ApellidoAutor = "Otros"
            Notacion = NombreAutor[0:3].upper() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres del nombre del autor

        else: #No se agrega ni autor ni editorial notacion va a ser "-"
            editorial = "Otros"
            NombreAutor = "Otros"
            ApellidoAutor = "Otros"
            _notacion = "OTR"

        if editorial or ApellidoAutor or NombreAutor:
            for i in range (0,3): #Notacion es un arreglo, este for funciona para pasar ese arreglo a ser una variable
                _notacion = _notacion + Notacion[i]
            
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
            query.execute("Insert or ignore into notaciones (notacion,id_editorial,id_autor) values (?,?,?)",(_notacion,id_autor,id_editorial))
            query.execute("Select id_notacion from notaciones where notacion = (?)",(_notacion,))
            id_notacion = query.fetchone()[0]

            #? INSERT DE REGISTRO LIBROS
            #En registro libros, id_libro deberia ser unico? ya que se guarda un solo libro con el numero de copias
            query.execute("Insert into RegistroLibros(id_libro,id_notacion,id_lugar,codigo_seccion) values (?,?,?,?)",(id_libro,id_notacion,id_lugar,SistemaDewey))            
             
            #? Guardar cambios
            #conexion.commit()  

            #Esta consulta devuelve la ultima seccion ingresada en RegistroLibros para que sea mas facil ingresar libros de manera ordenada
            #Si se ingresan por seccion no hace falta estar seleccionando nuevamente la seccion
            query.execute("select codigo_seccion from RegistroLibros order by id_registro desc limit 1")
            select_seccion = query.fetchone()

            query.execute("""
            select * from SistemaDewey 
            where SistemaDewey.codigo_seccion = 
            (?)""",(select_seccion[0],))
            ultima_seccion = query.fetchall()
            

        except Exception as e:
            print(f"Error: {e}")
        finally:
            query.close()
            conexion.close()
    

    return render_template("insertar.html", secciones = secciones, ultima_seccion = ultima_seccion) #Devuelve variables para poder usarlas en insert.html


# ----------------------------------------------------- CATALOGO DE LIBROS ----------------------------------------------------- #

##! Para dividir los resultados del query usar offset y limit, con variable para el numero de pagina
##! VIDEO: https://www.youtube.com/watch?v=jUVPtMnbuv4

@app.route("/libros", methods=["GET", "POST"])
def libros():

    #Abrir conexion con la base de datos
    conexion = conexion_BD()
    query = conexion.cursor()

    #! Recordatorio de posible bug (04/04/2025)
    #TODO: El libro "Los 10 retos" se inserto sin autor, aunque el autor si se inserto correctamente, en la tabla notaciones se le fue asignado el autor X
    #TODO: El libro se inserto utilizando las facilidades del navegador edge del autorellenado de datos
    #* Recordatorio: El commit estaba comentado en el primer intento de insert, este podria ser el origen del problema. 
    #* Observacion: El libro no tiene editorial, este tambien podria ser el origen del bug, pero en este caso lo dudo.

    #? Selecciona todos los libros disponibles
    #! Con el nuevo disenio algunos datos ya no se utilizan, como la editorial o el tomo
    query.execute("""
    select l.id_libro,Titulo,tomo,ano_publicacion,ISBN,numero_paginas,numero_copias, sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor , e.editorial, n.notacion
    from Libros as l
    join RegistroLibros as r on r.id_libro = l.id_libro
    join SistemaDewey as sd on sd.codigo_seccion = r.codigo_seccion 
    join notaciones as n on n.id_notacion = r.id_notacion
    join Autores as a on a.id_autor = n.id_autor
    join Editoriales as e on e.id_editorial = n.id_editorial""")
    libros = query.fetchall()
    
    #? Selecciona todas las secciones del sistema dewey, para ser usados en los filtros
    query.execute("select * from SistemaDewey")
    categorias = query.fetchall()

    query.close()
    conexion.close()
        

    return render_template("libros.html",libros=libros,categorias=categorias)

# ----------------------------------------------------- BUSCAR LIBROS ----------------------------------------------------- #

@app.route("/buscar_libro",methods = ["POST"])
def buscar_libro():
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.form["buscar"]
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.form["filtro-busqueda"]
    Seccion = request.form.get("categorias")
    
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f"where l.titulo like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f"where a.nombre_autor like '%{busqueda}%'")
    
    if Seccion == "Todas":
        SQL_where_seccion =" "
    else:
        SQL_where_seccion = (f" and sd.codigo_seccion = {Seccion}")

    print(SQL_where_seccion)

    #! Cuando tenga datos reales, comprobar importancia de left join (hice esto porque varios libros tenian datos incompletos)
    query_busqueda = (f"""
    select l.id_libro,Titulo,tomo,ano_publicacion,ISBN,numero_paginas,numero_copias, sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor , e.editorial, n.notacion
    from Libros as l
    left join RegistroLibros as r on r.id_libro = l.id_libro
    left join SistemaDewey as sd on sd.codigo_seccion = r.codigo_seccion 
    left join notaciones as n on n.id_notacion = r.id_notacion
    left join Autores as a on a.id_autor = n.id_autor
    left join Editoriales as e on e.id_editorial = n.id_editorial """)

    query_busqueda = query_busqueda + SQL_where_busqueda + SQL_where_seccion

    query.execute(query_busqueda)
    libros = query.fetchall()

    #? Selecciona todas las secciones del sistema dewey, para ser usados en los filtros
    query.execute("select * from SistemaDewey")
    categorias = query.fetchall()


    query.close()
    conexion.close()

    ## "' OR '1'='1' -- "
    ## "' UNION SELECT id_lugar, lugar, '', '', '', '', '', '', '', '', '', '', '' FROM lugares -- "

    return render_template("libros.html",libros=libros,categorias=categorias)

# ----------------------------------------------------- ELIMINAR LIBROS ----------------------------------------------------- #

@app.route("/eliminar_libro", methods=["GET", "POST"])
def eliminar_libro():
    id_libro = request.form["id_libro"]

    # Obtenre la fecha actual
    hoy = datetime.today().date()
    id_administrador = session.get("id_administrador")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("insert into libros_eliminados(id_administrador,id_libro,fecha) values(?,?,?)",(id_administrador,id_libro,hoy))

    query.execute("delete from libros where id_libro = ?",(id_libro))
    conexion.commit()

    query.close()
    conexion.close()

    return redirect("/libros")

# ----------------------------------------------------- SUGERENCIAS DINAMICAS ----------------------------------------------------- #

#! TEST_SUGERENCIAS
#TODO: Completar conforme a las sugerencias que faltan
#? Aun no se si sugerir en la busqueda de libros

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

    query.execute("select concat(nombre_autor,' ',apellido_autor) as NombreCompleto from autores;")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-libros-prestamos")
def sugerencias_libros_prestamos():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("select titulo from libros where numero_copias > 0")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-prestamo")
def sugerencias_prestamos():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select concat(l.titulo,' (',p.nombre,' ',p.apellido,')') from prestamos p 
                  join Libros l on p.id_libro = l.id_libro""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

@app.route("/sugerencias-lectores")
def sugerencias_lector():
    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("""select DISTINCT concat(nombre,' ',apellido) from prestamos;""")
    sugerencia = query.fetchall()

    query.close()
    conexion.close()

    return jsonify([fila[0] for fila in sugerencia])

# ----------------------------------------------------- PRESTAMOS ----------------------------------------------------- #

@app.route("/prestamos")
def prestamos():
    conexion = conexion_BD()
    query = conexion.cursor()

    # Obtenre la fecha actual
    hoy = datetime.today().date()

    # Buscar prestamos para verificar si estan vencidos
    query.execute("""select id_prestamo, fecha_entrega_estimada
                    from Prestamos
                    where id_estado = 1""")  # Solo prestamos que esten activos (no revisaremos los que ya esten devueltos o vencidos)
    prestamos_para_verificar = query.fetchall()

    #Verifica que si existan prestamos activos
    if prestamos_para_verificar:
        # for para revisar cada prestamo
        for prestamo in prestamos_para_verificar:
            id_prestamo = prestamo[0]
            fecha_entrega_estimada = datetime.strptime(prestamo[1], "%Y-%m-%d").date()

        if fecha_entrega_estimada < hoy:
            query.execute("""update Prestamos
                            set id_estado = 3
                            where id_prestamo = ?""", (id_prestamo,))
            conexion.commit()  # Guardamos los cambios

    # Consulta para mostrar los prestamos en tarjetas de prestamos.html
    query.execute("""select p.fecha_prestamo, p.fecha_entrega_estimada, p.fecha_devolucion, l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, e.estado, p.id_prestamo
                    from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados e on p.id_estado = e.id_estado""")
    prestamos = query.fetchall()

    query.close()
    conexion.close()


    return render_template("prestamos.html",prestamos=prestamos)

# ----------------------------------------------------- BUSCAR Prestamo ----------------------------------------------------- #

@app.route("/buscar_prestamo",methods=["POST"])
def buscar_prestamo():

    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.form["buscar_prestamo"]
    #Obtiene los datos del formulario filtros en libros.html
    filtro_busqueda = request.form["filtro-busqueda"]
    Estado = request.form["estados"]
    
    if filtro_busqueda == "Titulo":
        SQL_where_busqueda = (f"where l.titulo || ' (' || p.nombre || ' ' || p.apellido || ')' like '%{busqueda}%'")
    else:
        SQL_where_busqueda = (f"where p.nombre || ' ' || p.apellido like '%{busqueda}%'")
    
    if Estado == "Todos":
        SQL_where_estado =" "
    else:
        SQL_where_estado = (f" and e.id_estado = {Estado}")

    print(SQL_where_estado)
    
    query_busqueda = ("""select p.fecha_prestamo, p.fecha_entrega_estimada, p.fecha_devolucion, l.Titulo, p.nombre, p.apellido, p.dpi_usuario, p.num_telefono,  p.direccion, e.estado, p.id_prestamo
                    from Prestamos p
                    join Libros l on p.id_libro = l.id_libro
                    join Estados e on p.id_estado = e.id_estado """)
    
    query_busqueda = query_busqueda + SQL_where_busqueda + SQL_where_estado

    print(query_busqueda)

    query.execute(query_busqueda)
    prestamos = query.fetchall()

    query.close()
    conexion.close()

    return render_template("prestamos.html",prestamos=prestamos)

# ----------------------------------------------------- Devolver Prestamo ----------------------------------------------------- #

@app.route("/devolver_prestamo", methods=["POST"])
def devolver_prestamo():
    id_prestamo = request.form["id_prestamo"]

    # Obtenre la fecha actual
    hoy = datetime.today().date()

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("update prestamos set id_estado = 2 where id_prestamo = (?)",(id_prestamo,))
    conexion.commit() #Guarda la actualizacion de estado del prestamo

    query.execute("update prestamos set fecha_devolucion = (?) where id_prestamo = (?)",(hoy,id_prestamo,))
    conexion.commit() #Guarda la actualizacion de estado del prestamo


    query.close()
    conexion.close()

    return redirect("/prestamos")

# ----------------------------------------------------- Eliminar Prestamo ----------------------------------------------------- #

@app.route("/eliminar_prestamo", methods=["GET", "POST"])
def eliminar_prestamo():
    id_prestamo = request.form["id_prestamo"]

    # Obtenre la fecha actual
    hoy = datetime.today().date()
    id_administrador = session.get("id_administrador")

    conexion = conexion_BD()
    query = conexion.cursor()

    query.execute("insert into prestamos_eliminados(id_administrador,id_prestamo,fecha) values(?,?,?)",(id_administrador,id_prestamo,hoy))

    query.execute("delete from prestamos where id_prestamo = ?",(id_prestamo))
    conexion.commit()

    query.close()
    conexion.close()

    return redirect("/prestamos")


# ----------------------------------------------------- REGISTRO PRESTAMOS ----------------------------------------------------- #

@app.route("/registro_prestamos", methods=["GET", "POST"])
def registro_prestamos():
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
        Estado = 1 #Activo
            
        try:
            query.execute("Select id_libro from Libros where titulo = ?",(Libro,))
            Libro = query.fetchone()[0]

            #? INSERT DE PRESTAMOS
            query.execute(f"""Insert into Prestamos(dpi_usuario,nombre,apellido,direccion,num_telefono,id_libro,grado,id_estado,fecha_prestamo,fecha_entrega_estimada,fecha_devolucion)
                          values (?,?,?,?,?,?,?,?,?,?,NULL)""",(DPI,NombreLector,ApellidoLector,Direccion,Telefono,Libro,GradoEstudio,Estado,fecha_prestamo,fecha_entrega_estimada))

            query.execute(f"update Libros set numero_copias = (numero_copias-1) where id_libro = ?",(Libro,))

            #? Guardar cambios
            conexion.commit()  
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            query.close()
            conexion.close()


    return render_template("registro_prestamos.html")

# ----------------------------------------------------- APP ----------------------------------------------------- #

if __name__ == "__main__":
    #app.run()
    app.run(debug=True,port=5000)
