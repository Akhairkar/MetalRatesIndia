/* Chart helpers — requires Chart.js (loaded via CDN in each page) */

function filterHistory(history, range){
  const n = { '7D': 7, '30D': 30, '1Y': 365 }[range] || 30;
  return history.slice(-n);
}

function drawSparkline(canvas, history, color){
  if(!canvas || !window.Chart) return null;
  const data = history.slice(-30);
  const rising = data[data.length-1].rate >= data[0].rate;
  const lineColor = color || (rising ? '#35c98f' : '#ff5c5c');
  return new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: {
      labels: data.map(d => d.date),
      datasets: [{
        data: data.map(d => d.rate),
        borderColor: lineColor,
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.35,
        fill: true,
        backgroundColor: (ctx) => {
          const g = ctx.chart.ctx.createLinearGradient(0,0,0,44);
          g.addColorStop(0, lineColor + '33');
          g.addColorStop(1, lineColor + '00');
          return g;
        }
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: { x: { display:false }, y: { display:false } },
      plugins: { legend: { display:false }, tooltip: { enabled:false } },
      elements: { line: { capBezierPoints: true } }
    }
  });
}

function drawMainChart(canvas, seriesList, range){
  if(!canvas || !window.Chart) return null;
  const palette = ['#ff7a30','#35c98f','#c7c9cc','#d4af37','#7d8a94'];
  const datasets = seriesList.map((s, i) => {
    const data = filterHistory(s.history, range);
    return {
      label: s.name,
      data: data.map(d => d.rate),
      borderColor: s.color || palette[i % palette.length],
      backgroundColor: 'transparent',
      borderWidth: 2.4,
      pointRadius: 0,
      tension: 0.3,
      _labels: data.map(d => d.date)
    };
  });
  const labels = datasets.length ? datasets[0]._labels : [];
  return new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode:'index', intersect:false },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,.05)' },
          ticks: { color:'#5f6b78', maxTicksLimit: 8, font:{ family:'JetBrains Mono', size:10 } }
        },
        y: {
          grid: { color: 'rgba(255,255,255,.05)' },
          ticks: { color:'#5f6b78', font:{ family:'JetBrains Mono', size:10 } }
        }
      },
      plugins: {
        legend: { display: seriesList.length > 1, labels:{ color:'#9aa5b1', boxWidth:10, font:{ size:11 } } },
        tooltip: {
          backgroundColor:'#171d25', borderColor:'#262e38', borderWidth:1,
          titleColor:'#eef1f4', bodyColor:'#eef1f4', padding:10,
          callbacks: { label: (ctx) => `${ctx.dataset.label}: ₹${ctx.formattedValue}` }
        }
      }
    }
  });
}
