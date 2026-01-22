document.addEventListener('DOMContentLoaded', () => {
    const loginView = document.getElementById('login-view');
    const dashboardView = document.getElementById('dashboard-view');
    const siteSelector = document.getElementById('site-selector');
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');

    // Check Auth Status
    fetch('/auth/user')
        .then(res => res.json())
        .then(data => {
            if (data.authenticated) {
                showDashboard();
            } else {
                showLogin();
            }
        });

    function showLogin() {
        loginView.classList.remove('hidden');
        dashboardView.classList.add('hidden');
    }

    function showDashboard() {
        loginView.classList.add('hidden');
        dashboardView.classList.remove('hidden');
        loadSites();
    }

    // Login Redirect
    loginBtn.addEventListener('click', () => {
        window.location.href = '/auth/login';
    });

    // Logout
    logoutBtn.addEventListener('click', () => {
        fetch('/auth/logout').then(() => {
            window.location.reload();
        });
    });

    // Load Sites
    async function loadSites() {
        const res = await fetch('/api/sites');
        const sites = await res.json();
        
        sites.forEach(site => {
            const option = document.createElement('option');
            option.value = site.siteUrl;
            option.textContent = site.siteUrl;
            siteSelector.appendChild(option);
        });
    }

    // Chat Handler
    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;
        
        const siteUrl = siteSelector.value;
        if (!siteUrl) {
            alert("Please select a property first.");
            return;
        }

        // Add User Message
        appendMessage('user', text);
        userInput.value = '';

        // Show loading
        const loadingId = appendMessage('loading', 'Analyzing data...');

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text, site_url: siteUrl })
            });
            
            const data = await res.json();
            
            // Remove loading
            document.getElementById(loadingId).remove();

            if (data.error) {
                appendMessage('system', `Error: ${data.error}`);
            } else {
                appendMessage('system', data.insight);
            }
        } catch (e) {
            document.getElementById(loadingId).remove();
            appendMessage('system', "Error connecting to server.");
        }
    }

    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.id = `msg-${Date.now()}`;
        
        if (role === 'system') {
            div.innerHTML = marked.parse(text);
        } else {
            div.textContent = text;
        }
        
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return div.id;
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
