from flask import Flask
from database import db
from routes import routes
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'supersecretkey123'
login_manager = LoginManager()
login_manager.init_app(app)

# Luego, agrega la carga de usuarios
from models import User  # Asegúrate de que esta línea esté después de definir tu modelo User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Mazapan2022%21@localhost:5432/pf_popcornhour'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(routes)

# Crea todas las tablas (solo si no están creadas aún)
with app.app_context():
    db.create_all()

# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)