"""
DIANA - Fenêtre principale moderne
Interface de nouvelle génération ultra professionnelle
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QMessageBox,
    QFrame, QProgressBar, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QColor

import config
from src.quota_manager import get_quota_manager
from src.auth_manager import get_auth_manager
from src.inference_engine import get_inference_engine
from src.update_manager import UpdateScheduler
from src.ui.login_dialog import LoginDialog
from src.ui.modern_styles import get_modern_theme

logger = logging.getLogger(__name__)


class PredictionThread(QThread):
    """Thread pour effectuer les prédictions sans bloquer l'UI"""
    
    prediction_complete = pyqtSignal(dict)
    prediction_error = pyqtSignal(str)
    
    def __init__(self, image_path: Path):
        super().__init__()
        self.image_path = image_path
    
    def run(self):
        """Exécute la prédiction"""
        try:
            engine = get_inference_engine()
            result = engine.predict(self.image_path)
            
            if result:
                self.prediction_complete.emit(result)
            else:
                self.prediction_error.emit("Erreur lors de la prédiction")
                
        except Exception as e:
            logger.error(f"Erreur thread prédiction: {e}")
            self.prediction_error.emit(str(e))


class ModernMainWindow(QMainWindow):
    """Fenêtre principale moderne de DIANA"""
    
    def __init__(self):
        super().__init__()
        self.quota_manager = get_quota_manager()
        self.auth_manager = get_auth_manager()
        self.update_scheduler = UpdateScheduler()
        
        self.current_image_path = None
        self.prediction_thread = None
        
        self.setWindowTitle(f"{config.APP_NAME} - {config.APP_FULL_NAME}")
        self.setMinimumSize(1400, 800)
        
        self.setup_ui()
        self.apply_modern_theme()
        self.update_status()
        
        # Animation d'entrée
        self.animate_entrance()
    
    def setup_ui(self):
        """Configure l'interface moderne avec scroll"""
        # Widget central avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setCentralWidget(scroll)
        
        # Container principal
        container = QWidget()
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header moderne
        header = self._create_modern_header()
        main_layout.addWidget(header)
        
        # Stats cards
        stats = self._create_stats_cards()
        main_layout.addWidget(stats)
        
        # Zone principale
        content = self._create_modern_content()
        main_layout.addWidget(content)
        
        # Stretch pour pousser le contenu vers le haut
        main_layout.addStretch()
    
    def _create_modern_header(self) -> QFrame:
        """Crée l'header moderne avec gradient"""
        frame = QFrame()
        frame.setObjectName("headerFrame")
        frame.setMinimumHeight(180)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(102, 126, 234, 100))
        shadow.setOffset(0, 10)
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Titre principal
        title = QLabel("🏥 DIANA")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("Diagnostic Intelligent Automatisé pour les Nouvelles Analyses")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        return frame
    
    def _create_stats_cards(self) -> QFrame:
        """Crée les cartes de statistiques modernes"""
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setSpacing(24)
        
        stats = self.quota_manager.get_stats()
        
        # Analyses utilisées
        card1 = self._create_stat_card(
            str(stats['used']),
            "Analyses Effectuées"
        )
        layout.addWidget(card1)
        
        # Analyses restantes
        remaining_text = "∞" if stats['is_premium'] else str(stats['remaining'])
        card2 = self._create_stat_card(
            remaining_text,
            "Analyses Restantes"
        )
        layout.addWidget(card2)
        
        # Statut
        status_text = "✨" if stats['is_premium'] else "🆓"
        status_label = "Premium" if stats['is_premium'] else "Gratuit"
        card3 = self._create_stat_card(
            status_text,
            status_label
        )
        layout.addWidget(card3)
        
        return container
    
    def _create_stat_card(self, value: str, label: str) -> QFrame:
        """Crée une carte de statistique"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(120)
        
        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(102, 126, 234, 80))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        label_widget = QLabel(label)
        label_widget.setObjectName("statLabel")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_widget)
        
        return card
    
    def _create_modern_content(self) -> QWidget:
        """Crée la zone de contenu principale moderne"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(32)
        
        # Panneau gauche : Upload
        left_panel = self._create_upload_panel()
        layout.addWidget(left_panel, stretch=1)
        
        # Panneau droit : Résultats
        right_panel = self._create_results_panel()
        layout.addWidget(right_panel, stretch=1)
        
        return widget
    
    def _create_upload_panel(self) -> QFrame:
        """Crée le panneau d'upload moderne"""
        frame = QFrame()
        frame.setObjectName("card")
        
        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 10)
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(24)
        
        # Titre
        title = QLabel("📸 Sélectionner une image")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Zone d'image
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel("📁\n\nCliquez sur 'Parcourir'\npour sélectionner une image\n\nJPG, PNG, BMP acceptés")
        self.image_label.setObjectName("imagePreview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(300)
        self.image_label.setScaledContents(False)
        self.image_label.setWordWrap(True)
        image_layout.addWidget(self.image_label)
        
        layout.addWidget(image_container, stretch=1)
        
        # Boutons FIXES en bas
        btn_container = QWidget()
        btn_container.setFixedHeight(70)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(16)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        select_btn = QPushButton("📂 Parcourir")
        select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_btn.clicked.connect(self._select_image)
        btn_layout.addWidget(select_btn, stretch=1)
        
        self.analyze_btn = QPushButton("🔬 ANALYSER")
        self.analyze_btn.setObjectName("analyzeButton")
        self.analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self._analyze_image)
        btn_layout.addWidget(self.analyze_btn, stretch=2)
        
        layout.addWidget(btn_container)
        
        return frame
    
    def _create_results_panel(self) -> QFrame:
        """Crée le panneau de résultats moderne avec scroll"""
        frame = QFrame()
        frame.setObjectName("card")
        
        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 10)
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(24)
        
        # Titre
        title = QLabel("📊 Résultats de l'analyse")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Scroll area pour les résultats
        result_scroll = QScrollArea()
        result_scroll.setWidgetResizable(True)
        result_scroll.setFrameShape(QFrame.Shape.NoFrame)
        result_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Zone de résultats
        self.result_frame = QFrame()
        self.result_frame.setObjectName("resultCard")
        result_layout = QVBoxLayout(self.result_frame)
        
        self.result_label = QLabel("En attente d'analyse...\n\nSélectionnez une image\net cliquez sur ANALYSER")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-size: 19px; color: rgba(255,255,255,0.5);")
        result_layout.addWidget(self.result_label)
        
        result_scroll.setWidget(self.result_frame)
        layout.addWidget(result_scroll, stretch=1)
        
        # Barre de progression FIXE en bas
        progress_container = QWidget()
        progress_container.setFixedHeight(20)
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_container)
        
        return frame
    
    def apply_modern_theme(self):
        """Applique le thème moderne"""
        self.setStyleSheet(get_modern_theme())
    
    def animate_entrance(self):
        """Anime l'entrée des éléments"""
        self.setWindowOpacity(0)
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(800)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        
        # Garder la référence
        self._entrance_animation = animation
    
    def _select_image(self):
        """Ouvre un dialogue pour sélectionner une image"""
        formats = " ".join([f"*{ext}" for ext in config.SUPPORTED_IMAGE_FORMATS])
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une mammographie",
            "",
            f"Images ({formats});;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.current_image_path = Path(file_path)
            self._display_image(self.current_image_path)
            self.analyze_btn.setEnabled(True)
            logger.info(f"Image sélectionnée: {file_path}")
    
    def _display_image(self, image_path: Path):
        """Affiche l'image sélectionnée"""
        try:
            pixmap = QPixmap(str(image_path))
            if pixmap.isNull():
                self.image_label.setText("❌ Impossible de charger l'image")
                logger.error(f"Image invalide: {image_path}")
                return
            
            scaled_pixmap = pixmap.scaled(
                600, 600,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            logger.info(f"Image affichée: {image_path.name}")
        except Exception as e:
            logger.error(f"Erreur affichage image: {e}")
            self.image_label.setText("❌ Erreur de chargement")
    
    def _analyze_image(self):
        """Lance l'analyse"""
        if not self.current_image_path:
            QMessageBox.warning(self, "Erreur", "Aucune image sélectionnée")
            return
        
        if not self.quota_manager.can_analyze():
            QMessageBox.warning(
                self,
                "Quota épuisé",
                "Vous avez atteint la limite gratuite de 5000 analyses.\n\n"
                "Connectez-vous avec un compte Premium pour continuer."
            )
            self._show_login()
            return
        
        # UI pendant l'analyse
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.result_label.setText("🔬 Analyse en cours...\n\nVeuillez patienter")
        
        logger.info(f"Démarrage analyse: {self.current_image_path}")
        
        # Lancer l'analyse
        self.prediction_thread = PredictionThread(self.current_image_path)
        self.prediction_thread.prediction_complete.connect(self._on_prediction_complete)
        self.prediction_thread.prediction_error.connect(self._on_prediction_error)
        self.prediction_thread.start()
    
    def _on_prediction_complete(self, result: dict):
        """Gère la fin de la prédiction"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self._display_results(result)
        self.update_status()
        logger.info("Analyse terminée avec succès")
    
    def _on_prediction_error(self, error_message: str):
        """Gère les erreurs"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.result_label.setText(f"❌ Erreur\n\n{error_message}")
        QMessageBox.critical(self, "Erreur", f"Erreur d'analyse:\n{error_message}")
        logger.error(f"Erreur analyse: {error_message}")
    
    def _display_results(self, result: dict):
        """Affiche les résultats avec design moderne"""
        prediction = result.get("prediction", "Inconnu")
        confidence = result.get("confidence", 0)
        probabilities = result.get("probabilities", {})
        
        # Couleur selon le résultat
        if "Normal" in prediction or "Sain" in prediction:
            self.result_frame.setObjectName("resultNormal")
            emoji = "✅"
            color = "#4cd964"
        elif "Bénin" in prediction:
            self.result_frame.setObjectName("resultBenign")
            emoji = "ℹ️"
            color = "#5ac8fa"
        elif "Malin" in prediction:
            self.result_frame.setObjectName("resultMalignant")
            emoji = "⚠️"
            color = "#ff3b30"
        else:
            self.result_frame.setObjectName("resultNormal")
            emoji = "❓"
            color = "#8e8e93"
        
        # Forcer le rafraîchissement du style
        self.result_frame.setStyleSheet("")
        self.apply_modern_theme()
        
        # HTML moderne
        html = f"""
        <div style='text-align: center; padding: 32px;'>
            <h1 style='font-size: 80px; margin: 20px 0;'>{emoji}</h1>
            <h2 style='color: {color}; font-size: 48px; margin: 16px 0; font-weight: 900;'>
                {prediction}
            </h2>
            <p style='font-size: 32px; color: rgba(255,255,255,0.9); font-weight: 700; margin: 24px 0;'>
                Confiance : {confidence:.1f}%
            </p>
        """
        
        if probabilities:
            html += "<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 24px 0;'>"
            html += "<h3 style='font-size: 21px; color: rgba(255,255,255,0.8); margin-bottom: 16px; font-weight: 600;'>Probabilités détaillées</h3>"
            
            for class_name, prob in probabilities.items():
                bar_width = int(prob)
                html += f"""
                <div style='text-align: left; margin: 16px 0;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                        <span style='font-size: 18px; color: rgba(255,255,255,0.8);'>{class_name}</span>
                        <strong style='font-size: 18px; color: rgba(255,255,255,0.8);'>{prob:.2f}%</strong>
                    </div>
                    <div style='background: rgba(255,255,255,0.1); border-radius: 8px; height: 12px; overflow: hidden;'>
                        <div style='background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: {bar_width}%; border-radius: 8px;'></div>
                    </div>
                </div>
                """
        
        html += """
            <hr style='border: 1px solid rgba(255,255,255,0.1); margin: 24px 0;'>
            <div style='background: rgba(255, 159, 10, 0.15); border: 1px solid rgba(255, 159, 10, 0.3); border-radius: 16px; padding: 20px; margin-top: 24px;'>
                <p style='font-size: 15px; color: rgba(255,255,255,0.8); margin: 0;'>
                    ⚠️ Outil d'aide au diagnostic • Consultez un professionnel de santé
                </p>
            </div>
        </div>
        """
        
        self.result_label.setText(html)
    
    def _handle_account(self):
        """Gère le bouton de compte"""
        if self.auth_manager.is_logged_in():
            user = self.auth_manager.get_current_user()
            status = "Premium ✨" if user.get('is_premium') else "Gratuit"
            QMessageBox.information(
                self,
                "Compte",
                f"Connecté : {user.get('email')}\nStatut : {status}"
            )
        else:
            self._show_login()
    
    def _show_login(self):
        """Affiche le dialogue de connexion"""
        dialog = LoginDialog(self)
        dialog.login_success.connect(self._on_login_success)
        dialog.exec()
    
    def _on_login_success(self, user: dict):
        """Gère une connexion réussie"""
        self.quota_manager.set_premium(user.get('is_premium', False))
        self.update_status()
        status = "Premium ✨" if user.get('is_premium') else "Gratuit"
        QMessageBox.information(
            self,
            "Bienvenue !",
            f"Connexion réussie !\n\nStatut : {status}"
        )
    
    def update_status(self):
        """Met à jour le statut et les cartes de stats"""
        # Recréer les stats cards avec les nouvelles données
        stats = self.quota_manager.get_stats()
        
        # Trouver le container de stats
        for widget in self.centralWidget().widget().findChildren(QFrame):
            layout = widget.layout()
            if layout and isinstance(layout, QHBoxLayout) and layout.count() == 3:
                # Vider et recréer les stats
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                # Recréer les cartes
                card1 = self._create_stat_card(
                    str(stats['used']),
                    "Analyses Effectuées"
                )
                layout.addWidget(card1)
                
                remaining_text = "∞" if stats['is_premium'] else str(stats['remaining'])
                card2 = self._create_stat_card(
                    remaining_text,
                    "Analyses Restantes"
                )
                layout.addWidget(card2)
                
                status_text = "✨" if stats['is_premium'] else "🆓"
                status_label = "Premium" if stats['is_premium'] else "Gratuit"
                card3 = self._create_stat_card(
                    status_text,
                    status_label
                )
                layout.addWidget(card3)
                
                break
        
        self.apply_modern_theme()
    
    def closeEvent(self, event):
        """Gère la fermeture"""
        if self.prediction_thread and self.prediction_thread.isRunning():
            self.prediction_thread.terminate()
            self.prediction_thread.wait()
        event.accept()