from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder="../html/", static_folder="../front/")
app.secret_key = 'mi_clave_secreta' 

def inicializar_bd():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277'
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
                
            print("Base de datos y tabla creadas o verificadas correctamente.")
    
    except Error as e:
        print("Error al inicializar la base de datos:", e)
    
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
            print("Conexión a la base de datos cerrada.")


def registrar_usuario_en_bd(Nombre, Email, Password_, Rol):
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277',
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

@app.route('/login', methods=['GET', 'POST'])
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
                        return redirect(url_for('profesor'))
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

# Ruta principal
@app.route('/index')
def index():
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/')
def register():
    return render_template('register.html')

# @app.route('/index')
# def index():
#     return render_template('index.html')  

# @app.route('/login')
# def login():
#     return render_template('login.html')  


# Usuarios
@app.route('/administrador')
def administrador():
    return render_template('administrador.html')  

@app.route('/profesor')
def profesor():
    return render_template('profesor.html')  

@app.route('/estudiante')
def estudiante():
    return render_template('docente.html')  





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


@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    Nombre= request.form['Nombre']
    Email = request.form['Email']
    Rol= request.form['Rol']
    Password_ = request.form['Password_']
    
    registrar_usuario_en_bd(Nombre, Email, Password_, Rol)
    return redirect(url_for('register'))

if __name__ == "__main__":
    inicializar_bd()  #<- Same shit con lo de loguear admin
    app.run(debug=True)