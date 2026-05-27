async function loadRuntimeData() {
  const targets = [
    '../out/statistics_pca_report.json',
    '../out/runtime_diff.json',
    '../out/deployment_readiness.json',
    '../out/reality_tracker.json'
  ];

  const results = {};

  for (const target of targets) {
    try {
      const response = await fetch(target, { cache: 'no-store' });
      results[target] = await response.json();
    } catch (error) {
      results[target] = { error: String(error) };
    }
  }

  return results;
}

function renderTimeline(runtimeHistory) {
  if (!runtimeHistory || !runtimeHistory.length) {
    return;
  }

  const x = runtimeHistory.map(item => item.wave);
  const y = runtimeHistory.map(item => item.bridge_completion || 0);

  Plotly.newPlot('timeline_chart', [{
    x,
    y,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Bridge Completion'
  }], {
    title: 'Federation Runtime Timeline',
    yaxis: { range: [0, 100] }
  });
}

async function hydrateRuntimeDashboard() {
  const data = await loadRuntimeData();

  const deployment = data['../out/deployment_readiness.json'];
  const reality = data['../out/reality_tracker.json'];

  const deploymentScore = deployment.completion_percent || 0;
  const realityScore = reality.average_actual || 0;

  Plotly.newPlot('hydration_chart', [{
    values: [deploymentScore, realityScore],
    labels: ['Deployment', 'Reality Alignment'],
    type: 'pie'
  }], {
    title: 'Runtime Hydration Overview'
  });

  try {
    const historyResponse = await fetch('../out/runtime_history.json', { cache: 'no-store' });
    const history = await historyResponse.json();
    renderTimeline(history);
  } catch (error) {
    console.error(error);
  }

  const updated = document.getElementById('last_updated');
  if (updated) {
    updated.textContent = new Date().toISOString();
  }
}

window.addEventListener('load', hydrateRuntimeDashboard);
