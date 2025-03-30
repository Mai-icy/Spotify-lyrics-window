#!/usr/bin/python
# -*- coding:utf-8 -*-
from functools import wraps, partial
from types import MethodType

from PyQt6.QtCore import QThread, pyqtSignal


class ThreadManager:
    def __init__(self):
        self.threads = []

    def add_thread(self, thread):
        self.threads.append(thread)
        thread.finished.connect(lambda: self.remove_thread(thread))

    def remove_thread(self, thread):
        self.threads.remove(thread)
        thread.deleteLater()


thread_manager = ThreadManager()


def thread_drive(done_emit_func=None):
    """修饰线程驱动的类成员函数（槽函数必须依附于设置槽函数的线程）"""
    def outer(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            work_thread = WorkThread(func, self, *args, **kwargs)
            thread_manager.add_thread(work_thread)
            if done_emit_func:
                res_func = MethodType(done_emit_func, self)
                work_thread.finished.connect(res_func)
            work_thread.start()
            self.work_thread = work_thread

        return wrapper
    return outer


class WorkThread(QThread):
    thread_all_done_signal = pyqtSignal(object)
    done_signal = pyqtSignal(object)
    _running_num = 0

    def __init__(self, work_func, *args, **kwargs):
        super(WorkThread, self).__init__()
        self.work = partial(work_func, *args, **kwargs)

    def work(self):
        raise NotImplementedError("The 'work' function has not been set")

    def run(self):
        try:
            self.__class__._running_num += 1
            self.work()
        finally:
            self.__class__._running_num -= 1
            self.done_signal.emit('')

        if self.__class__._running_num == 0:
            self.thread_all_done_signal.emit('')
