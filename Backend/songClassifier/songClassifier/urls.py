from django.contrib import admin
from django.urls import path
from songClasfBackend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('classify/', views.classify, name='classify'),
]
