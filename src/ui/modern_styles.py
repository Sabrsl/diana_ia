"""
DIANA - Styles modernes ultra professionnels
Interface médicale de nouvelle génération
"""

MODERN_DARK_THEME = """
/* Variables CSS-like pour cohérence */
* {
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
}

QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0f0f1e, stop:1 #1a1a2e);
}

QWidget {
    background: transparent;
    color: #e8eaed;
}

/* Header avec gradient */
QFrame#headerFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #667eea, stop:1 #764ba2);
    border: none;
    border-radius: 16px;
    padding: 25px 30px;
}

/* Cards avec effet glassmorphism */
QFrame#card {
    background: rgba(42, 42, 62, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(10px);
    margin: 5px;
}

QFrame#card:hover {
    border: 1px solid rgba(102, 126, 234, 0.5);
    background: rgba(42, 42, 62, 0.8);
}

/* Boutons modernes avec animations */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #667eea, stop:1 #764ba2);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    min-height: 40px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #7c8ff5, stop:1 #8a5fb5);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #556bd9, stop:1 #654091);
}

QPushButton:disabled {
    background: rgba(102, 126, 234, 0.3);
    color: rgba(255, 255, 255, 0.4);
}

/* Bouton primaire (analyser) */
QPushButton#analyzeButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #00d4ff, stop:1 #0099ff);
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
    min-height: 44px;
}

QPushButton#analyzeButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #33ddff, stop:1 #33aaff);
}

/* Bouton de connexion */
QPushButton#loginButton {
    background: rgba(102, 126, 234, 0.2);
    border: 2px solid rgba(102, 126, 234, 0.5);
    padding: 12px 24px;
    min-width: 180px;
}

QPushButton#loginButton:hover {
    background: rgba(102, 126, 234, 0.3);
    border: 2px solid rgba(102, 126, 234, 0.8);
}

/* Labels avec typographie moderne */
QLabel#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: white;
    padding: 2px 0px;
}

QLabel#subtitleLabel {
    font-size: 12px;
    font-weight: 400;
    color: rgba(255, 255, 255, 0.7);
    padding: 2px 0px;
}

QLabel#sectionTitle {
    font-size: 15px;
    font-weight: 600;
    color: #e8eaed;
    padding-bottom: 8px;
}

QLabel#resultTitle {
    font-size: 32px;
    font-weight: 800;
    padding: 16px;
}

/* Zone d'image avec effet moderne */
QLabel#imagePreview {
    background: rgba(26, 26, 46, 0.5);
    border: 3px dashed rgba(102, 126, 234, 0.3);
    border-radius: 20px;
    padding: 40px;
    min-height: 400px;
}

QLabel#imagePreview:hover {
    border: 3px dashed rgba(102, 126, 234, 0.6);
    background: rgba(26, 26, 46, 0.7);
}

/* Carte de résultats avec gradient */
QFrame#resultCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(102, 126, 234, 0.15),
                                stop:1 rgba(118, 75, 162, 0.15));
    border: 2px solid rgba(102, 126, 234, 0.3);
    border-radius: 24px;
    padding: 32px;
}

/* Résultat bénin (BLEU) */
QFrame#resultBenign {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(90, 200, 250, 0.2),
                                stop:1 rgba(64, 156, 255, 0.1));
    border: 2px solid rgba(90, 200, 250, 0.4);
}

/* Résultat malin */
QFrame#resultMalignant {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(255, 59, 48, 0.2),
                                stop:1 rgba(255, 69, 58, 0.1));
    border: 2px solid rgba(255, 59, 48, 0.4);
}

/* Résultat Normal/Sain (VERT) */
QFrame#resultNormal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(76, 217, 100, 0.2),
                                stop:1 rgba(52, 199, 89, 0.1));
    border: 2px solid rgba(76, 217, 100, 0.4);
}

/* Barre de progression moderne */
QProgressBar {
    background: rgba(26, 26, 46, 0.5);
    border: none;
    border-radius: 12px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #00d4ff, stop:1 #0099ff);
    border-radius: 12px;
}

/* Stats cards - CORRECTION DES TAILLES */
QFrame#statCard {
    background: rgba(102, 126, 234, 0.1);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 12px;
    padding: 16px 12px;
    margin: 3px;
    min-height: 90px;
}

QLabel#statValue {
    font-size: 28px;
    font-weight: 800;
    color: #667eea;
    padding: 4px 0px;
    qproperty-alignment: AlignCenter;
}

QLabel#statLabel {
    font-size: 11px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.6);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 4px 0px;
    qproperty-alignment: AlignCenter;
}

/* ScrollArea moderne */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: rgba(26, 26, 46, 0.3);
    width: 8px;
    border-radius: 4px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: rgba(102, 126, 234, 0.5);
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(102, 126, 234, 0.7);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Menu bar moderne */
QMenuBar {
    background: rgba(26, 26, 46, 0.8);
    color: #e8eaed;
    border: none;
    padding: 8px;
    border-radius: 12px;
    margin: 8px;
}

QMenuBar::item {
    background: transparent;
    padding: 8px 16px;
    border-radius: 8px;
}

QMenuBar::item:selected {
    background: rgba(102, 126, 234, 0.3);
}

QMenu {
    background: rgba(26, 26, 46, 0.95);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 12px;
    padding: 8px;
}

QMenu::item {
    padding: 10px 24px;
    border-radius: 8px;
    color: #e8eaed;
}

QMenu::item:selected {
    background: rgba(102, 126, 234, 0.3);
}

/* Input fields modernes */
QLineEdit, QTextEdit {
    background: rgba(26, 26, 46, 0.6);
    border: 2px solid rgba(102, 126, 234, 0.3);
    border-radius: 12px;
    padding: 14px 18px;
    color: #e8eaed;
    font-size: 15px;
    selection-background-color: rgba(102, 126, 234, 0.5);
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid rgba(102, 126, 234, 0.8);
    background: rgba(26, 26, 46, 0.8);
}

/* Tabs modernes */
QTabWidget::pane {
    border: none;
    background: transparent;
}

QTabBar::tab {
    background: rgba(42, 42, 62, 0.5);
    color: rgba(255, 255, 255, 0.6);
    padding: 14px 28px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background: rgba(102, 126, 234, 0.3);
    color: white;
}

QTabBar::tab:hover {
    background: rgba(102, 126, 234, 0.2);
}

/* Tooltips modernes */
QToolTip {
    background: rgba(26, 26, 46, 0.95);
    color: #e8eaed;
    border: 1px solid rgba(102, 126, 234, 0.5);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}

/* Dialog moderne */
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0f0f1e, stop:1 #1a1a2e);
}

/* Badge/Chip pour le statut */
QLabel#statusBadge {
    background: rgba(102, 126, 234, 0.2);
    border: 1px solid rgba(102, 126, 234, 0.5);
    border-radius: 12px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QPushButton#premiumBadge {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #FFD700, stop:1 #FFA500);
    color: #000;
    font-weight: 700;
}
"""


def get_modern_theme():
    """Retourne le thème moderne"""
    return MODERN_DARK_THEME