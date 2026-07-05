function getI18n() {
  const element = document.getElementById("diet-i18n");

  if (!element?.textContent) {
    return { locale: "ja", translations: {} };
  }

  return JSON.parse(element.textContent);
}

export function translate(key) {
  return getI18n().translations?.[key] || key;
}

export function currentLocale() {
  return getI18n().locale || "ja";
}

