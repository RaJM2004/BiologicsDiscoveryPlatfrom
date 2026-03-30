// Dashboard Visualizations - Enhanced for Senior Lead Research View

document.addEventListener('DOMContentLoaded', () => {
    initRealTimeChart();
    startActivityFeed();
    startStatsPolling();
    initPipelineChart();
});

let pipelinePlot = null;

// 1. Plotly Real-Time Molecular Throughput
function initRealTimeChart() {
    const chartDiv = document.getElementById('throughput-chart');
    if (!chartDiv) return;

    let times = [];
    let y_values = [];
    let now = new Date();

    for (let i = 30; i > 0; i--) {
        times.push(new Date(now - i * 60000));
        y_values.push(100 + Math.random() * 50);
    }

    const data = [{
        x: times,
        y: y_values,
        mode: 'lines',
        fill: 'tozeroy',
        line: { color: '#3b82f6', width: 2 },
        fillcolor: 'rgba(59, 130, 246, 0.05)'
    }];

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 40, r: 20, t: 10, b: 30 },
        xaxis: { color: '#64748b', showgrid: false },
        yaxis: { color: '#64748b', gridcolor: '#1e293b', title: 'Mols/Sec' }
    };

    Plotly.newPlot(chartDiv, data, layout, { responsive: true, displayModeBar: false });

    setInterval(() => {
        const time = new Date();
        const throughput = 120 + Math.random() * 80;
        Plotly.extendTraces(chartDiv, { x: [[time]], y: [[throughput]] }, [0]);
        if (times.length > 50) {
            Plotly.relayout(chartDiv, { xaxis: { range: [new Date(time - 15 * 1000), time] } });
        }
    }, 2000);
}

// 2. Discovery Pipeline Maturity Chart (Horizontal Bar)
function initPipelineChart() {
    const chartDiv = document.getElementById('pipeline-chart');
    if (!chartDiv) return;

    const data = [{
        type: 'bar',
        x: [0, 0, 0, 0],
        y: ['ID', 'MAP', 'OPT', 'TOX'],
        orientation: 'h',
        marker: {
            color: ['#3b82f6', '#0ea5e9', '#8b5cf6', '#4ade80'],
            opacity: 0.8
        }
    }];

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 50, r: 20, t: 10, b: 30 },
        height: 300,
        xaxis: { color: '#64748b', showgrid: true, gridcolor: '#1e293b' },
        yaxis: { color: '#94a3b8', font: { size: 10 } }
    };

    Plotly.newPlot(chartDiv, data, layout, { responsive: true, displayModeBar: false });
    pipelinePlot = chartDiv;
}

// 3. Platform Stats & Pipeline Items
function startStatsPolling() {
    const updateStats = async () => {
        try {
            const res = await fetch('http://127.0.0.1:8000/api/monitoring/stats');
            if (res.ok) {
                const data = await res.json();
                
                // Top Metrics
                document.getElementById('sys-health').innerText = data.system_health;
                document.getElementById('daily-mols').innerText = data.daily_throughput.toLocaleString();
                document.getElementById('screening-count').innerText = data.active_ai_jobs;
                document.getElementById('gpu-load').innerText = data.gpu_load;
                
                // GPU Bar
                const gpuVal = parseFloat(data.gpu_load);
                document.getElementById('gpu-bar').style.width = gpuVal + '%';

                // Update Pipeline Chart
                if (data.pipeline && pipelinePlot) {
                    const counts = [
                        data.pipeline["Target Discovery"] || 0,
                        data.pipeline["Structural Mapping"] || 0,
                        data.pipeline["Lead Optimization"] || 0,
                        data.pipeline["ADMET Profiling"] || 0
                    ];
                    Plotly.restyle(pipelinePlot, { x: [counts] }, [0]);
                }

                // Render Top Candidates
                if (data.top_candidates && Array.isArray(data.top_candidates)) {
                    renderTopCandidates(data.top_candidates);
                } else {
                    renderTopCandidates([]);
                }

                const statusEl = document.getElementById('api-status');
                if (statusEl) {
                    statusEl.innerText = "CLUSTER: " + data.cluster_status;
                    statusEl.style.borderColor = data.cluster_status === "Operational" ? "#4ade80" : "#fbbf24";
                    statusEl.style.color = data.cluster_status === "Operational" ? "#4ade80" : "#fbbf24";
                }
            }
        } catch (e) {
            console.error("Stats Poll Error:", e);
        }
    };

    updateStats();
    setInterval(updateStats, 5000);
}

function renderTopCandidates(candidates) {
    const container = document.getElementById('top-candidates-list');
    if (!container) return;

    if (candidates.length === 0) {
        container.innerHTML = '<div class="text-xs text-slate-500 text-center mt-10">No lead candidates validated yet.</div>';
        return;
    }

    container.innerHTML = candidates.map(c => `
        <div class="flex items-center justify-between p-3 border-b border-slate-800/50 hover:bg-slate-800/30 transition">
            <div>
                <div class="text-[10px] text-blue-400 font-bold uppercase tracking-tighter">${c.target}</div>
                <div class="text-xs font-mono text-slate-200">${c.smiles.substring(0, 20)}...</div>
            </div>
            <div class="text-right">
                <div class="text-sm font-bold text-emerald-400">${c.affinity} <span class="text-[8px]">pIC50</span></div>
                <div class="text-[10px] text-slate-500">${c.model}</div>
            </div>
        </div>
    `).join('');
}

// 4. Activity Logs (Filtered)
async function startActivityFeed() {
    const feedContainer = document.getElementById('activity-feed');
    if (!feedContainer) return;

    const updateFeed = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
            const res = await fetch('http://127.0.0.1:8000/api/screening/', { headers });
            
            if (!res.ok) return;
            const data = await res.json();
            
            if (!Array.isArray(data)) return;

            const activities = data.slice(0, 10).map(d => ({
                job: (d._id || '').substring(0, 6),
                status: d.status || 'PENDING',
                target: d.target_id || 'UNKNOWN'
            }));

            feedContainer.innerHTML = activities.map(a => `
                <div class="font-mono mb-2 flex justify-between">
                    <span class="text-slate-500">[${new Date().toLocaleTimeString()}]</span>
                    <span class="text-blue-300">JOB_${a.job}</span>
                    <span class="text-slate-200">/ ${a.target}</span>
                    <span class="${a.status === 'Completed' ? 'text-emerald-400' : 'text-yellow-400'}">${a.status.toUpperCase()}</span>
                </div>
            `).join('');
        } catch (e) { }
    };

    updateFeed();
    setInterval(updateFeed, 8000);
}
