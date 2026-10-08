import pandas as pd


NOMES_CLASSES = {1: 'Primeira', 2: 'Segunda', 3: 'Terceira'}
NOMES_SEXOS = {'female': 'Feminino', 'male': 'Masculino'}
CORES_SEXOS = {'female': '#65d6ad', 'male': '#8d9eff'}
CORES_DESFECHOS = {0: '#8d9eff', 1: '#65d6ad'}
ROTULOS_DESFECHOS = {0: 'Não sobreviveu', 1: 'Sobreviveu'}
FAIXAS_ETARIAS = ['0–11', '12–17', '18–29', '30–44', '45–59', '60+']
COLUNAS_CORRELACAO = {
    'survived': 'Sobreviveu',
    'pclass': 'Classe',
    'age': 'Idade',
    'fare': 'Tarifa',
    'sibsp': 'Irmãos/cônjuges',
    'parch': 'Pais/filhos',
}


def preparar_valores_json(valores):
    return [None if pd.isna(valor) else float(valor) for valor in valores]


def montar_grafico_sobrevivencia(passageiros):
    taxas = passageiros.groupby(['pclass', 'sex'], observed=True)['survived'].mean()
    series = []
    for sexo in sorted(passageiros['sex'].dropna().unique().tolist()):
        series.append({
            'type': 'bar',
            'name': NOMES_SEXOS.get(sexo, sexo.capitalize()),
            'x': [NOMES_CLASSES[classe] for classe in [1, 2, 3]],
            'y': [
                None if (classe, sexo) not in taxas.index
                else float(taxas.loc[(classe, sexo)] * 100)
                for classe in [1, 2, 3]
            ],
            'marker': {'color': CORES_SEXOS.get(sexo, '#8d9eff')},
            'hovertemplate': '%{x}<br>%{y:.1f}%<extra>%{fullData.name}</extra>',
        })
    return {
        'data': series,
        'layout': {
            'title': 'Taxa de sobrevivência por classe e sexo',
            'xaxis': {'title': 'Classe'},
            'yaxis': {'title': 'Sobrevivência (%)', 'ticksuffix': '%'},
            'barmode': 'group',
        },
    }


def montar_grafico_idades(passageiros):
    series = []
    for desfecho, rotulo in ROTULOS_DESFECHOS.items():
        idades = passageiros.loc[
            passageiros['survived'].eq(desfecho), 'age'
        ].dropna()
        series.append({
            'type': 'histogram',
            'name': rotulo,
            'x': preparar_valores_json(idades.tolist()),
            'xbins': {'size': 5},
            'marker': {'color': CORES_DESFECHOS[desfecho]},
            'opacity': 0.78,
        })
    return {
        'data': series,
        'layout': {
            'title': 'Distribuição de idade por desfecho',
            'xaxis': {'title': 'Idade (anos)'},
            'yaxis': {'title': 'Número de passageiros'},
            'barmode': 'overlay',
        },
    }


def montar_grafico_tarifas(passageiros):
    cores = ['#65d6ad', '#8d9eff', '#e3a86d']
    series = []
    for classe in [1, 2, 3]:
        tarifas = passageiros.loc[
            passageiros['pclass'].eq(classe), 'fare'
        ].dropna()
        series.append({
            'type': 'box',
            'name': NOMES_CLASSES[classe],
            'x': preparar_valores_json(tarifas.tolist()),
            'boxpoints': 'outliers',
            'marker': {'color': cores[classe - 1]},
            'orientation': 'h',
        })
    return {
        'data': series,
        'layout': {
            'title': 'Distribuição de tarifa por classe',
            'xaxis': {'title': 'Tarifa'},
            'yaxis': {'title': 'Classe'},
        },
    }


def montar_grafico_embarque(passageiros):
    dados_embarque = passageiros.assign(
        embark_town=passageiros['embark_town'].fillna('Não informado')
    )
    contagens = dados_embarque.groupby(
        ['embark_town', 'survived'], observed=True
    ).size()
    locais = sorted(dados_embarque['embark_town'].dropna().unique().tolist())
    series = []
    for desfecho, rotulo in ROTULOS_DESFECHOS.items():
        series.append({
            'type': 'bar',
            'name': rotulo,
            'x': locais,
            'y': [
                int(contagens.get((local, desfecho), 0))
                for local in locais
            ],
            'marker': {'color': CORES_DESFECHOS[desfecho]},
        })
    return {
        'data': series,
        'layout': {
            'title': 'Passageiros por local de embarque e desfecho',
            'xaxis': {'title': 'Local de embarque'},
            'yaxis': {'title': 'Número de passageiros'},
            'barmode': 'stack',
        },
    }


def montar_grafico_faixas_etarias(passageiros):
    dados_idade = passageiros.dropna(subset=['age']).copy()
    dados_idade['age_band'] = pd.cut(
        dados_idade['age'],
        bins=[0, 12, 18, 30, 45, 60, float('inf')],
        labels=FAIXAS_ETARIAS,
        right=False,
    )
    taxas = dados_idade.groupby(
        ['age_band', 'sex'], observed=True
    )['survived'].mean()
    series = []
    for sexo in sorted(dados_idade['sex'].dropna().unique().tolist()):
        series.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': NOMES_SEXOS.get(sexo, sexo.capitalize()),
            'x': FAIXAS_ETARIAS,
            'y': [
                None if (faixa, sexo) not in taxas.index
                else float(taxas.loc[(faixa, sexo)] * 100)
                for faixa in FAIXAS_ETARIAS
            ],
            'marker': {'color': CORES_SEXOS.get(sexo, '#8d9eff')},
            'hovertemplate': '%{x} anos<br>%{y:.1f}%<extra>%{fullData.name}</extra>',
        })
    return {
        'data': series,
        'layout': {
            'title': 'Taxa de sobrevivência por faixa etária e sexo',
            'xaxis': {'title': 'Faixa etária'},
            'yaxis': {'title': 'Sobrevivência (%)', 'ticksuffix': '%'},
            'hovermode': 'x unified',
        },
    }


def montar_grafico_correlacao(passageiros):
    correlacao = passageiros[list(COLUNAS_CORRELACAO)].corr(method='pearson')
    rotulos = [COLUNAS_CORRELACAO[coluna] for coluna in correlacao.columns]
    valores = [
        [None if pd.isna(valor) else float(valor) for valor in linha]
        for linha in correlacao.to_numpy().tolist()
    ]
    textos = [
        ['' if pd.isna(valor) else f'{valor:.2f}' for valor in linha]
        for linha in correlacao.to_numpy().tolist()
    ]
    return {
        'data': [{
            'type': 'heatmap',
            'x': rotulos,
            'y': rotulos,
            'z': valores,
            'text': textos,
            'texttemplate': '%{text}',
            'zmin': -1,
            'zmax': 1,
            'colorscale': 'RdBu',
            'reversescale': True,
            'colorbar': {'title': 'r'},
            'hovertemplate': '%{y} × %{x}<br>r = %{z:.2f}<extra></extra>',
        }],
        'layout': {
            'title': 'Correlação de Pearson entre variáveis',
            'xaxis': {'side': 'bottom'},
            'yaxis': {'autorange': 'reversed'},
        },
    }


def montar_graficos(passageiros):
    return {
        'class_survival': montar_grafico_sobrevivencia(passageiros),
        'age_distribution': montar_grafico_idades(passageiros),
        'fare_distribution': montar_grafico_tarifas(passageiros),
        'embark_survival': montar_grafico_embarque(passageiros),
        'age_trend': montar_grafico_faixas_etarias(passageiros),
        'correlation': montar_grafico_correlacao(passageiros),
    }