from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error


app = Flask(__name__, template_folder="../front/html", static_folder="../front")
app.secret_key = 'mi_clave_secreta' 

def obtener_conexion():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',                                #<---------------------------------- CAMBIAR CONTRASEÑA ----------------------------------
        database='Proyecto_notas'
    )



def inicializar_bd():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',                             #<---------------------------------- CAMBIAR CONTRASEÑA ----------------------------------
        )
        
        if conexion.is_connected():
            cursor = conexion.cursor()

            cursor.execute("CREATE DATABASE IF NOT EXISTS Proyecto_notas")
            cursor.execute("USE Proyecto_notas")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuarios (
                    ID_usuario INT PRIMARY KEY AUTO_INCREMENT,
                    Nombre VARCHAR(255) NOT NULL,
                    Email VARCHAR(255) NOT NULL,
                    Password_ VARCHAR(255) NOT NULL,
                    Rol ENUM('administrador', 'docente', 'estudiante') NOT NULL
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Materias (
                    ID_materia INT PRIMARY KEY AUTO_INCREMENT,
                    Nombre VARCHAR(255) NOT NULL,   
                    Descripcion TEXT
                );
            """)

            cursor.execute("SELECT COUNT(*) FROM Materias")
            materias_existentes = cursor.fetchone()[0]

            if materias_existentes == 0:
                cursor.execute("""
                    INSERT INTO Materias (Nombre, Descripcion)
                    VALUES
                    ('Calculo', 'Materia de calculo'),
                    ('Programacion', 'Materia de programacion'),
                    ('Física', 'Materia de Física Básica'),
                    ('Bases de datos', 'Materia de bases de datos');
                """)
                conexion.commit()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Materias_Estudiante (
                    ID_materia_estudiante INT PRIMARY KEY AUTO_INCREMENT,
                    ID_estudiante INT,
                    ID_materia INT,
                    FOREIGN KEY (ID_estudiante) REFERENCES Usuarios(ID_usuario) ON DELETE CASCADE,
                    FOREIGN KEY (ID_materia) REFERENCES Materias(ID_materia) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Materias_Docente (
                    ID_materia_docente INT PRIMARY KEY AUTO_INCREMENT,
                    ID_docente INT,
                    ID_materia INT,
                    FOREIGN KEY (ID_docente) REFERENCES Usuarios(ID_usuario) ON DELETE CASCADE,
                    FOREIGN KEY (ID_materia) REFERENCES Materias(ID_materia) ON DELETE CASCADE
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Actividades (
                    ID_actividad INT PRIMARY KEY AUTO_INCREMENT,
                    ID_docente INT,
                    ID_materia INT,
                    Titulo VARCHAR(255) NOT NULL,
                    Descripcion TEXT,
                    Fecha DATE,
                    FOREIGN KEY (ID_docente) REFERENCES Usuarios(ID_usuario) ON DELETE CASCADE,
                    FOREIGN KEY (ID_materia) REFERENCES Materias(ID_materia) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Calificaciones (
                    ID_calificacion INT PRIMARY KEY AUTO_INCREMENT,
                    ID_estudiante INT,
                    ID_actividad INT,
                    Calificacion DECIMAL(5,2),
                    FOREIGN KEY (ID_estudiante) REFERENCES Usuarios(ID_usuario) ON DELETE CASCADE,
                    FOREIGN KEY (ID_actividad) REFERENCES Actividades(ID_actividad) ON DELETE CASCADE
                );
            """)


            cursor.execute("SELECT * FROM Usuarios WHERE Rol = 'administrador'")
            administrador_existe = cursor.fetchone()

            if not administrador_existe:
                cursor.execute("""
                    INSERT INTO Usuarios (Nombre, Email, Password_, Rol)
                    VALUES ('Admin1', 'staff@gmail.com', '0001', 'administrador')
                """)
                conexion.commit()
                print("Administrador creado correctamente.")
            else:
                print("El administrador ya existe en la base de datos.")
                
            print("Base de datos y tablas creadas o verificadas correctamente.")
    
    except Error as e:
        print("Error al inicializar la base de datos:", e)
    
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
            print("Conexión a la base de datos cerrada.")

#---------------------------------DB---------------------------------

@app.route('/docente_dashboard')
def docente_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    docente_id = session['user_id']
    print("ID del docente en sesión:", session.get('user_id'))

    try:
        # Conectar a la base de datos
        conexion = obtener_conexion()
        query = """
            SELECT m.Nombre 
            FROM Materias m
            JOIN Materias_Docente me ON m.ID_materia = me.ID_materia
            WHERE me.ID_docente = %s
        """
        with conexion.cursor() as cursor:
            cursor.execute(query, (docente_id,))
            materias = cursor.fetchall()

        # Extraer solo los nombres de las materias
        materias_nombres = [materia[0] for materia in materias]
        print("Nombres de las materias:", materias_nombres)
    except Error as e:
        print("Error al obtener las materias:", e)
        materias_nombres = []

    finally:
        if conexion.is_connected():
            conexion.close()

    return render_template('docente.html', materias=materias_nombres)


@app.route('/estudiante_dashboard')
def estudiante_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    estudiante_id = session['user_id']
    print("ID del estudiante en sesión:", session.get('user_id'))

    try:
        # Conectar a la base de datos
        conexion = obtener_conexion()
        query = """
            SELECT m.Nombre 
            FROM Materias m
            JOIN Materias_Estudiante me ON m.ID_materia = me.ID_materia
            WHERE me.ID_estudiante = %s
        """
        with conexion.cursor() as cursor:
            cursor.execute(query, (estudiante_id,))
            materias = cursor.fetchall()

        # Extraer solo los nombres de las materias
        materias_nombres = [materia[0] for materia in materias]
        print("Nombres de las materias:", materias_nombres)
    except Error as e:
        print("Error al obtener las materias:", e)
        materias_nombres = []

    finally:
        if conexion.is_connected():
            conexion.close()

    return render_template('estudiante.html', materias=materias_nombres)

#------------------------------------------------------------

@app.route('/asignar_materia_estudiante', methods=['GET', 'POST'])
def asignar_materia_estudiante():
    if request.method == 'POST':
        id_estudiante = request.form['estudiante']
        id_materia = request.form['materia']

        try:
            conexion = obtener_conexion()

            if conexion.is_connected():
                cursor = conexion.cursor()
                consulta = """
                INSERT INTO Materias_Estudiante (ID_estudiante, ID_materia)
                VALUES (%s, %s)
                """
                cursor.execute(consulta, (id_estudiante, id_materia))
                conexion.commit()
                flash("Materia asignada con éxito", "success")
        except Error as e:
            flash("Error al asignar materia: " + str(e), "error")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    try:
        conexion = obtener_conexion()
        if conexion.is_connected():
            cursor = conexion.cursor()

            # Obtener estudiantes
            cursor.execute("SELECT ID_usuario, Nombre FROM Usuarios WHERE Rol = 'estudiante'")
            estudiantes = cursor.fetchall()
            print(estudiantes)

            # Obtener materias
            cursor.execute("SELECT ID_materia, Nombre FROM Materias")
            materias = cursor.fetchall()
            print(materias)

            return render_template('asignar_materia_estudiante.html', estudiantes=estudiantes, materias=materias)
    except Error as e:
        flash("Error al cargar datos: " + str(e), "error")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


@app.route('/asignar_materia_docente', methods=['GET', 'POST'])
def asignar_materia_docente():
    if request.method == 'POST':
        id_docente = request.form['docente']
        id_materia = request.form['materia']

        try:
            conexion = obtener_conexion()
            if conexion.is_connected():
                cursor = conexion.cursor()
                consulta = """
                INSERT INTO Materias_Docente (ID_docente, ID_materia)
                VALUES (%s, %s)
                """
                cursor.execute(consulta, (id_docente, id_materia))
                conexion.commit()
                flash("Materia asignada con éxito", "success")
        except Error as e:
            flash("Error al asignar materia: " + str(e), "error")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    try:
        conexion = obtener_conexion()
        if conexion.is_connected():
            cursor = conexion.cursor()

            # Obtener docentes
            cursor.execute("SELECT ID_usuario, Nombre FROM Usuarios WHERE Rol = 'docente'")
            docentes = cursor.fetchall()
            print(docentes)

            # Obtener materias
            cursor.execute("SELECT ID_materia, Nombre FROM Materias")
            materias = cursor.fetchall()
            print(materias)

            return render_template('asignar_materia_docente.html', docentes=docentes, materias=materias)
    except Error as e:
        flash("Error al cargar datos: " + str(e), "error")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

#------------------------------------------------------------

# Usuarios
@app.route('/administrador')
def administrador():
    return render_template('administrador.html')  

@app.route('/docente')
def docente():
    return render_template('docente.html')  

@app.route('/estudiante')
def estudiante():
    return render_template('estudiante.html')  


#------------------------------------------------------------




#------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password_']
        try:
            conexion = obtener_conexion()
            if conexion.is_connected():
                cursor = conexion.cursor()
                consulta = "SELECT ID_usuario, Nombre, Rol FROM Usuarios WHERE Email = %s AND Password_ = %s"
                cursor.execute(consulta, (email, password))
                user = cursor.fetchone()
                if user:
                    # Guardar ID, Nombre y Rol en la sesión
                    session['user_id'] = user[0]  # ID del usuario
                    session['user'] = user[1]    # Nombre del usuario
                    session['rol'] = user[2]     # Rol del usuario

                    if user[2] == 'administrador':
                        return redirect(url_for('administrador'))
                    elif user[2] == 'docente':
                        return redirect(url_for('docente_dashboard'))
                    elif user[2] == 'estudiante':
                        return redirect(url_for('estudiante_dashboard'))
                else:
                    flash("Credenciales incorrectas", "error")
        except Error as e:
            print("Error al iniciar sesión:", e)
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    return render_template('login.html')

# Ruta de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#------------------------------------------------------------

def registrar_usuario_en_bd(Nombre, Email, Password_, Rol):
    try:
        conexion = obtener_conexion()
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = """
            INSERT INTO Usuarios (nombre, email, password_, rol)
            VALUES (%s, %s, %s ,%s)
            """
            cursor.execute(consulta, (Nombre, Email, Password_, Rol))
            conexion.commit()
            print("Usuario registrado con éxito.")
    except Error as e:
        print("Error al registrar el usuario:", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    Nombre= request.form['Nombre']
    Email = request.form['Email']
    Rol= request.form['Rol']
    Password_ = request.form['Password_']
    
    registrar_usuario_en_bd(Nombre, Email, Password_, Rol)
    return redirect(url_for('administrador'))

@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == "__main__":
    
    inicializar_bd()  #<- Same shit con lo de loguear admin
    app.run(debug=True)