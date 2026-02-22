# BoardGamesHub

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**Desarrollador principal: José Fuentes Laborda**

---

## 1. Descripción del Proyecto
BoardGamesHub es una plataforma web orientada a la gestión, evaluación y clasificación de juegos de mesa. El sistema permite a los usuarios registrados explorar un catálogo extenso de juegos, publicar valoraciones y estructurar rankings personalizados mediante una interfaz interactiva y dinámica.

## 2. Características Principales
* **Catálogo de Juegos:** Sistema de exploración con paginación optimizada y motor de búsqueda filtrada.
* **Sistema de Valoraciones:** Funcionalidad para calificar títulos y redactar reseñas accesibles para toda la comunidad de usuarios.
* **Clasificación Interactiva (Drag & Drop):** Herramienta intuitiva para la creación y edición de rankings por categorías. Incluye sistema de autoguardado en LocalStorage y prevención de registros duplicados en base de datos.
* **Gestión de Usuarios:** Sistema robusto de autenticación y autorización para proteger la información, colecciones y listas de cada perfil.

## 3. Arquitectura y Tecnologías
* **Backend:** Python, framework web Django.
* **Base de Datos:** MongoDB (NoSQL), optimizado para el manejo flexible de estructuras de datos (rankings JSON y catálogo).
* **Frontend:** HTML5, CSS3, JavaScript Vanilla (Fetch API, manipulación asíncrona del DOM, Drag & Drop nativo).
* **UI/UX:** Implementación de CSS Grid/Flexbox para diseño responsivo, fuentes de Google Fonts y sistema de iconografía de FontAwesome.

## 4. Instrucciones de Despliegue Local

1. Clonar el repositorio:
    git clone https://github.com/jfuenteslaborda/boardgameshub.git
    cd boardgameshub

2. Configurar el entorno virtual:
    python -m venv venv
    source venv/bin/activate  (En Windows utilizar: venv\Scripts\activate)

3. Instalar las dependencias del proyecto:
    pip install -r requirements.txt

4. Configurar la Base de Datos:
    Asegurar que el servicio de MongoDB esté en ejecución a nivel local o, en su defecto, configurar la URI de conexión de MongoDB Atlas en el archivo settings.py.

5. Aplicar migraciones y ejecutar el servidor local:
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

6. Acceso a la aplicación:
    Abrir el navegador web e ingresar a http://127.0.0.1:8000/

## 5. Generar CSV de juegos
Ejecuta el script para crear un CSV con 25 registros de ejemplo:

    python generate_games_csv.py --output games_seed.csv