from django.db import models


class SongFeature(models.Model):
    filename = models.CharField(max_length=200, unique=True, db_index=True)
    genre = models.CharField(max_length=50, db_index=True)
    tempo = models.FloatField()
    rms = models.FloatField(verbose_name="Energy")  # RMS representa energía
    centroid = models.FloatField(verbose_name="Spectral Centroid")
    mfccs = models.JSONField()  # Almacena todos los MFCCs en un solo campo

    class Meta:
        db_table = 'song_features'
        verbose_name = 'Song Feature'
        verbose_name_plural = 'Song Features'
        indexes = [
            models.Index(fields=['genre']),
            models.Index(fields=['tempo']),
        ]

    def __str__(self):
        return f"{self.filename} - {self.genre}"

    def save(self, *args, **kwargs):
        # Validación adicional si es necesaria
        if not self.filename.lower().endswith('.wav'):
            self.filename += '.wav'
        super().save(*args, **kwargs)
