/**
 * DIANA - Application principale
 * Gestion du routing et initialisation
 */

// ========== INITIALIZATION ==========

class DianaApp {
    constructor() {
        this.mainContent = document.getElementById('mainContent');
        this.init();
    }

    init() {
        // Appliquer le thème sauvegardé
        document.body.className = `theme-${AppState.theme}`;

        // S'abonner aux changements d'état
        AppState.subscribe((state) => {
            this.render();
            this.updateHeader();
        });

        // Render initial
        this.render();
        this.updateHeader();

        // Charger les statistiques
        this.loadStats();

        // Recharger les stats toutes les 30 secondes
        setInterval(() => this.loadStats(), 30000);
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                const stats = await response.json();
                this.updateStatsDisplay(stats);
            }
        } catch (error) {
            console.error('Erreur chargement stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        const statCards = document.querySelectorAll('.stat-card');
        if (statCards.length >= 3) {
            // Analyses effectuées
            const usedValue = statCards[0].querySelector('.stat-value');
            if (usedValue) usedValue.textContent = stats.used || 0;

            // Analyses restantes
            const remainingValue = statCards[1].querySelector('.stat-value');
            if (remainingValue) {
                remainingValue.textContent = stats.is_premium ? '∞' : (stats.remaining || 0);
            }

            // Type de compte
            const typeValue = statCards[2].querySelector('.stat-value');
            if (typeValue) {
                typeValue.textContent = stats.is_premium ? '✨' : '🆓';
            }

            const typeLabel = statCards[2].querySelector('.stat-label');
            if (typeLabel) {
                typeLabel.textContent = stats.is_premium ? 'Premium' : 'Gratuit';
            }
        }
    }

    render() {
        const page = AppState.currentPage;
        const pageContent = Pages[page];

        if (pageContent) {
            this.mainContent.innerHTML = pageContent();
            this.attachPageEvents(page);
        }
    }

    attachPageEvents(page) {
        // Attacher les événements spécifiques à chaque page
        switch (page) {
            case 'home':
                this.initHomePage();
                break;
            case 'login':
                new Components.LoginForm().attachEvents();
                break;
            case 'signup':
                new Components.SignupForm().attachEvents();
                break;
        }
    }

    updateHeader() {
        const user = AppState.getUser();
        const loginBtn = document.getElementById('loginBtn');
        const signupLink = document.getElementById('signupLink');
        const logoutLink = document.getElementById('logoutLink');

        if (user) {
            // Utilisateur connecté
            if (loginBtn) {
                loginBtn.textContent = `👤 ${user.name || user.email}`;
                loginBtn.onclick = () => AppState.navigateTo('profile');
            }
            if (signupLink) signupLink.style.display = 'none';
            if (logoutLink) logoutLink.style.display = 'block';
        } else {
            // Utilisateur non connecté
            if (loginBtn) {
                loginBtn.textContent = '🔐 Connexion';
                loginBtn.onclick = () => AppState.navigateTo('login');
            }
            if (signupLink) signupLink.style.display = 'block';
            if (logoutLink) logoutLink.style.display = 'none';
        }
    }

    // ========== PAGE HOME (ANALYSE) ==========

    initHomePage() {
        const fileInput = document.getElementById('fileInput');
        const preview = document.getElementById('preview');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const browseBtn = document.getElementById('browseBtn');
        const resetBtn = document.getElementById('resetBtn');
        const uploadZone = document.getElementById('uploadZone');
        const uploadText = document.getElementById('uploadText');
        const resultPanel = document.getElementById('resultPanel');

        if (!fileInput || !browseBtn || !uploadZone || !analyzeBtn || !resetBtn) {
            console.error('❌ Éléments manquants');
            return;
        }

        console.log('✅ Page home initialisée');

        // Bouton Parcourir
        browseBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileInput.click();
        });

        // Zone cliquable
        uploadZone.addEventListener('click', (e) => {
            if (e.target.id !== 'preview') {
                fileInput.click();
            }
        });

        // Support du glisser-déposer
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.style.borderColor = 'rgba(102, 126, 234, 0.8)';
            uploadZone.style.background = 'rgba(102, 126, 234, 0.1)';
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.style.borderColor = 'rgba(102, 126, 234, 0.4)';
            uploadZone.style.background = 'rgba(15, 15, 30, 0.5)';
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.style.borderColor = 'rgba(102, 126, 234, 0.4)';
            uploadZone.style.background = 'rgba(15, 15, 30, 0.5)';

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    fileInput.files = dataTransfer.files;
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);
                } else {
                    showNotification('❌ Veuillez déposer une image', 'error');
                }
            }
        });

        // Quand un fichier est sélectionné
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                console.log('📄 Fichier sélectionné:', file.name);
                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    uploadText.style.display = 'none';
                    analyzeBtn.disabled = false;
                };
                reader.onerror = (e) => {
                    console.error('❌ Erreur lecture fichier:', e);
                    showNotification('❌ Impossible de lire le fichier', 'error');
                };
                reader.readAsDataURL(file);
            }
        });

        // Bouton ANALYSER
        analyzeBtn.addEventListener('click', async () => {
            const file = fileInput.files[0];
            if (!file) {
                showNotification('❌ Aucun fichier sélectionné', 'error');
                return;
            }

            // Vérifications
            const maxSize = 50 * 1024 * 1024;
            if (file.size > maxSize) {
                showNotification(`❌ Fichier trop volumineux (${(file.size / 1024 / 1024).toFixed(2)} MB). Maximum: 50 MB`, 'error');
                return;
            }

            const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                showNotification(`❌ Type de fichier non supporté: ${file.type}`, 'error');
                return;
            }

            // Analyse
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '⏳ Analyse...';

            resultPanel.innerHTML = `
                <div class="result-content analyzing">
                    <div class="loader"></div>
                    <p style="margin-top: 24px; font-size: 1.3em; font-weight: 600;">🔬 Analyse en cours...</p>
                    <p style="margin-top: 12px; color: rgba(255,255,255,0.6);">Veuillez patienter</p>
                </div>
            `;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    this.displayResult(result, resultPanel);
                    showNotification('✅ Analyse terminée !', 'success');

                    // Recharger les statistiques après l'analyse
                    this.loadStats();
                } else {
                    let errorMessage = 'Erreur lors de l\'analyse';

                    try {
                        const error = await response.json();
                        errorMessage = error.detail || error.message || 'Erreur lors de l\'analyse';
                    } catch (e) {
                        // Si la réponse n'est pas du JSON, utiliser le texte brut
                        errorMessage = await response.text() || 'Erreur lors de l\'analyse';
                    }

                    if (response.status === 413) {
                        errorMessage = 'Fichier trop volumineux. Maximum: 50 MB';
                    } else if (response.status === 429) {
                        errorMessage = 'Quota épuisé. Connectez-vous avec un compte Premium.';
                    }

                    this.displayError(errorMessage, resultPanel);
                    showNotification('❌ ' + errorMessage, 'error');
                }
            } catch (error) {
                console.error('Exception:', error);
                this.displayError('Erreur de connexion. Vérifiez que le serveur est démarré.', resultPanel);
                showNotification('❌ Erreur de connexion', 'error');
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '🔬 ANALYSER';
            }
        });

        // Bouton RÉINITIALISER
        resetBtn.addEventListener('click', () => {
            // Réinitialiser le champ de fichier
            fileInput.value = '';

            // Réinitialiser l'aperçu d'image
            if (preview) {
                preview.style.display = 'none';
                preview.src = '';
            }

            // Réinitialiser la zone d'upload
            if (uploadZone) {
                uploadZone.style.border = '3px dashed rgba(102, 126, 234, 0.4)';
                uploadZone.style.background = 'var(--bg-tertiary)';
            }

            // Réinitialiser le texte d'upload
            if (uploadText) {
                uploadText.style.display = 'block';
                uploadText.innerHTML = `
                    <p style="font-size: 3em; margin-bottom: 16px;">📁</p>
                    <p style="font-size: 1.3em; margin-bottom: 8px; font-weight: 600;">Cliquez ou glissez une image</p>
                    <p style="color: rgba(255,255,255,0.6);">JPG, PNG, BMP, TIFF, WEBP acceptés</p>
                    <p style="color: rgba(255,255,255,0.4); margin-top: 8px; font-size: 0.9em;">Taille maximale: 50 MB</p>
                `;
            }

            // Réinitialiser le bouton d'analyse
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '🔬 ANALYSER';

            // Réinitialiser le panneau de résultats
            if (resultPanel) {
                resultPanel.innerHTML = `
                    <div class="result-content">
                        <p style="font-size: 1.2em; color: rgba(255,255,255,0.5);">
                            En attente d'analyse...<br><br>
                            Sélectionnez une image et cliquez sur ANALYSER
                        </p>
                    </div>
                `;
            }

            // Notification de réinitialisation
            showNotification('🔄 Interface réinitialisée', 'info');
        });
    }

    displayResult(result, resultPanel) {
        const prediction = result.prediction;
        const confidence = result.confidence.toFixed(1);
        const probabilities = result.probabilities;

        let emoji, color, cssClass;
        if (prediction.includes('Normal') || prediction.includes('Sain')) {
            emoji = '✅';
            color = '#4cd964';
            cssClass = 'result-normal';
        } else if (prediction.includes('Bénin')) {
            emoji = 'ℹ️';
            color = '#5ac8fa';
            cssClass = 'result-benign';
        } else if (prediction.includes('Malin')) {
            emoji = '⚠️';
            color = '#ff3b30';
            cssClass = 'result-malignant';
        } else {
            emoji = '❓';
            color = '#8e8e93';
            cssClass = 'result-normal';
        }

        let probBars = '';
        for (const [className, prob] of Object.entries(probabilities)) {
            probBars += `
                <div class="probability-bar">
                    <div class="probability-label">
                        <span>${className}</span>
                        <strong>${prob.toFixed(2)}%</strong>
                    </div>
                    <div class="bar">
                        <div class="bar-fill" style="width: ${prob}%"></div>
                    </div>
                </div>
            `;
        }

        resultPanel.innerHTML = `
            <div class="result-content ${cssClass}">
                <div class="result-icon">${emoji}</div>
                <div class="result-title" style="color: ${color}">${prediction}</div>
                <div class="result-confidence">Confiance : ${confidence}%</div>
                
                <div class="result-details">
                    <h3 style="margin-bottom: 16px; font-size: 1.3em;">Probabilités détaillées</h3>
                    ${probBars}
                </div>
                
                <div class="warning">
                    ⚠️ Outil d'aide au diagnostic • Consultez un professionnel de santé
                </div>
            </div>
        `;
    }

    displayError(message, resultPanel) {
        resultPanel.innerHTML = `
            <div class="result-content" style="background: rgba(255, 59, 48, 0.15); border: 2px solid rgba(255, 59, 48, 0.4);">
                <div class="result-icon">❌</div>
                <div class="result-title" style="color: #ff3b30;">Erreur</div>
                <p style="margin-top: 16px; font-size: 1.1em; color: rgba(255,255,255,0.8);">${message}</p>
            </div>
        `;
    }
}

// ========== NAVIGATION MENU ==========

function initMenu() {
    const menuBtn = document.getElementById('menuBtn');
    const menu = document.getElementById('mainMenu');
    const header = document.getElementById('mainHeader');

    if (menuBtn && menu && header) {
        menuBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const isOpen = menu.classList.contains('show');

            if (isOpen) {
                // Fermer le menu
                menu.classList.remove('show');
                header.classList.remove('header-compact');
            } else {
                // Ouvrir le menu
                menu.classList.add('show');
                header.classList.add('header-compact');
            }
        });

        // Fermer le menu au clic en dehors
        document.addEventListener('click', (e) => {
            if (!menu.contains(e.target) && !menuBtn.contains(e.target)) {
                menu.classList.remove('show');
                header.classList.remove('header-compact');
            }
        });
    }
}

// ========== BOUTON ACCUEIL ==========

function initHomeButton() {
    const homeBtn = document.getElementById('homeBtn');
    if (homeBtn) {
        homeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // Fermer le menu si ouvert
            const menu = document.getElementById('mainMenu');
            const header = document.getElementById('mainHeader');
            if (menu && header) {
                menu.classList.remove('show');
                header.classList.remove('header-compact');
            }

            // Forcer la navigation vers l'accueil avec replace
            window.location.replace(window.location.origin + window.location.pathname);
        });
    }
}


// ========== INIT APP ==========

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DIANA App chargée');
    window.dianaApp = new DianaApp();
    initMenu();
    initHomeButton();

});

