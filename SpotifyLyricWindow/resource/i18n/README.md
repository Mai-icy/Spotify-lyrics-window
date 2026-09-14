# Interface translations

The default UI language is Simplified Chinese (`zh_CN`). English (`en_US`) is
selected in Settings → General → Interface language. Changes are saved when
settings close and take effect after restarting the app. Lyrics, song metadata,
font names, color preset keys and lyrics translation modes are not localized.

`common/i18n.py` installs a Qt `QTranslator` before creating windows, so both
existing `self.tr(...)` calls and generated forms' `translate(...)` calls work.
UTF-8 JSON catalogs need no build tools or additional runtime dependencies.
Missing phrases fall back to the original text; Qt's own Chinese catalog is
loaded for standard Qt controls when available. Native OS dialogs can follow
the operating system language.

To add a language:

1. Add its stable locale code and native display name to `LANGUAGES` in
   `common/i18n.py`.
2. Add `<locale>.json` beside `en_US.json`, retaining the Chinese source keys in
   `messages`. An optional `contexts` object maps Qt class names to phrase maps
   and overrides shared translations when a phrase has different meanings.
3. Wrap new UI copy in `tr(...)`. Keep persisted identifiers and user data out
   of translations. Translate API error text at the display boundary.
4. Check all four settings pages at the minimum window size, download dialogs,
   overlay tooltips, tray menus, and switching back to Chinese after restart.

These catalogs currently contain fixed UI phrases, not plural/disambiguated
messages. Add support for those before introducing count-dependent translations.
