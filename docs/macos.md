# macOS MediaRemote backend

The active backend uses `macos-mediaremote-python==0.1.0a1` from PyPI
(import name: `macos_mediaremote`). Its wheel bundles the native framework and
upstream Perl script. Python 3.11+ is required. Install with
`python -m pip install -r requirements.txt`; no local CMake build is needed.

## Lazy loading and threading

- The dependency has a `sys_platform == "darwin"` marker. Windows/Linux do not
  install it, and their existing backend implementations are unchanged.
- The lyrics window imports `MacMediaSession` only inside its macOS initialization
  branch. Importing that module, or constructing the session before its deferred
  start, does not import the PyPI package or start a helper.
- The package is imported at the deferred macOS start. Missing dependencies fail
  gracefully and leave the application's Spotify API fallback available.
- A Python worker thread runs the package's asyncio stream. Raw snapshots cross
  into Qt through queued signals; snapshot processing and UI notifications stay
  on the Qt thread. The package handles protocol parsing, bounded buffers,
  initialization timeout, stderr draining and helper cleanup.
- Closing cancels the subscription task so its async context reaps the helper.
  Normal silence does not time out, and fatal failures are not endlessly retried.

## Contract and limitations

Only Spotify Desktop (`com.spotify.client`) is accepted. Public application
positions/durations remain milliseconds; raw package events preserve upstream
microseconds, while the package's `seek()` accepts seconds. The existing snapshot
clock, pause handling, track identity and event ordering remain in the application.

Controls use the package's public async methods on existing application worker
threads. Before dispatch, a fresh `get()` must match Spotify's bundle ID and the
cached PID; a mismatch or error returns failure for Spotify API fallback.
This is not the old in-helper native guard: querying and sending are separate
operations. The package targets global Now Playing and preserves upstream's
implicit application-launch behavior. An ownership change after checking can
still redirect a command or launch a player; successful dispatch is not a player
acknowledgement.

Version 0.1.0a1 is an alpha release, pins upstream v0.7.7, and preserves its
initialization ordering. The first snapshot is not a subscription-ready barrier.
The former subscribe-before-snapshot patch is not applied by this integration.
MediaRemote remains private API and may break after a macOS update. Spotify
authentication/metadata lookup remain part of the application's fallback workflow.

For desktop packaging, include the installed package's native data and licenses;
a plain Python import alone is not sufficient to collect all helper resources.

## Verification

```sh
python -m pytest -q
```

This runs the repository's existing tests. Additional macOS regression probes
are currently local-only and are not included in this repository or CI. Those
probes cover package mapping, thread delivery, cancellation, owner checks,
errors and lazy imports with a fake package client. Local read-only native
checks also verify reads, subscriptions and helper cleanup using the installed
PyPI wheel, without playback commands or a synthetic-player probe. An empty
successful read does not prove live Spotify compatibility.

Do interactive play/pause, next/previous and seek checks only with explicit user
approval. Also verify Spotify exit/restart and system-player changes. Native
macOS testing does not replace Windows/Linux desktop regression testing.

### Lyrics overlay

`common/mac_window.py` configures the Qt Cocoa panel using public AppKit APIs,
independently of the private MediaRemote helper. It disables hide-on-deactivate,
sets a floating/normal level according to the topmost preference, and replaces
Qt's `MoveToActiveSpace` behavior with `CanJoinAllSpaces | FullScreenAuxiliary`
when topmost is enabled. The policy is reapplied after each native show, including
flag changes and horizontal/vertical layout rebuilds. Windows/Linux flags are
unchanged. macOS font fallback uses PingFang SC without rewriting saved preferences.

Local Cocoa/rendering probes use an isolated working copy to avoid writing
real user preferences. They check native levels, Space flags, transparency,
font fallback, font selectors, show/hide and layout switches without connecting
to Spotify. These probes are not yet included in the repository.
Manually check app switching, Mission Control desktop
switches, fullscreen apps, and Stage Manager; Space flags alone do not prove
coverage over every fullscreen application or system/security surface.

### Global hotkeys and settings close

`common/mac_hotkeys.py` adapts the pinned pynput 1.8.1 Darwin listener. Its
input-source/layout snapshot is taken by `start()` on the main thread; the worker
only runs the existing event tap. Reading TIS/TSM properties on the worker can
trigger a fatal dispatch-queue assertion on macOS 26 when closing settings
restarts hotkeys. Recheck this adapter when upgrading pynput: it uses the
backend's internal `ListenerMixin` and `keycode_context`. Accessibility/input
monitoring permission is still required for global shortcuts; this fix does not
grant or bypass it.

Local settings checks exercise repeated open/close cycles and disabling/
re-enabling shortcuts with the native keyboard backend in an isolated
configuration. They do not send keyboard events or control Spotify and are not
yet included in the repository. A dummy keyboard backend cannot detect this
native crash, so interactive macOS validation remains necessary.
