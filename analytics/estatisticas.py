import pandas as pd


COLUNAS_AUSENTES = {
    'age': 'Idade',
    'embarked': 'Código do porto',
    'embark_town': 'Cidade de embarque',
    'deck': 'Convés',
    'fare': 'Tarifa',
}
COLUNAS_DESCRITIVAS = {
    'age': 'Idade',
    'fare': 'Tarifa',
    'sibsp': 'Irmãos/cônjuges a bordo',
    'parch': 'Pais/filhos a bordo',
}


def contar_tarifas_atipicas(tarifas):
    valores = tarifas.dropna()
    if valores.empty:
        return 0
    primeiro_quartil = valores.quantile(0.25)
    terceiro_quartil = valores.quantile(0.75)
    intervalo = terceiro_quartil - primeiro_quartil
    limite_inferior = primeiro_quartil - 1.5 * intervalo
    limite_superior = terceiro_quartil + 1.5 * intervalo
    atipicas = (valores < limite_inferior) | (valores > limite_superior)
    return int(atipicas.sum())


def montar_tabela_descritiva(passageiros):
    resumo = passageiros[list(COLUNAS_DESCRITIVAS)].describe()
    tabela = []
    for coluna, rotulo in COLUNAS_DESCRITIVAS.items():
        medidas = resumo[coluna]
        tabela.append({
            'label': rotulo,
            'count': int(medidas['count']),
            'mean': None if pd.isna(medidas['mean']) else float(medidas['mean']),
            'std': None if pd.isna(medidas['std']) else float(medidas['std']),
            'min': None if pd.isna(medidas['min']) else float(medidas['min']),
            'median': None if pd.isna(medidas['50%']) else float(medidas['50%']),
            'max': None if pd.isna(medidas['max']) else float(medidas['max']),
        })
    return tabela


def calcular_estatisticas(passageiros):
    taxa_sobrevivencia = (
        float(passageiros['survived'].mean() * 100)
        if not passageiros.empty
        else None
    )
    mediana_tarifa = (
        float(passageiros['fare'].median())
        if passageiros['fare'].notna().any()
        else None
    )
    valores_ausentes = [
        {
            'label': rotulo,
            'percent': round(float(passageiros[coluna].isna().mean() * 100), 1),
        }
        for coluna, rotulo in COLUNAS_AUSENTES.items()
    ]
    resumo = {
        'count': int(len(passageiros)),
        'survivors': int(passageiros['survived'].sum()),
        'survival_rate': round(taxa_sobrevivencia, 1) if taxa_sobrevivencia is not None else None,
        'median_fare': round(mediana_tarifa, 2) if mediana_tarifa is not None else None,
        'outliers': contar_tarifas_atipicas(passageiros['fare']),
    }
    return {
        'descriptive': resumo,
        'descriptive_table': montar_tabela_descritiva(passageiros),
        'missingness': valores_ausentes,
    }