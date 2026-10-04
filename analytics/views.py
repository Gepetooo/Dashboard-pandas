import pandas as pd
from django.shortcuts import render

from .data import DATASET_URL, carregar_conjunto_dados


MISSING_COLUMNS = {
    'age': 'Idade',
    'embarked': 'Código do porto',
    'embark_town': 'Cidade de embarque',
    'deck': 'Convés',
    'fare': 'Tarifa',
}
DESCRIPTIVE_COLUMNS = {
    'age': 'Idade',
    'fare': 'Tarifa',
    'sibsp': 'Irmãos/cônjuges a bordo',
    'parch': 'Pais/filhos a bordo',
}
CORRELATION_COLUMNS = {
    'survived': 'Sobreviveu',
    'pclass': 'Classe',
    'age': 'Idade',
    'fare': 'Tarifa',
    'sibsp': 'Irmãos/cônjuges',
    'parch': 'Pais/filhos',
}


def converter_numero(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def preparar_valores_json(values):
    return [None if pd.isna(value) else float(value) for value in values]


def exibir_painel(request):
    try:
        frame = carregar_conjunto_dados()
    except Exception:
        return render(request, 'analytics/dashboard.html', {
            'error': 'Não foi possível carregar o arquivo CSV local. Confira se dashboard/data/titanic.csv está presente no projeto.',
            'source_url': DATASET_URL,
        })

    minimum_age = float(frame['age'].min())
    maximum_age = float(frame['age'].max())
    age_min = max(minimum_age, min(maximum_age, converter_numero(request.GET.get('age_min'), minimum_age)))
    age_max = max(age_min, min(maximum_age, converter_numero(request.GET.get('age_max'), maximum_age)))
    sex_options = sorted(frame['sex'].dropna().unique().tolist())
    sex = request.GET.get('sex', 'all')
    if sex not in sex_options:
        sex = 'all'
    passenger_class = request.GET.get('passenger_class', 'all')
    if passenger_class not in {'all', '1', '2', '3'}:
        passenger_class = 'all'
    filtered = frame[frame['age'].isna() | frame['age'].between(age_min, age_max)]
    if sex != 'all':
        filtered = filtered[filtered['sex'].eq(sex)]
    if passenger_class != 'all':
        filtered = filtered[filtered['pclass'].eq(int(passenger_class))]
    class_names = {1: 'Primeira', 2: 'Segunda', 3: 'Terceira'}
    sex_labels = {'female': 'Feminino', 'male': 'Masculino'}
    class_rates = filtered.groupby(['pclass', 'sex'], observed=True)['survived'].mean()
    survival_by_class = []
    for selected_sex in sorted(filtered['sex'].dropna().unique().tolist()):
        survival_by_class.append({
            'type': 'bar',
            'name': sex_labels.get(selected_sex, selected_sex.capitalize()),
            'x': [class_names[class_number] for class_number in [1, 2, 3]],
            'y': [
                None if (class_number, selected_sex) not in class_rates.index
                else float(class_rates.loc[(class_number, selected_sex)] * 100)
                for class_number in [1, 2, 3]
            ],
            'marker': {'color': '#65d6ad' if selected_sex == 'female' else '#8d9eff'},
            'hovertemplate': '%{x}<br>%{y:.1f}%<extra>%{fullData.name}</extra>',
        })

    age_data = []
    for survived, label, color in [(0, 'Não sobreviveu', '#8d9eff'), (1, 'Sobreviveu', '#65d6ad')]:
        ages = filtered.loc[filtered['survived'].eq(survived), 'age'].dropna()
        age_data.append({
            'type': 'histogram',
            'name': label,
            'x': preparar_valores_json(ages.tolist()),
            'xbins': {'size': 5},
            'marker': {'color': color},
            'opacity': 0.78,
        })

    fare_data = []
    for class_number in [1, 2, 3]:
        fares = filtered.loc[filtered['pclass'].eq(class_number), 'fare'].dropna()
        fare_data.append({
            'type': 'box',
            'name': class_names[class_number],
            'x': preparar_valores_json(fares.tolist()),
            'boxpoints': 'outliers',
            'marker': {'color': ['#65d6ad', '#8d9eff', '#e3a86d'][class_number - 1]},
            'orientation': 'h',
        })

    port_frame = filtered.assign(embark_town=filtered['embark_town'].fillna('Não informado'))
    port_counts = port_frame.groupby(['embark_town', 'survived'], observed=True).size()
    port_names = sorted(port_frame['embark_town'].dropna().unique().tolist())
    port_data = []
    for survived, label, color in [(0, 'Não sobreviveu', '#8d9eff'), (1, 'Sobreviveu', '#65d6ad')]:
        port_data.append({
            'type': 'bar',
            'name': label,
            'x': port_names,
            'y': [int(port_counts.get((port_name, survived), 0)) for port_name in port_names],
            'marker': {'color': color},
        })

    age_band_labels = ['0–11', '12–17', '18–29', '30–44', '45–59', '60+']
    age_bands = filtered.dropna(subset=['age']).copy()
    age_bands['age_band'] = pd.cut(
        age_bands['age'],
        bins=[0, 12, 18, 30, 45, 60, float('inf')],
        labels=age_band_labels,
        right=False,
    )
    age_band_rates = age_bands.groupby(['age_band', 'sex'], observed=True)['survived'].mean()
    age_trend_data = []
    for selected_sex in sorted(age_bands['sex'].dropna().unique().tolist()):
        age_trend_data.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': sex_labels.get(selected_sex, selected_sex.capitalize()),
            'x': age_band_labels,
            'y': [
                None if (age_band, selected_sex) not in age_band_rates.index
                else float(age_band_rates.loc[(age_band, selected_sex)] * 100)
                for age_band in age_band_labels
            ],
            'marker': {'color': '#65d6ad' if selected_sex == 'female' else '#8d9eff'},
            'hovertemplate': '%{x} anos<br>%{y:.1f}%<extra>%{fullData.name}</extra>',
        })

    correlation = filtered[list(CORRELATION_COLUMNS)].corr(method='pearson')
    correlation_labels = [CORRELATION_COLUMNS[column] for column in correlation.columns]
    correlation_values = [
        [None if pd.isna(value) else float(value) for value in row]
        for row in correlation.to_numpy().tolist()
    ]
    correlation_text = [
        ['' if pd.isna(value) else f'{value:.2f}' for value in row]
        for row in correlation.to_numpy().tolist()
    ]

    fare_values = filtered['fare'].dropna()
    first_quartile = fare_values.quantile(0.25) if not fare_values.empty else None
    third_quartile = fare_values.quantile(0.75) if not fare_values.empty else None
    outlier_count = 0
    if first_quartile is not None and third_quartile is not None:
        spread = third_quartile - first_quartile
        outlier_count = int(((fare_values < first_quartile - 1.5 * spread) | (fare_values > third_quartile + 1.5 * spread)).sum())
    survival_rate = float(filtered['survived'].mean() * 100) if not filtered.empty else None
    median_fare = float(filtered['fare'].median()) if filtered['fare'].notna().any() else None
    missingness = [
        {'label': label, 'percent': round(float(filtered[column].isna().mean() * 100), 1)}
        for column, label in MISSING_COLUMNS.items()
    ]
    numeric_summary = filtered[list(DESCRIPTIVE_COLUMNS)].describe()
    descriptive_table = []
    for column, label in DESCRIPTIVE_COLUMNS.items():
        summary = numeric_summary[column]
        descriptive_table.append({
            'label': label,
            'count': int(summary['count']),
            'mean': None if pd.isna(summary['mean']) else float(summary['mean']),
            'std': None if pd.isna(summary['std']) else float(summary['std']),
            'min': None if pd.isna(summary['min']) else float(summary['min']),
            'median': None if pd.isna(summary['50%']) else float(summary['50%']),
            'max': None if pd.isna(summary['max']) else float(summary['max']),
        })
    descriptive = {
        'count': int(len(filtered)),
        'survivors': int(filtered['survived'].sum()),
        'survival_rate': round(survival_rate, 1) if survival_rate is not None else None,
        'median_fare': round(median_fare, 2) if median_fare is not None else None,
        'outliers': outlier_count,
    }
    charts = {
        'class_survival': {'data': survival_by_class, 'layout': {'title': 'Taxa de sobrevivência por classe e sexo', 'xaxis': {'title': 'Classe'}, 'yaxis': {'title': 'Sobrevivência (%)', 'ticksuffix': '%'}, 'barmode': 'group'}},
        'age_distribution': {'data': age_data, 'layout': {'title': 'Distribuição de idade por desfecho', 'xaxis': {'title': 'Idade (anos)'}, 'yaxis': {'title': 'Número de passageiros'}, 'barmode': 'overlay'}},
        'fare_distribution': {'data': fare_data, 'layout': {'title': 'Distribuição de tarifa por classe', 'xaxis': {'title': 'Tarifa'}, 'yaxis': {'title': 'Classe'}}},
        'embark_survival': {'data': port_data, 'layout': {'title': 'Passageiros por local de embarque e desfecho', 'xaxis': {'title': 'Local de embarque'}, 'yaxis': {'title': 'Número de passageiros'}, 'barmode': 'stack'}},
        'age_trend': {'data': age_trend_data, 'layout': {'title': 'Taxa de sobrevivência por faixa etária e sexo', 'xaxis': {'title': 'Faixa etária'}, 'yaxis': {'title': 'Sobrevivência (%)', 'ticksuffix': '%'}, 'hovermode': 'x unified'}},
        'correlation': {'data': [{'type': 'heatmap', 'x': correlation_labels, 'y': correlation_labels, 'z': correlation_values, 'text': correlation_text, 'texttemplate': '%{text}', 'zmin': -1, 'zmax': 1, 'colorscale': 'RdBu', 'reversescale': True, 'colorbar': {'title': 'r'}, 'hovertemplate': '%{y} × %{x}<br>r = %{z:.2f}<extra></extra>'}], 'layout': {'title': 'Correlação de Pearson entre variáveis', 'xaxis': {'side': 'bottom'}, 'yaxis': {'autorange': 'reversed'}}},
    }
    context = {
        'source_url': DATASET_URL,
        'sex_options': sex_options,
        'selected_sex': sex,
        'selected_class': passenger_class,
        'age_min': age_min,
        'age_max': age_max,
        'minimum_age': minimum_age,
        'maximum_age': maximum_age,
        'descriptive': descriptive,
        'descriptive_table': descriptive_table,
        'missingness': missingness,
        'charts': charts,
    }
    return render(request, 'analytics/dashboard.html', context)