# https://github.com/123panNextGen/123pan
# src/threading_utils.py

from PyQt6 import QtCore
import threading


class WorkerSignals(QtCore.QObject):
    """工作线程信号"""
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)
    log = QtCore.pyqtSignal(str)
    cancel = QtCore.pyqtSignal()
    paused = QtCore.pyqtSignal()
    resumed = QtCore.pyqtSignal()


class ThreadedTask(QtCore.QRunnable):
    """线程任务"""
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.is_cancelled = False
        self.is_paused = False
        # pause event: set() means running, clear() means paused
        self._pause_event = threading.Event()
        self._pause_event.set()

    @QtCore.pyqtSlot()
    def run(self):
        """运行任务"""
        try:
            if self.is_cancelled:
                return
            res = self.fn(*self.args, **self.kwargs, signals=self.signals, task=self)
            if not self.is_cancelled:
                self.signals.result.emit(res)
        except Exception as e:
            if not self.is_cancelled:
                self.signals.error.emit(str(e))
        finally:
            if not self.is_cancelled:
                self.signals.finished.emit()
    
    def cancel(self):
        """取消任务"""
        self.is_cancelled = True
        self.signals.cancel.emit()

    def pause(self):
        """暂停任务"""
        if not self.is_paused:
            self.is_paused = True
            self._pause_event.clear()
            self.signals.paused.emit()

    def resume(self):
        """恢复任务"""
        if self.is_paused:
            self.is_paused = False
            self._pause_event.set()
            self.signals.resumed.emit()
