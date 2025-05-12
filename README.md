## Pasos para Ejecutar el Backend (Django)

1.  **Navegar al Directorio del Backend:**
    cd Backend

2.  **Crear el Entorno Virtual:**
    python -m venv venv

3.  **Activar el Entorno Virtual:**

    # En Windows:

    venv/Scripts/activate

    # En macOS y Linux:

    source venv/bin/activate

4.  **Instalar las Dependencias:**
    Una vez activado el entorno virtual, instala las bibliotecas necesarias desde el archivo `requirements.txt`:
    pip install -r requirements.txt

5.  **Registra tus instalaciones**
    Cada que instales algo nuevo dentro el entorno virtual ejecuta:
    pip freeze > requirements.txt

6.  **Realizar las Migraciones:** (//aún no realizar migraciones)
    Aplica las migraciones de Django para crear las tablas de la base de datos:
    python manage.py migrate

7.  **Ejecutar el Servidor de Desarrollo:**
    Inicia el servidor de desarrollo de Django:
    python manage.py runserver

    Esto iniciará el servidor en la dirección `http://127.0.0.1:8000/`.