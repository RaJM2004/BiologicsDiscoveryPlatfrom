// Dashboard Visualizations

document.addEventListener('DOMContentLoaded', () => {
    initRealTimeChart();
    startActivityFeed();
    simulateGPULoad();
});

// 1. Plotly Real-Time Chart
function initRealTimeChart() {
    const chartDiv = document.getElementById('throughput-chart');

    // Initial Data
    let times = [];
    let y_values = [];
    let now = new Date();

    // Generate 30 mins of history
    for (let i = 30; i > 0; i--) {
        times.push(new Date(now - i * 60000));
        y_values.push(100 + Math.random() * 50);
    }

    const data = [{
        x: times,
        y: y_values,
        mode: 'lines',
        fill: 'tozeroy',
        line: { color: '#0ea5e9', width: 3 },
        fillcolor: 'rgba(14, 165, 233, 0.1)'
    }];

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 40, r: 20, t: 20, b: 40 },
        xaxis: {
            color: '#64748b',
            showgrid: false
        },
        yaxis: {
            color: '#64748b',
            gridcolor: '#334155',
            title: 'Molecules Screened / Sec'
        }
    };

    const config = { responsive: true, displayModeBar: false };

    Plotly.newPlot(chartDiv, data, layout, config);

    // Update every second simualting live throughput
    setInterval(() => {
        const time = new Date();
        const throughput = 120 + Math.random() * 80; // Random simulated speed

        Plotly.extendTraces(chartDiv, {
            x: [[time]],
            y: [[throughput]]
        }, [0]);

        // Keep 30 min window
        if (times.length > 50) {
            Plotly.relayout(chartDiv, {
                xaxis: {
                    range: [new Date(time - 30 * 1000), time] // Last 30 seconds view
                }
            });
        }
    }, 1000);
}

// 2. Fetch Real Activity from Backend
async function startActivityFeed() {
    const feedContainer = document.getElementById('activity-feed');

    const updateFeed = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            if (!token) {
                // If no token, maybe just clear feed or show login prompt in console
                // For now, we return to avoid 401 spam
                return;
            }

            // Fetch latest screening jobs as "Activity"
            const res = await fetch('http://127.0.0.1:8000/api/screening/', { headers });
            if (res.status === 401) {
                if (window.handleUnauthorized) window.handleUnauthorized();
                return;
            }
            const data = await res.json();

            // Fetch Targets
            const res2 = await fetch('http://127.0.0.1:8000/api/targets/', { headers });
            if (res2.status === 401) {
                if (window.handleUnauthorized) window.handleUnauthorized();
                return;
            }
            const targets = await res2.json();

            // Interleave and sort by date (mocking "Activity Stream")
            let activities = [];

            if (Array.isArray(data)) {
                data.forEach(d => activities.push({
                    type: 'Screening',
                    name: `Screening Job ${d._id.substring(0, 6)}...`,
                    status: d.status,
                    time: new Date() // In real app, use d.created_at
                }));
            }

            if (Array.isArray(targets)) {
                targets.forEach(t => activities.push({
                    type: 'Target',
                    name: `New Target: ${t.name}`,
                    status: 'Registered',
                    time: new Date()
                }));
            }

            // Just show last 5 events for demo freshness
            // Note: Since created_at might be old, for demo we mock "Just Now" if backend doesn't sort
            const recent = activities.slice(0, 10);

            feedContainer.innerHTML = recent.map(item => `
                <div class="feed-item fade-in">
                    <span class="feed-time">${item.type}</span>
                    <div style="display:flex; justify-content:space-between; color: #e2e8f0;">
                        <span>${item.name}</span>
                        <span style="color: ${item.status === 'Completed' || item.status === 'Registered' ? '#4ade80' : '#facc15'}">${item.status}</span>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            console.error(e);
        }
    };

    updateFeed();
    setInterval(updateFeed, 5000);
}

// 3. Simulate GPU Load
function simulateGPULoad() {
    const el = document.getElementById('gpu-load');
    setInterval(() => {
        // Random fluctuation between 60% and 95%
        const load = Math.floor(Math.random() * (95 - 60 + 1) + 60);
        el.innerText = load + "%";
        el.style.color = load > 90 ? '#f43f5e' : '#4ade80';
    }, 2000);
}
