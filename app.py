from flask import Flask, session
from database import db
from routes import routes
from flask_login import LoginManager
from datetime import timedelta

# Crear una instancia de la app
app = Flask(__name__)
app.secret_key = 'supersecretkey123' # Clave secreta para la sesión
# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Configurar la duración de la cookie de sesión
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7) # Mantener la sesión activa por 7 días

# Importar el modelo User
from models import User 

# Cargar el usuario por ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configurar la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Mazapan2022%21@localhost:5432/pf_popcornhour'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)

# Registrar el Blueprint de las rutas
app.register_blueprint(routes)

# Asegurar que la sesión sea permanente
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7)

# Crea todas las tablas (solo si no están creadas aún)
with app.app_context():
    db.create_all()

# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)