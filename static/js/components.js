/**
 * DIANA - Composants réutilisables
 * Système de composants modulaires pour l'interface web
 */

// ========== ÉTAT GLOBAL ==========
const AppState = {
    user: null,
    theme: localStorage.getItem('theme') || 'dark',
    currentPage: 'home',

    setUser(user) {
        this.user = user;
        localStorage.setItem('user', JSON.stringify(user));
        this.notify();
    },

    getUser() {
        if (!this.user) {
            const stored = localStorage.getItem('user');
            this.user = stored ? JSON.parse(stored) : null;
        }
        return this.user;
    },

    logout() {
        this.user = null;
        localStorage.removeItem('user');
        this.notify();
    },

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', this.theme);
        document.body.className = `theme-${this.theme}`;
        this.notify();
    },

    navigateTo(page) {
        this.currentPage = page;
        this.notify();
    },

    listeners: [],

    subscribe(callback) {
        this.listeners.push(callback);
    },

    notify() {
        this.listeners.forEach(callback => callback(this));
    }
};

// ========== COMPOSANTS UI ==========

// Modal réutilisable
class Modal {
    constructor(title, content, actions = []) {
        this.title = title;
        this.content = content;
        this.actions = actions;
    }

    render() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${this.title}</h2>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>
                </div>
                <div class="modal-body">
                    ${this.content}
                </div>
                <div class="modal-footer">
                    ${this.actions.map(action => `
                        <button class="btn ${action.className || ''}" onclick="${action.onclick}">
                            ${action.label}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;

        // Fermer au clic sur l'overlay
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        return modal;
    }

    show() {
        document.body.appendChild(this.render());
    }
}

// Card réutilisable
class Card {
    constructor(options = {}) {
        this.title = options.title || '';
        this.content = options.content || '';
        this.className = options.className || '';
        this.icon = options.icon || '';
    }

    render() {
        return `
            <div class="card ${this.className}">
                ${this.icon ? `<div class="card-icon">${this.icon}</div>` : ''}
                ${this.title ? `<h3 class="card-title">${this.title}</h3>` : ''}
                <div class="card-content">${this.content}</div>
            </div>
        `;
    }
}

// Formulaire de login
class LoginForm {
    render() {
        return `
            <form id="loginForm" class="auth-form">
                <div class="form-group">
                    <label for="loginEmail">📧 Email</label>
                    <input type="email" id="loginEmail" name="email" required 
                           placeholder="votre@email.com" class="form-input">
                </div>
                
                <div class="form-group">
                    <label for="loginPassword">🔒 Mot de passe</label>
                    <input type="password" id="loginPassword" name="password" required 
                           placeholder="••••••••" class="form-input">
                </div>
                
                <button type="submit" class="btn btn-primary btn-block">
                    🔐 Se connecter
                </button>
                
                <p class="form-footer">
                    Pas encore de compte ? 
                    <a href="#" onclick="AppState.navigateTo('signup'); return false;">
                        S'inscrire
                    </a>
                </p>
            </form>
        `;
    }

    attachEvents() {
        const form = document.getElementById('loginForm');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);

                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (response.ok) {
                        AppState.setUser(result.user);
                        showNotification('✅ Connexion réussie !', 'success');
                        AppState.navigateTo('home');
                    } else {
                        showNotification('❌ ' + result.detail, 'error');
                    }
                } catch (error) {
                    showNotification('❌ Erreur de connexion', 'error');
                    console.error('Erreur:', error);
                }
            });
        }
    }
}

// Formulaire d'inscription
class SignupForm {
    render() {
        return `
            <form id="signupForm" class="auth-form">
                <div class="form-group">
                    <label for="signupName">👤 Nom complet</label>
                    <input type="text" id="signupName" name="name" required 
                           placeholder="Jean Dupont" class="form-input">
                </div>
                
                <div class="form-group">
                    <label for="signupEmail">📧 Email</label>
                    <input type="email" id="signupEmail" name="email" required 
                           placeholder="votre@email.com" class="form-input">
                </div>
                
                <div class="form-group">
                    <label for="signupPassword">🔒 Mot de passe</label>
                    <input type="password" id="signupPassword" name="password" required 
                           placeholder="••••••••" class="form-input" minlength="6">
                </div>
                
                <div class="form-group">
                    <label for="signupPasswordConfirm">🔒 Confirmer le mot de passe</label>
                    <input type="password" id="signupPasswordConfirm" name="password_confirm" required 
                           placeholder="••••••••" class="form-input" minlength="6">
                </div>
                
                <button type="submit" class="btn btn-primary btn-block">
                    ✨ S'inscrire
                </button>
                
                <p class="form-footer">
                    Déjà un compte ? 
                    <a href="#" onclick="AppState.navigateTo('login'); return false;">
                        Se connecter
                    </a>
                </p>
            </form>
        `;
    }

    attachEvents() {
        const form = document.getElementById('signupForm');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);

                // Vérifier que les mots de passe correspondent
                const password = formData.get('password');
                const passwordConfirm = formData.get('password_confirm');

                if (password !== passwordConfirm) {
                    showNotification('❌ Les mots de passe ne correspondent pas', 'error');
                    return;
                }

                try {
                    const response = await fetch('/api/auth/signup', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (response.ok) {
                        AppState.setUser(result.user);
                        showNotification('✅ Inscription réussie ! Bienvenue !', 'success');
                        AppState.navigateTo('home');
                    } else {
                        showNotification('❌ ' + result.detail, 'error');
                    }
                } catch (error) {
                    showNotification('❌ Erreur inscription', 'error');
                    console.error('Erreur:', error);
                }
            });
        }
    }
}

// ========== UTILITAIRES ==========

// Notification toast
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Animation d'entrée
    setTimeout(() => notification.classList.add('show'), 10);

    // Retirer après 3 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Formater la date
function formatDate(date) {
    return new Date(date).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Exporter les composants
window.Components = {
    Modal,
    Card,
    LoginForm,
    SignupForm
};

window.AppState = AppState;
window.showNotification = showNotification;
window.formatDate = formatDate;

