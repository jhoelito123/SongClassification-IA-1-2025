from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import librosa
import numpy as np
import os
from rl_agent.agent import QLearningAgent

# Cargar el agente entrenado al iniciar el servidor
# El archivo 'q_agent.json' debe contener la Q-table y parámetros del modelo
AGENT = QLearningAgent.load('q_agent.json')


@csrf_exempt  # Permite peticiones POST desde diferentes dominios
def classify(request):
    """
    Endpoint API para clasificación de géneros musicales.

    Procesa un archivo de audio recibido y devuelve la predicción de género
    utilizando el agente Q-learning entrenado.

    Método: POST
    Parámetros:
    - audio: Archivo de audio en formato WAV

    Respuestas:
    - 200: Éxito {status, genre, features}
    - 400: Error en procesamiento {status, message}
    - 405: Método no permitido
    """

    if request.method == 'POST' and request.FILES.get('audio'):
        try:
            # =============================================
            # 1. PROCESAMIENTO DEL AUDIO
            # =============================================
            audio_file = request.FILES['audio']

            # Configuración del procesamiento de audio:
            # - sr=22050: Frecuencia de muestreo estándar
            # - mono=True: Conversión a mono (1 canal)
            y, sr = librosa.load(audio_file, sr=22050, mono=True)

            # =============================================
            # 2. EXTRACCIÓN DE CARACTERÍSTICAS
            # =============================================
            # Las características deben coincidir exactamente con las usadas en entrenamiento
            features = [
                librosa.beat.beat_track(y=y, sr=sr)[0],  # Tempo (BPM)
                librosa.feature.rms(y=y).mean(),          # Energía promedio
                librosa.feature.spectral_centroid(
                    y=y, sr=sr).mean(),  # Centroide espectral
                # 20 MFCCs
                *librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20).mean(axis=1)
            ]

            # =============================================
            # 3. PREDICCIÓN DEL GÉNERO
            # =============================================
            # Convertir características a estado discreto (igual que en entrenamiento)
            state = AGENT.discretize_state(features)

            # Seleccionar acción (género) según política ε-greedy
            genre_id = AGENT.choose_action(state)
            predicted_genre = AGENT.actions[genre_id]

            # =============================================
            # 4. CONSTRUCCIÓN DE LA RESPUESTA
            # =============================================
            response_data = {
                'status': 'success',
                'genre': predicted_genre,
                'features': {
                    # Conversión explícita a float
                    'tempo': float(features[0]),
                    'energy': float(features[1]),     # para serialización JSON
                    'centroid': float(features[2])
                }
            }

            return JsonResponse(response_data)

        except librosa.util.exceptions.ParameterError as e:
            # Error específico de librosa (archivo de audio inválido)
            return JsonResponse({
                'status': 'error',
                'message': f'Formato de audio no válido: {str(e)}'
            }, status=400)

        except Exception as e:
            # Error genérico durante el procesamiento
            return JsonResponse({
                'status': 'error',
                'message': f'Error en el servidor: {str(e)}'
            }, status=400)

    # Si la petición no es POST o no contiene archivo
    return JsonResponse({
        'status': 'error',
        'message': 'Se requiere una petición POST con archivo de audio'
    }, status=405)
