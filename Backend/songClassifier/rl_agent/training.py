from songClasfBackend.models import SongFeature
from .agent import QLearningAgent
import numpy as np


def train_agent(episodes=1000, save_path='q_agent.json'):
    """
    Entrena un agente de Q-learning para clasificación automática de géneros musicales
    utilizando las características acústicas almacenadas en la base de datos.

    Args:
        episodes (int): Número de iteraciones de entrenamiento (default: 1000)
        save_path (str): Ruta para guardar el modelo entrenado (default: 'q_agent.json')

    Returns:
        QLearningAgent: Instancia del agente entrenado
    """

    # Paso 1: Preparación de datos
    # --------------------------------------------
    # Obtención de todas las canciones procesadas
    songs = SongFeature.objects.all()

    # Identificación de géneros únicos y creación de mapeo numérico
    genres = list(sorted(set(s.genre for s in songs)))
    genre_to_id = {g: i for i, g in enumerate(genres)}

    # Paso 2: Inicialización del agente
    # --------------------------------------------
    # Creación del agente con los géneros como espacio de acciones
    agent = QLearningAgent(actions=genres)

    # Paso 3: Preparación del conjunto de entrenamiento
    # --------------------------------------------
    # Construcción de matrices de características (X) y etiquetas (y)
    X = []  # Lista de vectores de características
    y = []  # Lista de IDs de géneros (etiquetas)

    for song in songs:
        # Creación del vector de características combinando:
        # - Características temporales (tempo)
        # - Características espectrales (RMS, centroid)
        # - Coeficientes MFCC (timbre)
        features = [
            song.tempo,
            song.rms,
            song.centroid,
            *song.mfccs  # Desempaquetado de los 20 coeficientes MFCC
        ]
        X.append(features)
        y.append(genre_to_id[song.genre])

    # Paso 4: Ciclo de entrenamiento
    # --------------------------------------------
    for episode in range(episodes):
        # Muestreo aleatorio de una canción
        idx = np.random.randint(0, len(X))

        # Transformación de características a estado discreto
        state = agent.discretize_state(X[idx])

        # Selección de acción según política ε-greedy
        action = agent.choose_action(state)

        # Cálculo de recompensa (+1 acierto, -1 error)
        reward = 1 if action == y[idx] else -1

        # Obtención del siguiente estado (con wrap-around)
        next_state = agent.discretize_state(X[(idx + 1) % len(X)])

        # Actualización de la Q-table
        agent.learn(state, action, reward, next_state)

        # Decaimiento de ε: Reducción progresiva de la exploración
        agent.epsilon = max(0.01, agent.epsilon * 0.995)

    # Paso 5: Persistencia del modelo
    # --------------------------------------------
    # Guardado del agente entrenado en disco
    agent.save(save_path)

    return agent
