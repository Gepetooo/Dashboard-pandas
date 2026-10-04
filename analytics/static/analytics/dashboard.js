const dadosGraficos = JSON.parse(
  document.getElementById('charts-data').textContent
);

const layoutBase = {
  paper_bgcolor: 'rgba(0, 0, 0, 0)',
  plot_bgcolor: 'rgba(0, 0, 0, 0)',
  font: {
    color: '#cbd4e6',
    family: 'Inter, system-ui, sans-serif',
    size: 11,
  },
  title: {
    font: {
      size: 15,
      color: '#f2f5fc',
    },
    x: 0.04,
    xanchor: 'left',
  },
  margin: {
    l: 58,
    r: 22,
    t: 54,
    b: 48,
  },
  legend: {
    orientation: 'h',
    y: -0.22,
  },
  xaxis: {
    gridcolor: '#26324a',
    zerolinecolor: '#26324a',
  },
  yaxis: {
    gridcolor: '#26324a',
    zerolinecolor: '#26324a',
  },
};

const identificadoresGraficos = [
  'class_survival',
  'age_distribution',
  'fare_distribution',
  'embark_survival',
  'age_trend',
  'correlation',
];

const opcoesGraficos = {
  responsive: true,
  displaylogo: false,
  locale: 'pt-br',
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
};

for (const identificador of identificadoresGraficos) {
  const elementoGrafico = document.getElementById(identificador);
  const configuracaoGrafico = dadosGraficos[identificador];

  Plotly.newPlot(
    elementoGrafico,
    configuracaoGrafico.data,
    {
      ...layoutBase,
      ...configuracaoGrafico.layout,
    },
    opcoesGraficos
  );
}
