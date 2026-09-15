"""Startup-only UI localization using existing Qt tr()/translate() calls."""
import json
import logging
from pathlib import Path

from PyQt6.QtCore import QLibraryInfo, QTranslator


LANGUAGES = (('zh_CN', '简体中文'), ('en_US', 'English'))
TRANSLATIONS_PATH = Path(__file__).resolve().parents[2] / 'resource' / 'i18n'
logger = logging.getLogger(__name__)


def supported_language(language):
    return language if language in dict(LANGUAGES) else 'zh_CN'


class CatalogTranslator(QTranslator):
    """Shared UI phrases, with optional per-context overrides for future locales."""

    def __init__(self, catalog, parent=None):
        super().__init__(parent)
        self.messages = catalog.get('messages', {})
        self.contexts = catalog.get('contexts', {})

    def isEmpty(self):
        return not (self.messages or self.contexts)

    def translate(self, context, sourceText, disambiguation=None, n=-1):
        # None maps to a null QString, allowing Qt translators/source fallback.
        return self.contexts.get(context, {}).get(sourceText, self.messages.get(sourceText))


def install_translations(app, language):
    """Call before constructing widgets. Settings only change the next startup."""
    for translator in getattr(app, '_ui_translators', ()):
        app.removeTranslator(translator)
        translator.deleteLater()
    app._ui_translators = []  # Keep Python overrides alive for the app lifetime.
    language = supported_language(language)
    if language != 'zh_CN':
        try:
            with (TRANSLATIONS_PATH / f'{language}.json').open(encoding='utf-8') as source:
                catalog = json.load(source)
            translator = CatalogTranslator(catalog, app)
            app.installTranslator(translator)
            app._ui_translators.append(translator)
        except (OSError, ValueError):
            logger.exception('Unable to load UI language %s; using Chinese', language)
            language = 'zh_CN'
    if language == 'zh_CN':
        qt_translator = QTranslator(app)
        if qt_translator.load('qtbase_zh_CN', QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
            app.installTranslator(qt_translator)
            app._ui_translators.append(qt_translator)
    app.setProperty('uiLanguage', language)
