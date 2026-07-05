const fallbackI18n = { locale: "ja", translations: {} };
let i18n;

function getI18n() {
  if (i18n) {
    return i18n;
  }

  const element = document.getElementById("diet-i18n");

  if (!element?.textContent) {
    i18n = fallbackI18n;
    return i18n;
  }

  i18n = JSON.parse(element.textContent);
  return i18n;
}

export function translate(key) {
  return getI18n().translations?.[key] || key;
}

export function currentLocale() {
  return getI18n().locale || "ja";
}
