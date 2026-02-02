# https://github.com/123panNextGen/123pan
# src/themes.py

"""Catppuccin 主题配置 - https://catppuccin.com/
Light: Latte (#eff1f5 base, #4c4f69 text)
Dark: Mocha (#1e1e2e base, #cdd6f4 text)
"""

LIGHT_THEME = """
/* Catppuccin Latte - Light Theme */
/* Base: #eff1f5 | Text: #4c4f69 | Primary: #1e66f5 */
/* 全局样式 */
QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-family: "SF Pro Display", "Segoe UI", "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial;
    font-size: 13px;
}

/* 主窗口 */
QMainWindow {
    background-color: #eff1f5;
}

/* 表格样式 */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 12px;
    padding: 8px;
    gridline-color: #e6e9ef;
}

/* 表格行样式 */
QTableWidget::item {
    padding: 10px 6px;
    border: none;
    background-color: transparent;
    border-radius: 6px;
    color: #4c4f69;
}

/* 表格行悬停效果 */
QTableWidget::item:hover {
    background-color: #dfe0ea;
}

/* 表格行选中效果 */
QTableWidget::item:selected {
    background-color: #1e66f5;
    color: #ffffff;
}

/* 表头样式 */
QHeaderView::section {
    background-color: #e6e9ef;
    color: #4c4f69;
    padding: 12px 16px;
    border: none;
    border-bottom: 1px solid #ccd0da;
    font-weight: 600;
    text-align: left;
}

QHeaderView {
    background-color: transparent;
    border: none;
}

/* 按钮样式 */
QPushButton {
    background-color: #ffffff;
    color: #1e66f5;
    border: 1px solid #bcc0cc;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 500;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #f2f4f8;
    border-color: #1e66f5;
}

QPushButton:pressed {
    background-color: #e8edf5;
    border-color: #1e66f5;
}

QPushButton:disabled {
    background-color: #e6e9ef;
    border-color: #ccd0da;
    color: #9ca0b0;
}

/* 输入控件样式 */
QLineEdit, QTextEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #bcc0cc;
    padding: 10px 14px;
    border-radius: 12px;
    color: #4c4f69;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #1e66f5;
    background-color: #f8faff;
}

/* 状态栏样式 */
QStatusBar {
    background-color: #e6e9ef;
    color: #4c4f69;
    padding: 8px 16px;
    border-top: 1px solid #ccd0da;
}

/* 菜单样式 */
QMenu {
    background-color: #fafbfc;
    border: 1px solid #acb0be;
    border-radius: 12px;
    padding: 8px 0;
    color: #2d3749;
}

QMenu::item {
    padding: 10px 24px;
    background-color: transparent;
    border: none;
    border-radius: 8px;
    margin: 2px 8px;
    color: #2d3749;
}

QMenu::item:hover {
    background-color: #e8edf5;
}

QMenu::item:selected {
    background-color: #dce0e8;
    color: #1e66f5;
    font-weight: 500;
}

QMenu::item:disabled {
    color: #9ca0b0;
}

QMenu::separator {
    background-color: #acb0be;
    height: 1px;
    margin: 4px 0;
}

/* 滚动条样式 */
QScrollBar {
    background-color: #eff1f5;
    border-radius: 10px;
    width: 10px;
    height: 10px;
}

QScrollBar::handle {
    background-color: #bcc0cc;
    border-radius: 10px;
    min-width: 24px;
    min-height: 24px;
}

QScrollBar::handle:hover {
    background-color: #acb0be;
}

QScrollBar::add-line, QScrollBar::sub-line {
    background-color: transparent;
}

/* 对话框样式 */
QDialog {
    background-color: #eff1f5;
    border: 1px solid #ccd0da;
    border-radius: 16px;
}

/* 分组框样式 */
QGroupBox {
    background-color: #f8f9fb;
    border: 1px solid #ccd0da;
    border-radius: 12px;
    margin-top: 16px;
    padding: 16px;
    color: #4c4f69;
}

QGroupBox::title {
    color: #4c4f69;
    font-weight: 600;
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
}

/* 复选框样式 */
QCheckBox {
    spacing: 8px;
    color: #4c4f69;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #bcc0cc;
    border-radius: 6px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #1e66f5;
    border-color: #1e66f5;
}

QCheckBox::indicator:unchecked:hover {
    border-color: #acb0be;
}

/* 标签样式 */
QLabel {
    color: #4c4f69;
}

QLabel#lbl_path {
    font-weight: 600;
    color: #1e66f5;
    font-size: 14px;
}

QLabel#loading_label {
    color: #1e66f5;
}

/* 设置按钮特殊样式 */
QPushButton#btn_settings {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    padding: 6px;
    color: #1e66f5;
}

QPushButton#btn_settings:hover {
    background-color: #e8edf5;
}

/* 提示文本 */
QToolTip {
    background-color: #4c4f69;
    color: #eff1f5;
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    padding: 4px 8px;
}
"""

DARK_THEME = """
/* Catppuccin Mocha - Dark Theme */
/* Base: #1e1e2e | Text: #cdd6f4 | Primary: #89b4fa */
/* 全局样式 */
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "SF Pro Display", "Segoe UI", "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial;
    font-size: 13px;
}

/* 主窗口 */
QMainWindow {
    background-color: #1e1e2e;
}

/* 侧边栏 */
QWidget#sidebar {
    background-color: #181825;
    border-right: 1px solid #313244;
}

/* 表格样式 */
QTableWidget {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 12px;
    padding: 8px;
    gridline-color: #313244;
}

/* 表格行样式 */
QTableWidget::item {
    padding: 10px 6px;
    border: none;
    background-color: transparent;
    border-radius: 6px;
    color: #cdd6f4;
}

/* 表格行悬停效果 */
QTableWidget::item:hover {
    background-color: #45475a;
}

/* 表格行选中效果 */
QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

/* 表头样式 */
QHeaderView::section {
    background-color: #313244;
    color: #bac2de;
    padding: 12px 16px;
    border: none;
    border-bottom: 1px solid #45475a;
    font-weight: 600;
    text-align: left;
}

QHeaderView {
    background-color: transparent;
    border: none;
}

/* 按钮样式 */
QPushButton {
    background-color: #313244;
    color: #89b4fa;
    border: 1px solid #45475a;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 500;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #2d2d44;
    border-color: #89b4fa;
}

QPushButton:disabled {
    background-color: #313244;
    border-color: #45475a;
    color: #6c7086;
}

/* 输入控件样式 */
QLineEdit, QTextEdit, QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    padding: 10px 14px;
    border-radius: 12px;
    color: #cdd6f4;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #89b4fa;
    background-color: #313244;
}

/* 状态栏样式 */
QStatusBar {
    background-color: #313244;
    color: #bac2de;
    padding: 8px 16px;
    border-top: 1px solid #45475a;
}

/* 菜单样式 */
QMenu {
    background-color: #313244;
    border: 1px solid #585b70;
    border-radius: 12px;
    padding: 8px 0;
    color: #cdd6f4;
}

QMenu::item {
    padding: 10px 24px;
    background-color: transparent;
    border: none;
    border-radius: 8px;
    margin: 2px 8px;
    color: #cdd6f4;
}

QMenu::item:hover {
    background-color: #414559;
}

QMenu::item:selected {
    background-color: #585b70;
    color: #89b4fa;
    font-weight: 500;
}

QMenu::item:disabled {
    color: #6c7086;
}

QMenu::separator {
    background-color: #585b70;
    height: 1px;
    margin: 4px 0;
}

/* 滚动条样式 */
QScrollBar {
    background-color: #1e1e2e;
    border-radius: 10px;
    width: 10px;
    height: 10px;
}

QScrollBar::handle {
    background-color: #45475a;
    border-radius: 10px;
    min-width: 24px;
    min-height: 24px;
}

QScrollBar::handle:hover {
    background-color: #585b70;
}

QScrollBar::add-line, QScrollBar::sub-line {
    background-color: transparent;
}

/* 对话框样式 */
QDialog {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 16px;
    color: #cdd6f4;
}

/* 分组框样式 */
QGroupBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 12px;
    margin-top: 16px;
    padding: 16px;
    color: #cdd6f4;
}

QGroupBox::title {
    color: #bac2de;
    font-weight: 600;
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
}

/* 复选框样式 */
QCheckBox {
    spacing: 8px;
    color: #cdd6f4;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #45475a;
    border-radius: 6px;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QCheckBox::indicator:unchecked:hover {
    border-color: #585b70;
}

/* 标签样式 */
QLabel {
    color: #cdd6f4;
}

QLabel#lbl_path {
    font-weight: 600;
    color: #89b4fa;
    font-size: 14px;
}

QLabel#loading_label {
    color: #89b4fa;
}

/* 设置按钮特殊样式 */
QPushButton#btn_settings {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    padding: 6px;
    color: #89b4fa;
}

QPushButton#btn_settings:hover {
    background-color: rgba(137, 180, 250, 0.1);
}

/* 提示文本 */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px 8px;
}

/* 分隔线 */
QFrame[frameShape="4"] {
    color: #45475a;
}
"""
