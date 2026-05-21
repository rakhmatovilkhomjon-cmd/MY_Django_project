(function () {
  const CHART_COLORS = [
    "rgba(2, 132, 199, 0.85)",
    "rgba(5, 150, 105, 0.85)",
    "rgba(79, 70, 229, 0.85)",
    "rgba(217, 119, 6, 0.85)",
    "rgba(220, 38, 38, 0.85)",
  ];

  function buildChartConfig(kind, spec) {
    const datasets = (spec.datasets || []).map((ds, i) => ({
      label: ds.label,
      data: ds.data,
      backgroundColor: kind === "line" ? CHART_COLORS[i % CHART_COLORS.length] : CHART_COLORS[i % CHART_COLORS.length],
      borderColor: CHART_COLORS[i % CHART_COLORS.length],
      borderWidth: kind === "line" ? 2 : 1,
      fill: false,
      tension: 0.2,
    }));

    return {
      type: kind === "pie" ? "pie" : kind,
      data: {
        labels: spec.labels || [],
        datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: kind === "pie" ? 1.4 : 1.8,
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } },
          title: { display: false },
        },
        scales:
          kind === "pie"
            ? {}
            : {
                x: {
                  title: { display: !!spec.xLabel, text: spec.xLabel || "" },
                  grid: { color: "rgba(15, 23, 42, 0.06)" },
                },
                y: {
                  beginAtZero: true,
                  title: { display: !!spec.yLabel, text: spec.yLabel || "" },
                  grid: { color: "rgba(15, 23, 42, 0.06)" },
                },
              },
      },
    };
  }

  function initWritingCharts() {
    if (typeof Chart === "undefined") return;
    document.querySelectorAll(".writing-chart-canvas").forEach((canvas) => {
      if (canvas.dataset.chartInitialized === "1") return;
      const scriptId = canvas.dataset.chartScript;
      const kind = canvas.dataset.chartKind;
      if (!scriptId || !kind) return;
      const el = document.getElementById(scriptId);
      if (!el) return;
      let spec;
      try {
        spec = JSON.parse(el.textContent);
      } catch (e) {
        return;
      }
      canvas.dataset.chartInitialized = "1";
      new Chart(canvas.getContext("2d"), buildChartConfig(kind, spec));
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWritingCharts);
  } else {
    initWritingCharts();
  }
  window.initWritingCharts = initWritingCharts;
})();
