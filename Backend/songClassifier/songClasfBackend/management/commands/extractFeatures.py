import os
import librosa
import numpy as np
from django.core.management.base import BaseCommand
from songClasfBackend.models import SongFeature
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


class Command(BaseCommand):
    """
    Comando de Django para procesar una biblioteca musical y extraer características acústicas.
    Procesa archivos .wav organizados en subdirectorios por género musical y almacena las
    características extraídas en la base de datos para su uso en el modelo de aprendizaje.
    """

    def add_arguments(self, parser):
        """
        Configura los argumentos del comando:
        - data_path: Ruta al directorio raíz que contiene subdirectorios por género musical
        - --workers: Número de procesos paralelos para el procesamiento (default: 4)
        """
        parser.add_argument(
            'data_path',
            type=str,
            help='Ruta al directorio que contiene subcarpetas por género musical'
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=4,
            help='Número de workers para procesamiento paralelo (default: 4)'
        )

    def process_song(self, file_path, genre):
        """
        Procesa un archivo de audio individual y extrae sus características acústicas.

        Args:
            file_path (str): Ruta completa al archivo .wav
            genre (str): Género musical obtenido del nombre del subdirectorio

        Returns:
            dict or None: Diccionario con metadatos y características si tiene éxito, 
                         None si el archivo ya existe o hay errores
        """
        try:
            filename = os.path.basename(file_path)

            # Verificación de duplicados en la base de datos
            if SongFeature.objects.filter(filename=filename).exists():
                return None

            # Configuración de procesamiento de audio:
            # - Frecuencia de muestreo estándar (22050 Hz)
            # - Conversión a mono (un solo canal)
            # - Duración máxima de procesamiento (30 segundos)
            y, sr = librosa.load(file_path, sr=22050, mono=True, duration=30)

            # Extracción de características clave:
            features = {
                # BPM (pulsaciones por minuto)
                'tempo': librosa.beat.beat_track(y=y, sr=sr)[0],
                # Energía promedio (volumen)
                'rms': librosa.feature.rms(y=y).mean(),
                # Brillantez del sonido
                'centroid': librosa.feature.spectral_centroid(y=y, sr=sr).mean(),
                # Firmas espectrales
                'mfccs': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20).mean(axis=1).tolist(),
            }

            return {
                'filename': filename,
                'genre': genre,
                **features
            }

        except Exception as e:
            # Registro detallado de errores manteniendo el flujo de ejecución
            self.stdout.write(self.style.ERROR(
                f"Error procesando {file_path}: {str(e)}"))
            return None

    def handle(self, *args, **options):
        """
        Método principal que ejecuta el flujo completo de procesamiento:
        1. Recorre la estructura de directorios
        2. Procesa archivos en paralelo
        3. Almacena resultados en la base de datos
        """
        data_path = options['data_path']
        workers = options['workers']
        jobs = []

        # Construcción de la lista de trabajos:
        # - Recorre cada subdirectorio (género)
        # - Identifica archivos .wav válidos
        for genre in os.listdir(data_path):
            genre_path = os.path.join(data_path, genre)

            if not os.path.isdir(genre_path):
                continue

            for filename in os.listdir(genre_path):
                if filename.lower().endswith(('.wav', '.mp3')):
                    jobs.append((
                        # Ruta completa al archivo
                        os.path.join(genre_path, filename),
                        genre  # Género obtenido del nombre del directorio
                    ))

        # Procesamiento paralelo con:
        # - Pool de workers configurable
        # - Barra de progreso visual
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(tqdm(
                executor.map(lambda x: self.process_song(*x), jobs),
                total=len(jobs),
                desc="Procesando canciones",
                unit="canción"
            ))

        # Filtrado de resultados válidos (excluyendo errores y duplicados)
        valid_results = [r for r in results if r is not None]

        if valid_results:
            # Inserción masiva optimizada en la base de datos
            SongFeature.objects.bulk_create([
                SongFeature(**song_data) for song_data in valid_results
            ])
            self.stdout.write(self.style.SUCCESS(
                f"Procesamiento completado. {len(valid_results)} canciones nuevas almacenadas."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "No se encontraron canciones nuevas para procesar."
            ))
