"""AppKit application/overlay policies (call on the GUI thread only)."""


def configure_accessory_app():
    """Keep windows and the status item usable without a Dock application tile."""
    import AppKit

    app = AppKit.NSApplication.sharedApplication()
    if not app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory):
        import logging
        logging.getLogger(__name__).warning('macOS refused accessory activation policy')


def activate_application():
    """Activate only on an explicit user request, such as opening settings."""
    import AppKit

    AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(True)


def configure_overlay(win_id: int, always_on_top: bool):
    # Keep Cocoa imports local: Windows/Linux and Qt's offscreen tests do not
    # need PyObjC. QWidget.winId() on Cocoa is an NSView, not an NSWindow.
    import AppKit
    import objc

    window = objc.objc_object(c_void_p=int(win_id)).window()
    if window is None:
        return

    window.setHidesOnDeactivate_(False)
    # A transparent native panel can cast a shadow around each opaque glyph,
    # and around the rectangular background when the mouse enters the panel.
    window.setHasShadow_(False)
    # Match Qt's stay-on-top level; Qt lowers floating-level panels on deactivation.
    window.setLevel_(AppKit.NSModalPanelWindowLevel if always_on_top else AppKit.NSNormalWindowLevel)

    # Qt normally chooses MoveToActiveSpace for panels. It is mutually
    # exclusive with CanJoinAllSpaces, which a global lyrics overlay needs.
    managed = (AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
               | AppKit.NSWindowCollectionBehaviorMoveToActiveSpace
               | AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary)
    behavior = int(window.collectionBehavior()) & ~managed
    if always_on_top:
        behavior |= (AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
                     | AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary)
    window.setCollectionBehavior_(behavior)
