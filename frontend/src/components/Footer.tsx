import { useLanguage } from "../contexts/LanguageContext";

export default function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="bg-gray-200 dark:bg-gray-800 border-t border-gray-300 dark:border-gray-700">
      <div className="container mx-auto px-4 py-4 text-center text-sm text-gray-600 dark:text-gray-400">
        {t("footer.credit")}
      </div>
    </footer>
  );
}