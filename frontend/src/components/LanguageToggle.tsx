import { useLanguage } from "../contexts/LanguageContext";

export default function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <button
      onClick={() => setLang(lang === "vi" ? "en" : "vi")}
      className="px-3 py-1 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition text-sm font-medium"
    >
      {lang === "vi" ? "🇻🇳 VI" : "🇬🇧 EN"}
    </button>
  );
}