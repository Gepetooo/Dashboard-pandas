from django.shortcuts import render

from .data import DATASET_REPOSITORY_URL, DATASET_URL, carregar_conjunto_dados
from .estatisticas import calcular_estatisticas
from .filtros import filtrar_passageiros, obter_filtros
from .graficos import montar_graficos


def exibir_painel(request):
    try:
        frame = carregar_conjunto_dados()
    except Exception:
        return render(request, 'analytics/dashboard.html', {
            'error': 'Não foi possível carregar o arquivo CSV local. Confira se dashboard/data/titanic.csv está presente no projeto.',
            'source_url': DATASET_URL,
            'repository_url': DATASET_REPOSITORY_URL,
        })

    filtros = obter_filtros(frame, request.GET)
    passageiros = filtrar_passageiros(frame, filtros)
    estatisticas = calcular_estatisticas(passageiros)
    graficos = montar_graficos(passageiros)

    contexto = {
        'source_url': DATASET_URL,
        'repository_url': DATASET_REPOSITORY_URL,
        **filtros,
        **estatisticas,
        'charts': graficos,
    }
    return render(request, 'analytics/dashboard.html', contexto)