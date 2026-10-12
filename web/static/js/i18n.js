// Thai / English strings.  Owner: M09 (M10 adds keys for pages 02–04 via PR)
// Rules: every visible string goes through t(); default language is Thai; remember choice in localStorage.
export const I18N = {
  th: {
    "brand.sub": "ระบบเซ็นเซอร์ข้อมูลลูกค้า",
    "nav.mask": "เซ็นเซอร์ Log", "nav.rules": "กฎ Regex", "nav.tests": "Test Suite", "nav.dfa": "Automaton",
    // TODO(M09, M10): add the remaining keys
  },
  en: {
    "brand.sub": "Data Masking Console",
    "nav.mask": "Mask Logs", "nav.rules": "Regex Rules", "nav.tests": "Test Suite", "nav.dfa": "Automaton",
  },
};

export let lang = "th";

/** t("lines", {n: 5}) -> "5 บรรทัด". Falls back to Thai, then to the key itself. */
export function t(key, vars = {}) {
  // TODO(M09): implement lookup + {placeholder} substitution (no regex needed: split/join)
  return I18N[lang][key] ?? I18N.th[key] ?? key;
}

/** Switch language, persist it, re-render every [data-i18n] node and notify pages. */
export function setLang(next) {
  // TODO(M09): update `lang`, localStorage, <html lang>, [data-i18n], [data-i18n-ph], [data-i18n-html];
  //            dispatch window event "langchange" so rules.js / tests.js / dfa.js can re-render
  lang = next;
}
