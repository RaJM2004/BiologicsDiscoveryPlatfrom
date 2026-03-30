// Main JavaScript file for global interactions

const API_BASE_URL = "http://127.0.0.1:8000";
console.log("Main JS v1.0.3 Loading with Auth Interceptor...");
window.BIO_PLATFORM_MAIN_LOADED = true;

// --- Global Fetch Interceptor ---
const { fetch: originalFetch } = window;
window.fetch = async (...args) => {
    let [resource, config] = args;
    config = config || {};
    const token = localStorage.getItem('token');

    // Determine URL string safely
    const urlStr = typeof resource === 'string' ? resource : (resource ? resource.url : "");
    const isLocalApi = urlStr && (urlStr.startsWith('/') || urlStr.startsWith(API_BASE_URL) || urlStr.startsWith(window.location.origin));
    
    // Safety Log
    console.debug(`[Fetch Interceptor] Targeting: ${urlStr} | Local: ${isLocalApi}`);

    if (token && isLocalApi) {
        config.headers = config.headers || {};
        // Only add header if not already present
        if (!config.headers['Authorization']) {
            config.headers['Authorization'] = 'Bearer ' + token;
        }
        // Force JSON for API calls if body is present and not FormData
        if (config.body && !(config.body instanceof FormData) && !config.headers['Content-Type']) {
            config.headers['Content-Type'] = 'application/json';
        }
    }

    try {
        const response = await originalFetch(resource, config);
        
        // Global 401 handling
        if (response.status === 401) {
            const path = window.location.pathname;
            if (!path.includes('login.html') && !path.includes('landing.html')) {
                console.warn("Unauthorized access. Redirecting...");
                window.handleUnauthorized();
            }
        }
        return response;
    } catch (err) {
        console.error(`[Fetch Interceptor Error] ${urlStr}:`, err);
        throw err;
    }
};


// Global Helpers (must be outside DOMContentLoaded for inline onclick handlers)
window.handleUnauthorized = () => {
    console.warn("Session expired. Redirecting to login...");
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('role');
    window.location.href = 'login.html';
};

window.logout = () => {
    localStorage.clear();
    window.location.href = 'login.html';
};

window.goToPreformulation = (compoundId, smiles) => {
    const url = `preformulation_analysis.html?compound_id=${encodeURIComponent(compoundId)}&smiles=${encodeURIComponent(smiles)}&auto_run=true`;
    window.location.href = url;
};

window.goToFormulation = (compoundId) => {
    const url = `formulation_design.html?compound_id=${encodeURIComponent(compoundId)}&auto_run=true`;
    window.location.href = url;
};

window.goToADMET = (smiles) => {
    const url = `admet_prediction.html?smiles=${encodeURIComponent(smiles)}&auto_run=true`;
    window.location.href = url;
};

// Application Logic
document.addEventListener('DOMContentLoaded', () => {
    console.log('Biologics Discovery Platform loaded.');

    // Highlight active link
    const currentPath = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-item a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else if (currentPath === '' && link.getAttribute('href') === 'dashboard.html') {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Handle stats update if on dashboard
    if (document.getElementById('experiment-count')) {
        updateDashboardStats();
    }
});

async function updateDashboardStats() {
    const statusEl = document.getElementById('api-status');
    const expCountEl = document.getElementById('experiment-count');
    const targetCountEl = document.getElementById('target-count');
    const screenCountEl = document.getElementById('screening-count');

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            // No token, cannot fetch data.
            // Set counts to 0 or some default state
            targetCountEl.textContent = "0";
            expCountEl.textContent = "0";
            screenCountEl.textContent = "0";
            statusEl.textContent = "● Login Required";
            statusEl.style.color = "#facc15"; // Yellow
            return;
        }

        const headers = { 'Authorization': `Bearer ${token}` };

        // Fetch User Profile
        try {
            const userRes = await fetch(`${API_BASE_URL}/api/auth/me`, { headers });
            if (userRes.ok) {
                const user = await userRes.json();
                const profileEl = document.querySelector('.user-profile span');
                const displayName = user.full_name || (user.email ? user.email.split('@')[0] : 'Scientist');
                if (profileEl) profileEl.textContent = `Welcome, ${displayName}`;
            }
        } catch (e) {
            console.error("Failed to fetch user profile", e);
        }

        // Check health
        const healthRes = await fetch(`${API_BASE_URL}/health`);
        if (healthRes.ok) {
            statusEl.textContent = "● System Online";
            statusEl.style.color = "#4ade80"; // Green
            statusEl.style.background = "rgba(74, 222, 128, 0.1)";
        } else {
            throw new Error("Health check failed");
        }

        // Fetch Targets
        const targetsRes = await fetch(`${API_BASE_URL}/api/targets/`, { headers });
        if (targetsRes.status === 401) {
            window.handleUnauthorized();
            return;
        }
        const targets = await targetsRes.json();
        targetCountEl.textContent = targets.length;

        // Fetch Experiments
        const expRes = await fetch(`${API_BASE_URL}/api/experiments/`, { headers });
        if (expRes.status === 401) {
            window.handleUnauthorized();
            return;
        }
        const experiments = await expRes.json();
        expCountEl.textContent = experiments.length;

        // Fetch Screenings
        const screenRes = await fetch(`${API_BASE_URL}/api/screening/`, { headers });
        if (screenRes.status === 401) {
            window.handleUnauthorized();
            return;
        }
        const screenings = await screenRes.json();
        screenCountEl.textContent = screenings.length;

    } catch (error) {
        console.error("API Error:", error);
        statusEl.textContent = "● Offline / Error";
        statusEl.style.color = "#f87171"; // Red
        statusEl.style.background = "rgba(248, 113, 113, 0.1)";

        // Show placeholders if connection fails
        targetCountEl.textContent = "0";
        expCountEl.textContent = "0";
        screenCountEl.textContent = "0";
    }
}
