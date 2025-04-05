from flask import Flask, render_template, request
from config import conexion_BD

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "1234"

# !Se puede monar esta app en la nube?
# *Se puede en RENDER HOSTING

# ----------------------------------------------------- PRINCIPAL ----------------------------------------------------- #

@app.route("/", methods=["GET", "POST"])
def inicio():

    return render_template("index.html")

# ----------------------------------------------------- INSERTAR LIBROS ----------------------------------------------------- #

@app.route("/insertar", methods=["GET", "POST"])
def insertar_libro():

    #Abrir conexion con la base de datos
    conexion = conexion_BD()
    query = conexion.cursor()

    #TODO: ## Cambiar la consulta entre parentesis, hacerla una variables para que sea mas sencillo de comprender
    #Esta consulta devuelve la ultima seccion ingresada en RegistroLibros para que sea mas facil ingresar libros de manera ordenada
    #Si se ingresan por seccion no hace falta estar seleccionando nuevamente la seccion
    query.execute("""
    select * from SistemaDewey 
    where SistemaDewey.codigo_seccion = 
    (select codigo_seccion from RegistroLibros 
    order by id_registro desc limit 1)""")
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
            Notacion = editorial[0:3].lower() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres de la editorial

        elif ApellidoAutor:
            editorial = "X"
            Notacion = ApellidoAutor[0:3].lower() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres del apellido autor
        
        elif NombreAutor: #Para el extranio caso de que no exista ni editorial ni apellido de autor
            editorial = "X"
            ApellidoAutor = "-"
            Notacion = NombreAutor[0:3].lower() #string[inicio:fin:paso] // Para tomar los primeros 3 caracteres del nombre del autor

        else: #No se agrega ni autor ni editorial notacion va a ser "X"
            editorial = "X"
            NombreAutor = "X"
            ApellidoAutor = "X"
            _notacion = "X"

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
            conexion.commit()  

            #Esta consulta devuelve la ultima seccion ingresada en RegistroLibros para que sea mas facil ingresar libros de manera ordenada
            #Si los libros se ingresan por seccion no hace falta estar seleccionando nuevamente la seccion.
            query.execute("""
            select * from SistemaDewey 
            where SistemaDewey.codigo_seccion = 
            (select codigo_seccion from RegistroLibros 
            order by id_registro desc limit 1)""")
            ultima_seccion = query.fetchall()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            query.close()
            conexion.close()
    

    return render_template("insertar.html", secciones = secciones, ultima_seccion = ultima_seccion) #Devuelve variables para poder usarlas en insert.html

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
    query.execute("""
    select l.id_libro,Titulo,tomo,ano_publicacion,ISBN,numero_paginas,numero_copias, sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor , e.editorial, n.notacion
    from Libros as l
    join RegistroLibros as r on r.id_libro = l.id_libro
    join SistemaDewey as sd on sd.codigo_seccion = r.codigo_seccion 
    join notaciones as n on n.id_notacion = r.id_notacion
    join Autores as a on a.id_autor = n.id_autor
    join Editoriales as e on e.id_editorial = n.id_editorial""")
    libros = query.fetchall()
    
    query.close()
    conexion.close()
        

    return render_template("libros.html",libros=libros)

@app.route("/buscar_libro",methods = ["POST"])
def buscar_libro():
    conexion = conexion_BD()
    query = conexion.cursor()

    busqueda = request.form["buscar"]

    #? Selecciona todos los libros disponibles
    query.execute(f"""
    select l.id_libro,Titulo,tomo,ano_publicacion,ISBN,numero_paginas,numero_copias, sd.codigo_seccion, sd.seccion, a.nombre_autor, a.apellido_autor , e.editorial, n.notacion
    from Libros as l
    join RegistroLibros as r on r.id_libro = l.id_libro
    join SistemaDewey as sd on sd.codigo_seccion = r.codigo_seccion 
    join notaciones as n on n.id_notacion = r.id_notacion
    join Autores as a on a.id_autor = n.id_autor
    join Editoriales as e on e.id_editorial = n.id_editorial
    where l.titulo like '%{busqueda}%' """)
    libros = query.fetchall()
    
    query.close()
    conexion.close()

    print(busqueda)

    return render_template("libros.html",libros=libros)

if __name__ == "__main__":
    #app.run()
    app.run(debug=True,port=5000)
