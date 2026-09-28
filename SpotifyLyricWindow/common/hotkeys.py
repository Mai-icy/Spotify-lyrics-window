"""Permission checks and platform-specific keyboard listener selection."""
import sys


def has_hotkey_permission():
    if sys.platform != "darwin":
        return True
    # Check before importing pynput or creating an event tap. Never prompt here.
    from ApplicationServices import AXIsProcessTrusted
    from Quartz import CGPreflightListenEventAccess

    return bool(AXIsProcessTrusted() and CGPreflightListenEventAccess())


def request_hotkey_permission(permission):
    """Only call after the user explicitly clicks an authorization button."""
    if sys.platform != "darwin":
        return
    if permission == "accessibility":
        from ApplicationServices import AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt
        AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: True})
    elif permission == "input_monitoring":
        from Quartz import CGRequestListenEventAccess
        CGRequestListenEventAccess()


def create_global_hotkeys(bindings):
    from pynput import keyboard

    if sys.platform == "darwin" and keyboard.Listener.__module__ == "pynput.keyboard._darwin":
        from common.macos.hotkeys import MacGlobalHotKeys
        return MacGlobalHotKeys(bindings)
    return keyboard.GlobalHotKeys(bindings)
