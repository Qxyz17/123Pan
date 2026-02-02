# https://github.com/123panNextGen/123pan
# src/ui_theme_manager.py

"""UI主题管理器"""

from PyQt6 import QtGui
from themes import LIGHT_THEME, DARK_THEME


class ThemeManager:
    """主题管理类"""
    
    def __init__(self, window):
        self.window = window
        self.is_dark_mode = False
        self.on_theme_changed = None  # 主题改变回调
        self.detect_and_apply_theme()
    
    def detect_system_theme(self):
        """检测系统是否为深色模式"""
        palette = self.window.palette()
        bg_color = palette.color(QtGui.QPalette.ColorRole.Base)
        brightness = (bg_color.red() + bg_color.green() + bg_color.blue()) / 3
        return brightness < 128
    
    def detect_and_apply_theme(self):
        """检测系统主题并应用"""
        self.is_dark_mode = self.detect_system_theme()
        self.apply_theme()
    
    def apply_theme(self):
        """应用当前主题"""
        if self.is_dark_mode:
            self.window.setStyleSheet(DARK_THEME)
        else:
            self.window.setStyleSheet(LIGHT_THEME)
        
        # 触发主题改变回调，允许重新应用自定义样式
        if self.on_theme_changed:
            self.on_theme_changed()
    
    def toggle_theme(self):
        """切换主题"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
    
    def check_theme_change(self):
        """检查系统主题是否已变化"""
        new_dark_mode = self.detect_system_theme()
        if new_dark_mode != self.is_dark_mode:
            self.is_dark_mode = new_dark_mode
            self.apply_theme()
