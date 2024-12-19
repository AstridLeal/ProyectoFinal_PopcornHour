# Popcorn Hour
Proyecto final de Programación Avanazada en Hybridge.

Popcorn Hour es una aplicación web para recomendar, calificar y discutir sobre películas y series. Los usuarios pueden registrarse como estándar o moderadores, y cada rol tiene diferentes permisos.

## Características

- **Usuarios no registrados**: Pueden ver la calificación de las películas, los comentarios y toda la información de las películas.
- **Usuarios estándar**: Pueden calificar y comentar películas.
- **Moderadores**: Pueden subir nuevas películas.


## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu_usuario/ProyectoFinal_PopcornHour.git
    cd ProyectoFinal_PopcornHour
    ```

2. Crea y activa un entorno virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4. Configura la base de datos:
    - Asegúrate de tener una base de datos configurada y actualiza `database.py` con tus credenciales de base de datos.
    python database.py

5. Ejecuta la aplicación:
    python app.py