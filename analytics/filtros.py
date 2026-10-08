import pandas as pd


def converter_numero(valor, padrao):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


def obter_filtros(frame, parametros):
    idade_minima = float(frame['age'].min())
    idade_maxima = float(frame['age'].max())
    idade_inicial = max(
        idade_minima,
        min(idade_maxima, converter_numero(parametros.get('age_min'), idade_minima)),
    )
    idade_final = max(
        idade_inicial,
        min(idade_maxima, converter_numero(parametros.get('age_max'), idade_maxima)),
    )
    opcoes_sexo = sorted(frame['sex'].dropna().unique().tolist())
    sexo_selecionado = parametros.get('sex', 'all')
    if sexo_selecionado not in opcoes_sexo:
        sexo_selecionado = 'all'
    classe_selecionada = parametros.get('passenger_class', 'all')
    if classe_selecionada not in {'all', '1', '2', '3'}:
        classe_selecionada = 'all'

    return {
        'sex_options': opcoes_sexo,
        'selected_sex': sexo_selecionado,
        'selected_class': classe_selecionada,
        'age_min': idade_inicial,
        'age_max': idade_final,
        'minimum_age': idade_minima,
        'maximum_age': idade_maxima,
    }


def filtrar_passageiros(frame, filtros):
    passageiros = frame[
        frame['age'].isna()
        | frame['age'].between(filtros['age_min'], filtros['age_max'])
    ]
    if filtros['selected_sex'] != 'all':
        passageiros = passageiros[
            passageiros['sex'].eq(filtros['selected_sex'])
        ]
    if filtros['selected_class'] != 'all':
        passageiros = passageiros[
            passageiros['pclass'].eq(int(filtros['selected_class']))
        ]
    return passageiros