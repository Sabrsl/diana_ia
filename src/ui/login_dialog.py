"""
DIANA - Dialogue de connexion
Interface de connexion / inscription pour les comptes premium
"""

import asyncio
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTabWidget, QWidget,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.auth_manager import get_auth_manager


class LoginDialog(QDialog):
    """Dialogue de connexion/inscription"""
    
    login_success = pyqtSignal(dict)  # Signal émis lors d'une connexion réussie
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = get_auth_manager()
        self.setWindowTitle("DIANA - Connexion Premium")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("🔐 Connexion Premium")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Accédez à des analyses illimitées")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Tabs pour connexion/inscription
        tabs = QTabWidget()
        tabs.addTab(self._create_login_tab(), "Se connecter")
        tabs.addTab(self._create_signup_tab(), "S'inscrire")
        layout.addWidget(tabs)
        
        # Bouton annuler
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
    
    def _create_login_tab(self) -> QWidget:
        """Crée l'onglet de connexion"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Email
        email_label = QLabel("Email:")
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("votre.email@example.com")
        layout.addWidget(email_label)
        layout.addWidget(self.login_email)
        
        # Mot de passe
        password_label = QLabel("Mot de passe:")
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setPlaceholderText("••••••••")
        layout.addWidget(password_label)
        layout.addWidget(self.login_password)
        
        # Bouton connexion
        login_btn = QPushButton("Se connecter")
        login_btn.setObjectName("primaryButton")
        login_btn.clicked.connect(self._handle_login)
        layout.addWidget(login_btn)
        
        layout.addStretch()
        return widget
    
    def _create_signup_tab(self) -> QWidget:
        """Crée l'onglet d'inscription"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Email
        email_label = QLabel("Email:")
        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("votre.email@example.com")
        layout.addWidget(email_label)
        layout.addWidget(self.signup_email)
        
        # Mot de passe
        password_label = QLabel("Mot de passe:")
        self.signup_password = QLineEdit()
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_password.setPlaceholderText("••••••••")
        layout.addWidget(password_label)
        layout.addWidget(self.signup_password)
        
        # Confirmation mot de passe
        confirm_label = QLabel("Confirmer le mot de passe:")
        self.signup_confirm = QLineEdit()
        self.signup_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_confirm.setPlaceholderText("••••••••")
        layout.addWidget(confirm_label)
        layout.addWidget(self.signup_confirm)
        
        # Bouton inscription
        signup_btn = QPushButton("S'inscrire")
        signup_btn.setObjectName("primaryButton")
        signup_btn.clicked.connect(self._handle_signup)
        layout.addWidget(signup_btn)
        
        layout.addStretch()
        return widget
    
    def _handle_login(self):
        """Gère la tentative de connexion"""
        email = self.login_email.text().strip()
        password = self.login_password.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return
        
        # Connexion asynchrone
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, message = loop.run_until_complete(
            self.auth_manager.sign_in(email, password)
        )
        loop.close()
        
        if success:
            user = self.auth_manager.get_current_user()
            QMessageBox.information(self, "Succès", message)
            self.login_success.emit(user)
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", message)
    
    def _handle_signup(self):
        """Gère la tentative d'inscription"""
        email = self.signup_email.text().strip()
        password = self.signup_password.text()
        confirm = self.signup_confirm.text()
        
        if not email or not password or not confirm:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas")
            return
        
        if len(password) < 8:
            QMessageBox.warning(self, "Erreur", "Le mot de passe doit contenir au moins 8 caractères")
            return
        
        # Inscription asynchrone
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, message = loop.run_until_complete(
            self.auth_manager.sign_up(email, password)
        )
        loop.close()
        
        if success:
            QMessageBox.information(self, "Succès", message)
            # Passer à l'onglet de connexion
        else:
            QMessageBox.critical(self, "Erreur", message)

