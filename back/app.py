from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder="../front/html", static_folder="../front")
app.secret_key = 'mi_clave_secreta' 

def inicializar_bd():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  #<---------------------------------- CAMBIAR CONTRASEÑA ----------------------------------
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

            cursor.execute("""
                INSERT INTO Materias (Nombre, Descripcion)
                VALUES
                ('Calculo', 'Materia de calculo'),
                ('Programacion', 'Materia de programacion'),
                ('Física', 'Materia de Física Básica'),
                ('Bases de datos', 'Materia de bases de datos');
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Materias_Estudiante (
                    ID_materia_estudiante INT PRIMARY KEY AUTO_INCREMENT,
                    ID_estudiante INT,
                    ID_materia INT,
                    FOREIGN KEY (ID_estudiante) REFERENCES Usuarios(ID_usuario) ON DELETE CASCADE,
                    FOREIGN KEY (ID_materia) REFERENCES Materias(ID_materia) ON DELETE CASCADE
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


@app.route('/asignar_materia_estudiante')
def asignar_materia_estudiante():
    return render_template('asignar_materia_estudiante.html')

@app.route('/asignar_materia_docente')
def asignar_materia_docente():
    return render_template('asignar_materia_docente.html')

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


@app.route('/categorias')
def categorias():
    return render_template('categorias.html')  

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')  

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')  

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')  

#------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password_']
        try:
            conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='Proyecto_notas'
            )
            if conexion.is_connected():
                cursor = conexion.cursor()
                consulta = "SELECT Nombre, Rol FROM Usuarios WHERE Email = %s AND Password_ = %s"
                cursor.execute(consulta, (email, password))
                user = cursor.fetchone()
                if user:
                    session['user'] = user[0]
                    session['rol'] = user[1]

                    if user[1] == 'administrador':
                        return redirect(url_for('administrador'))
                    elif user[1] == 'docente':
                        return redirect(url_for('docente'))
                    elif user[1] == 'estudiante':
                        return redirect(url_for('estudiante'))
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
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='Proyecto_notas'
        )
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