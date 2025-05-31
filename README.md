## Proyecto de Clasificación de Música usando Aprendizaje por Refuerzo (RL)

Área: Aprendizaje por Refuerzo (Reinforcement Learning)
Subárea: Clasificación y Optimización
Problema: Clasificación automática de canciones por género musical

- ¿Qué es el Aprendizaje por Refuerzo?
  El Aprendizaje por Refuerzo (RL) es una técnica de Machine Learning que entrena agentes inteligentes para tomar decisiones mediante un enfoque de ensayo y error. A través de un sistema de recompensas y penalizaciones, el agente aprende progresivamente cuál es la mejor estrategia para lograr un objetivo.
  A diferencia del aprendizaje supervisado, donde se necesitan etiquetas explícitas, en RL el agente aprende de su experiencia, ajustando sus decisiones en función del entorno.

- Objetivos del Proyecto

1. Clasificación con Aprendizaje por Refuerzo
   Desarrollar un agente RL capaz de clasificar canciones automáticamente en géneros musicales (como rock, jazz, electrónica, etc.), utilizando características extraídas de audio como:

   - Tempo (BPM)
   - Nivel de energía (RMS)
   - Centroide espectral
   - Coeficientes MFCC

2. Optimización de la Política de Clasificación
   Implementar un proceso de optimización que permita al agente mejorar continuamente su política de decisión con base en las recompensas obtenidas. Esto permite:

   - Reducir errores de clasificación.
   - Aprender estrategias más eficientes sin supervisión directa.

- Relación entre Clasificación y Optimización en RL

  - Clasificación: Es la tarea principal del agente, por ejemplo, etiquetar correctamente una canción como "rock".
  - Optimización: Es el proceso mediante el cual el agente ajusta su comportamiento para maximizar recompensas, es decir, mejorar la precisión de clasificación con el tiempo.

  Mientras la clasificación es lo que hace el agente, la optimización es cómo lo mejora.

## Estructura del Proyecto

# Extracción de características de audio

Este comando permite procesar automáticamente archivos .wav organizados por carpetas (donde cada carpeta representa un género musical), extraer características acústicas de cada canción usando librosa, y guardar los resultados en la base de datos a través del modelo SongFeature.

- Cómo usarlo
  python manage.py <nombre_del_comando> <ruta_a_datos> --workers <num_hilos>

  <nombre_del_comando>: Nombre del archivo del comando (sin .py).
  <ruta_a_datos>: Ruta al directorio principal que contiene carpetas por género, cada una con archivos .wav.
  --workers: (Opcional) Número de hilos para paralelizar el procesamiento. Por defecto: 4.

- Estructura esperada del directorio:
  dataset/
  │
  ├── rock/
  │ ├── song1.wav
  │ └── song2.wav
  │
  ├── jazz/
  │ ├── song3.wav
  │ └── song4.wav
  │
  └── ...

- ¿Qué hace el comando paso a paso?

  1.  Recorre carpetas por género
      Cada subdirectorio dentro del data_path representa un género musical.
      Dentro de cada carpeta se procesan todos los archivos .wav.

  2.  Procesa cada canción
      Para cada archivo .wav, se realiza lo siguiente:
      Se carga el audio (en mono, a 22.050 Hz, hasta 30 segundos).
      Se extraen características acústicas con librosa:

      - tempo: ritmo estimado (en BPM).
      - rms: energía promedio del audio.
      - centroid: centroide espectral promedio (frecuencia central del espectro).
      - mfccs: 20 coeficientes cepstrales de Mel (MFCCs), promedio de cada uno.

      Se crea un diccionario con las características, el nombre del archivo y su género.

  3.  Evita duplicados
      Antes de procesar un archivo, verifica si ya existe en la base de datos usando su nombre (filename). Si ya fue procesado, lo omite.

  4.  Ejecuta en paralelo
      Usa ThreadPoolExecutor para procesar múltiples canciones al mismo tiempo, lo que acelera significativamente la ejecución en grandes datasets. También muestra una barra de progreso con tqdm.

  5.  Guarda en la base de datos
      Filtra resultados válidos (descarta errores y duplicados).

  - def add_arguments(self, parser):
    Permite que el comando reciba parámetros personalizados cuando lo ejecutas con python manage.py.

    data_path (obligatorio): Ruta al directorio con subcarpetas por género.
    --workers (opcional): Número de hilos para procesar archivos en paralelo

- def process_song(self, file_path, genre):
  Procesa un solo archivo .wav para extraer sus características acústicas con librosa.
  Carga el archivo de audio (mono, 22050 Hz, duración máxima de 30 s).

  Extrae:

  - tempo: velocidad o BPM.
  - rms: nivel de energía.
  - centroid: centro de gravedad del espectro de frecuencias.
  - mfccs: 20 coeficientes MFCC promedio.

  Devuelve un diccionario listo para guardarse en la base de datos.
  Evita duplicados: Si el archivo ya está registrado en el modelo SongFeature, lo omite.

- def handle(self, \*args, \*\*options):
  Es el método principal del comando, se ejecuta cuando usas el comando en consola.
  Lee los argumentos (data_path y workers) desde options.

  1. Busca todos los archivos .wav en las subcarpetas (géneros).
  2. Crea tareas para procesar cada archivo (jobs).
  3. Ejecuta esas tareas en paralelo usando ThreadPoolExecutor.
  4. Muestra barra de progreso con tqdm.
  5. Filtra resultados válidos (descarta errores o duplicados).
  6. Guarda los datos en la base de datos en bloque (bulk_create).
  7. Muestra mensajes de éxito o advertencia en consola.

# Entrenamiento de Agente - training.py

Este módulo permite entrenar un agente de Q-learning para clasificar canciones según su género, usando las características previamente extraídas y guardadas en la base de datos Django a través del modelo SongFeature.

- Cómo usarlo
  Este método debe llamarse desde un entorno de desarrollo (como un script Python o vista Django):

  python manage.py shell

  > > > from rl_agent.training import train_agent
  > > > train_agent(episodes=5000)

- ¿Qué hace el entrenamiento paso a paso?

1. Carga datos desde la base de datos

   songs = SongFeature.objects.all()

   - Recupera todos los registros de canciones almacenados en la tabla SongFeatured

2. Identifica géneros únicos

   genres = list(sorted(set(s.genre for s in songs)))
   genre_to_id = {g: i for i, g in enumerate(genres)}

   - Extrae una lista ordenada de los géneros disponibles en la base de datos.
   - Asigna un identificador entero a cada género (genre_to_id) para facilitar el entrenamiento.

3. Inicializa el agente de Q-learning

   agent = QLearningAgent(actions=genres)

   - Crea una instancia del agente, donde cada género es una acción que el agente puede tomar.

4. Prepara el conjunto de entrenamiento

   for song in songs:
   features = [song.tempo, song.rms, song.centroid, *song.mfccs]
   X.append(features)
   y.append(genre_to_id[song.genre])

   Para cada canción:
   Construye un vector con 23 características:

   - tempo: velocidad en BPM.
   - rms: energía del audio.
   - centroid: centroide espectral.
   - mfccs: 20 coeficientes MFCC.

   Guarda ese vector en X (datos de entrada).
   Almacena la etiqueta de género en y (como número entero).

5. Entrena al agente por episodios

   for episode in range(episodes):
   ...

   Por cada episodio:

   - a. Se elige una canción aleatoriamente.
     idx = np.random.randint(0, len(X))

   - b. Se transforma su vector de características en un estado discreto:
     state = agent.discretize_state(X[idx])

   - c. El agente elige una acción (género) según su política:
     action = agent.choose_action(state)

   - d. Se otorga una recompensa basada en si acertó o no:
     reward = 1 if action == y[idx] else -1

   - e. Se calcula el siguiente estado como el de la siguiente canción (usando wrap-around):
     next_state = agent.discretize_state(X[(idx + 1) % len(X)])

   - f. El agente actualiza su Q-table aplicando la fórmula de Q-learning:
     agent.learn(state, action, reward, next_state)

   - g. Se reduce epsilon gradualmente para disminuir la exploración:
     agent.epsilon = max(0.01, agent.epsilon \* 0.995)

6. Guarda el agente entrenado

   agent.save(save_path)

   - Guarda la Q-table y los parámetros del agente en un archivo .json.

7. Devuelve el agente

   return agent

   - Permite reutilizar el agente entrenado para hacer predicciones más adelante.

# Entrenamiento de Agente - agent.py

La clase QLearningAgent implementa la lógica de un agente que aprende con el algoritmo clásico Q-learning. Puede discretizar estados, elegir acciones, aprender de recompensas, y guardar/cargar su conocimiento desde archivo.

¿Qué hace esta clase?

1. Inicializa el agente

   **init**(self, actions, alpha, gamma, epsilon)

   - actions: Lista de acciones posibles (géneros musicales).
   - alpha: Tasa de aprendizaje (0 a 1).
   - gamma: Factor de descuento (cuánto valora el futuro).
   - epsilon: Tasa de exploración (probabilidad de tomar una acción aleatoria).
   - Crea una Q-table vacía con un defaultdict, que se llena dinámicamente.

2. Convierte características en estados discretos

   discretize_state(features)

   - Divide cada característica (tempo, rms, centroid, mfccs) en 10 bins.
   - Convierte cada valor continuo en un bin entero.
   - Devuelve un tuple de enteros que representa el estado actual.
   - Este estado discreto puede usarse como clave en la Q-table.

3. Elige una acción con ε-greedy

   choose_action(state)

   - Con probabilidad epsilon: elige una acción aleatoria (explora).
   - Con probabilidad 1 - epsilon: elige la acción con mayor valor Q (explota).
   - Usa np.argmax(...) para encontrar la mejor acción conocida hasta el momento.

4. Actualiza la Q-table con lo aprendido

   learn(state, action, reward, next_state)

   - Calcula el valor futuro esperado del siguiente estado.
   - Usa la fórmula:
     𝑄(𝑠,𝑎)←𝑄(𝑠,𝑎)+𝛼[𝑟- 𝛾 ⋅ max 𝑎 𝑄(𝑠′,𝑎′)−𝑄(𝑠,𝑎)] ó Q(s,a)←Q(s,a)+α[r+γ⋅ a max ​ Q(s′,a′)−Q(s,a)]
     - ¿Qué significa cada término?
       Símbolo -> Significado
       Q(s, a) -> Valor actual estimado de hacer acción a en estado s.
       r -> Recompensa obtenida por hacer esa acción.
       s' -> Estado siguiente (después de hacer la acción).
       a' -> Todas las acciones posibles en el siguiente estado.
       max Q(s', a') -> Mejor valor estimado desde el siguiente estado (valor futuro óptimo).
       α (alpha) -> Tasa de aprendizaje: cuánto peso damos a la nueva información (entre 0 y 1).
       γ (gamma) -> Factor de descuento: cuánto valoramos las recompensas futuras (también entre 0 y 1).
   - Actualiza la Q-table incrementando el valor correspondiente a la acción tomada en el estado actual.

5. Guarda el modelo en disco

   save(path)

   - Convierte la Q-table (diccionario de tuplas → listas) en un JSON y lo guarda junto con los parámetros del agente.

6. Carga un modelo desde disco

   load(path)

   - Reconstruye un agente Q-learning desde un archivo .json, restaurando su Q-table y sus parámetros originales.

# Endpoint - views.py

Este módulo implementa una vista Django (classify) que recibe un archivo de audio .wav, extrae sus características acústicas usando librosa, y utiliza un agente Q-learning previamente entrenado para predecir su género musical.

- Cómo usarlo
  Método HTTP: POST
  Ruta: /classify (según tu configuración de urls.py)
  Encabezados requeridos: Ninguno especial
  Parámetros:
  audio: archivo .wav subido como multipart/form-data.

- ¿Qué hace este módulo paso a paso?

1. Carga el agente de Q-learning
   AGENT = QLearningAgent.load('q_agent.json')

   - Al importar el módulo, se carga automáticamente el agente entrenado desde el archivo q_agent.json.
   - Este agente contiene la Q-table y la lista de géneros que puede predecir.

2. Define la vista classify

   @csrf_exempt
   def classify(request):

   - La vista está exenta del token CSRF para permitir pruebas con herramientas como Postman o curl.
   - Solo responde a peticiones POST.

3. Valida y procesa el archivo recibido

   if request.method == 'POST' and request.FILES.get('audio'):

   - Verifica que:
     - La solicitud sea POST.
     - Contenga un archivo con clave audio.

4. Carga y preprocesa el audio

   y, sr = librosa.load(audio, sr=22050, mono=True)

   - Convierte el audio en un vector monoaural (y) con frecuencia de muestreo fija (sr = 22050 Hz).
   - Esto garantiza que todos los audios se analicen bajo las mismas condiciones.

5. Extrae las características acústicas

   features = [
   librosa.beat.beat_track(y=y, sr=sr)[0], # tempo (BPM)
   librosa.feature.rms(y=y).mean(), # rms (energía promedio)
   librosa.feature.spectral_centroid(y=y, sr=sr).mean(), # centroid (frecuencia promedio)
   \*librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20).mean(axis=1) # 20 MFCCs
   ]

   - Se extraen 23 características en total:
     1 tempo
     1 rms
     1 centroid
     20 MFCCs (media de cada uno)

curl.exe -X POST -F "audio=@C:\Users\usser\Documents\Proyectos\Clasificacion de Musicas\SongClassification-IA-1-2025\Backend\songClassifier\media\pop\pop.00016.wav" http://127.0.0.1:8000/classify/
