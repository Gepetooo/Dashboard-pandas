from django.urls import path

from .views import exibir_painel

urlpatterns = [
    path('', exibir_painel, name='painel_analitico'),
]