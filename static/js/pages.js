/**
 * DIANA - Gestion des pages
 * Système de routing et pages de l'application
 */

// ========== PAGES ==========

const Pages = {
    // Page d'accueil (analyse)
    home: () => `
        <div class="page-home">
            <div class="content-grid">
                <!-- Upload Panel -->
                <div class="panel">
                    <div class="panel-title">📸 Sélectionner une image</div>
                    
                    <form id="uploadForm" enctype="multipart/form-data">
                        <input type="file" id="fileInput" accept="image/*" style="display: none;">
                        
                        <div class="upload-zone" id="uploadZone">
                            <div id="uploadText">
                                <p style="font-size: 2.2em; margin-bottom: 12px;">📁</p>
                                <p style="font-size: 1.1em; margin-bottom: 6px; font-weight: 600;">Cliquez ou glissez une image</p>
                                <p style="color: rgba(255,255,255,0.6);">JPG, PNG, BMP, TIFF, WEBP acceptés</p>
                                <p style="color: rgba(255,255,255,0.4); margin-top: 8px; font-size: 0.9em;">Taille maximale: 50 MB</p>
                            </div>
                            <img id="preview" style="display: none;">
                        </div>
                        
                        <div style="margin-top: 24px; display: flex; gap: 16px;">
                            <button type="button" class="btn" id="browseBtn" style="flex: 1;">
                                📂 Parcourir
                            </button>
                            <button type="button" class="btn btn-primary" id="analyzeBtn" style="flex: 2;" disabled>
                                🔬 ANALYSER
                            </button>
                            <button type="button" class="btn btn-secondary" id="resetBtn" style="flex: 1;">
                                🔄 Réinitialiser
                            </button>
                        </div>
                    </form>
                </div>
                
                <!-- Results Panel -->
                <div class="panel">
                    <div class="panel-title">📊 Résultats de l'analyse</div>
                    
                    <div id="resultPanel">
                        <div class="result-content">
                            <p style="font-size: 1em; color: rgba(255,255,255,0.5);">
                                En attente d'analyse...<br><br>
                                Sélectionnez une image et cliquez sur ANALYSER
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    // Page de connexion
    login: () => `
        <div class="page-auth">
            <div class="auth-container">
                <div class="auth-card">
                    <div class="auth-header">
                        <h1>🔐 Connexion</h1>
                        <p>Accédez à votre compte DIANA</p>
                    </div>
                    ${new Components.LoginForm().render()}
                </div>
            </div>
        </div>
    `,

    // Page d'inscription
    signup: () => `
        <div class="page-auth">
            <div class="auth-container">
                <div class="auth-card">
                    <div class="auth-header">
                        <h1>✨ Inscription</h1>
                        <p>Créez votre compte DIANA Premium</p>
                    </div>
                    ${new Components.SignupForm().render()}
                </div>
            </div>
        </div>
    `,

    // Page de profil
    profile: () => {
        const user = AppState.getUser();
        if (!user) {
            AppState.navigateTo('login');
            return '';
        }

        return `
            <div class="page-profile">
                <h1 class="page-title">👤 Mon Profil</h1>
                
                <div class="profile-grid">
                    ${new Components.Card({
            title: 'Informations personnelles',
            icon: '👤',
            content: `
                            <div class="profile-info">
                                <div class="info-row">
                                    <span class="info-label">Nom:</span>
                                    <span class="info-value">${user.name || 'Non renseigné'}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Email:</span>
                                    <span class="info-value">${user.email}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Type de compte:</span>
                                    <span class="info-value ${user.is_premium ? 'premium' : 'free'}">
                                        ${user.is_premium ? '✨ Premium' : '🆓 Gratuit'}
                                    </span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Membre depuis:</span>
                                    <span class="info-value">${formatDate(user.created_at || new Date())}</span>
                                </div>
                            </div>
                        `
        }).render()}
                    
                    ${new Components.Card({
            title: 'Statistiques d\'utilisation',
            icon: '📊',
            content: `
                            <div class="stats-info">
                                <div class="stat-item">
                                    <div class="stat-value-large">${user.analyses_count || 0}</div>
                                    <div class="stat-label-small">Analyses effectuées</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value-large">${user.is_premium ? '∞' : (user.quota_remaining || 0)}</div>
                                    <div class="stat-label-small">Analyses restantes</div>
                                </div>
                            </div>
                        `
        }).render()}
                    
                            ${new Components.Card({
            title: 'Gestion du compte',
            icon: '🔐',
            content: `
                            <div class="setting-item">
                                <button class="btn btn-secondary btn-block" onclick="showNotification('🚧 Fonctionnalité bientôt disponible', 'info')">
                                    🔑 Changer le mot de passe
                                </button>
                            </div>
                            
                            <div class="setting-item">
                                <button class="btn btn-danger btn-block" onclick="confirmLogout()">
                                    🚪 Se déconnecter
                                </button>
                            </div>
                        `
        }).render()}
                    
                    ${!user.is_premium ? new Components.Card({
            title: 'Passez à Premium',
            icon: '✨',
            className: 'card-premium',
            content: `
                            <p>Débloquez des analyses illimitées et des fonctionnalités avancées !</p>
                            <ul class="features-list">
                                <li>✅ Analyses illimitées</li>
                                <li>✅ Priorité de traitement</li>
                                <li>✅ Historique complet</li>
                                <li>✅ Support prioritaire</li>
                            </ul>
                            <button class="btn btn-primary btn-block" onclick="showNotification('🚧 Fonctionnalité bientôt disponible', 'info')">
                                Passer à Premium
                            </button>
                        `
        }).render() : ''}
                </div>
            </div>
        `;
    },

    // Page d'apparence
    settings: () => `
        <div class="page-settings">
            <h1 class="page-title">🎨 Apparence</h1>
            
            <div class="settings-grid">
                ${new Components.Card({
        title: 'Thème de l\'interface',
        icon: '🎨',
        content: `
                        <div class="setting-item">
                            <div class="setting-info">
                                <h4>Mode d'affichage</h4>
                                <p>Choisissez entre le mode sombre et clair pour une meilleure expérience</p>
                            </div>
                            <button class="btn btn-toggle" onclick="AppState.toggleTheme()">
                                ${AppState.theme === 'dark' ? '🌙 Mode sombre' : '☀️ Mode clair'}
                            </button>
                        </div>
                        
                        <div class="setting-item">
                            <div class="setting-info">
                                <h4>Thème actuel</h4>
                                <p>${AppState.theme === 'dark' ? 'Interface sombre activée' : 'Interface claire activée'}</p>
                            </div>
                        </div>
                    `
    }).render()}
                
                ${new Components.Card({
        title: 'Notifications',
        icon: '🔔',
        content: `
                        <div class="setting-item">
                            <div class="setting-info">
                                <h4>Notifications push</h4>
                                <p>Recevoir des notifications pour les analyses terminées</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" id="notificationToggle">
                                <span class="slider"></span>
                            </label>
                        </div>
                        
                        <div class="setting-item">
                            <div class="setting-info">
                                <h4>Notifications email</h4>
                                <p>Recevoir des emails pour les mises à jour importantes</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" id="emailToggle" checked>
                                <span class="slider"></span>
                            </label>
                        </div>
                    `
    }).render()}
            </div>
        </div>
    `,

    // Page d'aide
    help: () => `
        <div class="page-help">
            <h1 class="page-title">❓ Aide</h1>
            
            <div class="help-grid">
                ${new Components.Card({
        title: 'Comment utiliser DIANA ?',
        icon: '📖',
        content: `
                        <ol class="help-list">
                            <li>Sélectionnez ou glissez une image médicale</li>
                            <li>Cliquez sur le bouton ANALYSER</li>
                            <li>Attendez quelques secondes le traitement</li>
                            <li>Consultez les résultats détaillés</li>
                        </ol>
                    `
    }).render()}
                
                ${new Components.Card({
        title: 'Formats supportés',
        icon: '📄',
        content: `
                        <ul class="help-list">
                            <li>JPG / JPEG</li>
                            <li>PNG</li>
                            <li>BMP</li>
                            <li>TIFF</li>
                            <li>WEBP</li>
                        </ul>
                        <p style="margin-top: 12px; color: rgba(255,255,255,0.6);">
                            Taille maximale: 50 MB
                        </p>
                    `
    }).render()}
                
                ${new Components.Card({
        title: 'FAQ',
        icon: '💬',
        content: `
                        <div class="faq-item">
                            <h4>Mes données sont-elles sécurisées ?</h4>
                            <p>Oui, toutes les images sont traitées localement et supprimées immédiatement après analyse.</p>
                        </div>
                        
                        <div class="faq-item">
                            <h4>Combien d'analyses puis-je faire ?</h4>
                            <p>Compte gratuit: 5000 analyses. Compte Premium: illimité.</p>
                        </div>
                        
                        <div class="faq-item">
                            <h4>Les résultats sont-ils fiables ?</h4>
                            <p>DIANA est un outil d'aide au diagnostic. Consultez toujours un professionnel de santé.</p>
                        </div>
                    `
    }).render()}
                
                ${new Components.Card({
        title: 'Contact',
        icon: '📧',
        content: `
                        <p>Besoin d'aide supplémentaire ?</p>
                        <button class="btn btn-primary btn-block" onclick="showNotification('📧 Contactez support@diana-app.com', 'info')">
                            Contacter le support
                        </button>
                    `
    }).render()}
            </div>
        </div>
    `
};

// ========== NAVIGATION ==========

function confirmLogout() {
    const modal = new Components.Modal(
        'Déconnexion',
        '<p>Êtes-vous sûr de vouloir vous déconnecter ?</p>',
        [
            {
                label: 'Annuler',
                className: 'btn-secondary',
                onclick: 'this.closest(\'.modal-overlay\').remove()'
            },
            {
                label: '🚪 Se déconnecter',
                className: 'btn-danger',
                onclick: 'logout()'
            }
        ]
    );
    modal.show();
}

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        AppState.logout();
        showNotification('✅ Déconnexion réussie', 'success');
        AppState.navigateTo('home');
        document.querySelector('.modal-overlay')?.remove();
    } catch (error) {
        console.error('Erreur logout:', error);
    }
}

window.Pages = Pages;
window.confirmLogout = confirmLogout;
window.logout = logout;

