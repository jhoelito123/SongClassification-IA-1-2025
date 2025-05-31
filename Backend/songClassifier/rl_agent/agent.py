import numpy as np
import json
import os
from collections import defaultdict


class QLearningAgent:
    """
    Implementación de un agente de Q-learning para clasificación de géneros musicales.
    Utiliza una tabla Q para almacenar los valores de estado-acción y aprende mediante
    el algoritmo estándar de Q-learning con exploración ε-greedy.
    """

    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.2):
        """
        Inicializa el agente con sus parámetros de aprendizaje.

        Args:
            actions (list): Lista de acciones posibles (géneros musicales)
            alpha (float): Tasa de aprendizaje (default: 0.1)
            gamma (float): Factor de descuento para recompensas futuras (default: 0.9)
            epsilon (float): Probabilidad inicial de exploración (default: 0.2)
        """
        self.actions = actions  # Espacio de acciones (géneros)
        self.alpha = alpha      # Controla la velocidad de aprendizaje
        self.gamma = gamma      # Importancia de recompensas futuras
        self.epsilon = epsilon  # Balance exploración/explotación

        # Tabla Q: Diccionario que mapea estados discretos a valores de acción
        # Usa defaultdict para inicializar nuevos estados con ceros
        self.q_table = defaultdict(lambda: np.zeros(len(actions)))

    def discretize_state(self, features):
        """
        Convierte un vector continuo de características en un estado discreto
        mediante la discretización de cada característica en intervalos.

        Args:
            features (list): Vector de características [tempo, rms, centroid, mfcc1...mcc20]

        Returns:
            tuple: Estado discreto representado como tupla de índices
        """
        discretized = []
        bins = 10  # Número de intervalos por característica

        # Rangos predefinidos para cada tipo de característica:
        ranges = [
            (50, 200),     # tempo (BPM)
            (0, 1),        # rms (energía normalizada)
            (100, 5000),   # centroid (Hz)
            *[(-300, 300) for _ in range(20)]  # MFCCs (valores típicos)
        ]

        # Discretización de cada característica
        for i, (min_val, max_val) in enumerate(ranges):
            value = features[i]
            # Asignación a intervalo usando digitize
            digit = np.digitize(value, np.linspace(min_val, max_val, bins))
            discretized.append(int(digit))  # Conversión explícita a entero

        return tuple(discretized)

    def choose_action(self, state):
        """
        Selecciona una acción según la política ε-greedy:
        - Con probabilidad ε: acción aleatoria (exploración)
        - De lo contrario: mejor acción conocida (explotación)

        Args:
            state (tuple): Estado discreto actual

        Returns:
            int: Índice de la acción seleccionada
        """
        if np.random.random() < self.epsilon:
            # Exploración: selección aleatoria uniforme
            return np.random.choice(len(self.actions))
        # Explotación: acción con máximo valor Q
        return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        """
        Actualiza la Q-table usando el algoritmo de Q-learning:
        Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]

        Args:
            state (tuple): Estado actual
            action (int): Acción tomada
            reward (float): Recompensa obtenida
            next_state (tuple): Estado siguiente
        """
        # Máximo valor Q para el siguiente estado
        best_next = np.max(self.q_table[next_state])

        # Target temporal difference
        td_target = reward + self.gamma * best_next

        # Error temporal difference
        td_error = td_target - self.q_table[state][action]

        # Actualización del valor Q
        self.q_table[state][action] += self.alpha * td_error

    def save(self, path):
        """
        Serializa el agente (Q-table y parámetros) a un archivo JSON.

        Args:
            path (str): Ruta del archivo de salida
        """
        with open(path, 'w') as f:
            json.dump({
                'q_table': {str(k): list(v) for k, v in self.q_table.items()},
                'params': {
                    'actions': self.actions,
                    'alpha': self.alpha,
                    'gamma': self.gamma,
                    'epsilon': self.epsilon
                }
            }, f, indent=2)

    @classmethod
    def load(cls, path):
        """
        Crea una instancia del agente desde un archivo JSON serializado.

        Args:
            path (str): Ruta del archivo serializado

        Returns:
            QLearningAgent or None: Agente reconstruido o None si el archivo no existe
        """
        if not os.path.exists(path):
            return None

        with open(path) as f:
            data = json.load(f)

        # Reconstrucción del agente
        agent = cls(
            actions=data['params']['actions'],
            alpha=data['params']['alpha'],
            gamma=data['params']['gamma'],
            epsilon=data['params']['epsilon']
        )

        # Reconstrucción de la Q-table
        agent.q_table = defaultdict(
            lambda: np.zeros(len(data['params']['actions'])),
            {eval(k): np.array(v) for k, v in data['q_table'].items()}
        )

        return agent
