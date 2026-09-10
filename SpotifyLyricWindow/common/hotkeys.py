"""Select the keyboard listener without changing Windows/Linux behavior."""
import sys


def create_global_hotkeys(bindings):
    from pynput import keyboard

    if sys.platform == "darwin" and keyboard.Listener.__module__ == "pynput.keyboard._darwin":
        from common.mac_hotkeys import MacGlobalHotKeys
        return MacGlobalHotKeys(bindings)
    return keyboard.GlobalHotKeys(bindings)
