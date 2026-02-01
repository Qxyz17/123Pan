# https://github.com/123panNextGen/123pan
# src/threading_utils.py

from PyQt6 import QtCore


class WorkerSignals(QtCore.QObject):
    """工作线程信号"""
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)
    log = QtCore.pyqtSignal(str)
    cancel = QtCore.pyqtSignal()


class ThreadedTask(QtCore.QRunnable):
    """线程任务"""
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.is_cancelled = False

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
