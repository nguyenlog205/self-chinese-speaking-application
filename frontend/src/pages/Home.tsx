import { Link } from "react-router-dom";
import { useLanguage } from "../contexts/LanguageContext";

export default function Home() {
  const { t } = useLanguage();

  return (
    <div className="max-w-3xl mx-auto text-center">
      <h1 className="text-4xl font-bold text-primary mb-4">
        {t("app.name")}
      </h1>
      <p className="text-lg text-gray-700 dark:text-gray-300 mb-8">
        {t("practice.title")}
      </p>
      <Link
        to="/practice"
        className="inline-block bg-primary text-white px-8 py-3 rounded-lg hover:bg-primary/90 transition"
      >
        {t("nav.practice")}
      </Link>
    </div>
  );
}