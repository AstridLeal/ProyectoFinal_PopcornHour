from flask import Flask
from database import db
from routes import routes
from flask_login import LoginManager

# Crear una instancia de la app
app = Flask(__name__)
app.secret_key = 'supersecretkey123' # Clave secreta para la sesión
# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

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

# Crea todas las tablas (solo si no están creadas aún)
with app.app_context():
    db.create_all()

# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)