"""Main-thread input-source initialization for the pinned pynput 1.8.1 backend."""
import threading

from pynput.keyboard import GlobalHotKeys
from pynput._util.darwin import ListenerMixin, keycode_context


class MacGlobalHotKeys(GlobalHotKeys):
    def start(self):
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("macOS hotkeys must be started on the main thread")
        # The stock Darwin Listener._run reads TIS/TSM input-source properties
        # on its worker thread. macOS 26 can abort the process for that call,
        # notably when settings closes and starts a new listener. Copy layout
        # bytes here; no native input-source object is passed to the worker.
        with keycode_context() as context:
            self._keycode_snapshot = context
        super().start()

    def _run(self):
        # Python 3.14's Thread.start/bootstrap also uses _context. Do not put
        # pynput's tuple there until bootstrap has entered the worker's run().
        self._context = self._keycode_snapshot
        try:
            # Keep pynput's normal event tap, permission check, callbacks and
            # stop lifecycle; bypass only Darwin Listener._run's TIS lookup.
            ListenerMixin._run(self)
        finally:
            self._context = None
            self._keycode_snapshot = None
