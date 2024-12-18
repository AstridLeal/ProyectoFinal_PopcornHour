import os
from flask import current_app, Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import User, Movie, Comment
from database import db

routes = Blueprint('routes', __name__)

# Ruta principal: lista de películas
@routes.route('/')
def index():
    movies = Movie.query.all()
    movie_ratings = {}
    for movie in movies:
        comments = Comment.query.filter_by(movie_id=movie.id).all()
        ratings = [comment.rating for comment in comments if comment.rating > 0]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        movie_ratings[movie.id] = average_rating

    return render_template('index.html', movies=movies, movie_ratings=movie_ratings)

# Ruta de registro
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # 'standard' o 'moderator'

        # Verificar si el correo ya existe
        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado.', 'danger')
            return redirect(url_for('routes.register'))

        # Crear un nuevo usuario con contraseña hasheada
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html')

# Ruta de inicio de sesión
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verificar si el usuario existe
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Guardar datos del usuario en la sesión
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html')

# Ruta para cerrar sesión
@routes.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('routes.index'))

# Ruta para agregar una película (solo para moderadores)
@routes.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    # Verificar si el usuario está autenticado y es moderador
    if session.get('role') != 'moderator':  # Verifica si es moderador
        flash('No tienes permisos para agregar películas.', 'danger')
        return redirect(url_for('routes.dashboard'))

    image_url = None

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        genre = request.form['genre']
        year = request.form['year']

        # Si no se proporciona una URL de imagen, revisa si el usuario subió un archivo
        if 'image' in request.files:  # Verifica si se subió una imagen
            image = request.files['image']
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.root_path, 'static', 'images', filename)
                image.save(image_path)
                image_url = url_for('static', filename=f'images/{filename}')

        # Guardar la película
        new_movie = Movie(title=title, description=description, genre=genre, year=year, image_url=image_url)
        db.session.add(new_movie)
        db.session.commit()

        flash(f'Película "{title}" agregada exitosamente.', 'success')
        return redirect(url_for('routes.dashboard'))

    return render_template('add_movie.html')

# Dashboard para mostrar las películas y opciones
@routes.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero.', 'warning')
        return redirect(url_for('routes.login'))

    movies = Movie.query.all()
    movie_ratings = {}
    for movie in movies:
        comments = Comment.query.filter_by(movie_id=movie.id).all()
        ratings = [comment.rating for comment in comments if comment.rating > 0]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        movie_ratings[movie.id] = average_rating

    return render_template('dashboard.html', movies=movies, movie_ratings=movie_ratings, username=session['username'], role=session['role'])

# Ruta para ver detalles de una película
@routes.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    comments = Comment.query.filter_by(movie_id=movie.id, parent_id=None).all()  # Solo comentarios principales

    # Calcular el promedio de calificación
    ratings = [comment.rating for comment in comments if comment.rating > 0]
    average_rating = sum(ratings) / len(ratings) if ratings else 0

    if 'user_id' in session:
        user_role = session.get('role')
        if user_role == 'standard' and request.method == 'POST':
            comment_text = request.form['comment']
            rating = request.form.get('rating')  # Puede ser None si es una respuesta
            parent_id = request.form.get('parent_id')  # ID del comentario padre, si es una respuesta

            # Validar que la calificación sea un número y esté entre 1 y 5, si se proporciona
            if rating:
                try:
                    rating = int(rating)
                    if not (1 <= rating <= 5):
                        flash('La calificación debe estar entre 1 y 5 estrellas.', 'danger')
                        return redirect(url_for('routes.movie_detail', movie_id=movie.id))
                except ValueError:
                    flash('La calificación debe ser un número entero entre 1 y 5.', 'danger')
                    return redirect(url_for('routes.movie_detail', movie_id=movie.id))

            new_comment = Comment(movie_id=movie.id, user_id=session['user_id'], text=comment_text, rating=rating or 0, parent_id=parent_id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comentario y calificación agregados exitosamente.', 'success')

            return redirect(url_for('routes.movie_detail', movie_id=movie.id))

    return render_template('movie_details.html', movie=movie, comments=comments, average_rating=average_rating, user_id=session.get('user_id'))

# Ruta para eliminar una película (solo para moderadores)
@routes.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if 'user_id' not in session or session.get('role') != 'moderator':
        flash('No tienes permisos para eliminar películas.', 'danger')
        return redirect(url_for('routes.dashboard'))

    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash(f'Película "{movie.title}" eliminada exitosamente.', 'success')
    return redirect(url_for('routes.dashboard'))