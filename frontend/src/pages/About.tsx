import { useLanguage } from "../contexts/LanguageContext";

export default function About() {
  const { t } = useLanguage();

  const members = [
    { name: "Nguyễn Hoàng Long", role: "Backend Developer" },
    { name: "Nguyễn Hoàng Long", role: "Frontend Developer" },
    { name: "Nguyễn Hoàng Long", role: "AI Engineer" },
  ];

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-primary mb-4">
        {t("about.title")}
      </h2>
      <p className="mb-6 text-gray-700 dark:text-gray-300">
        {t("about.team")}
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        {members.map((m, i) => (
          <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
            <p className="font-semibold">{m.name}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{m.role}</p>
          </div>
        ))}
      </div>
    </div>
  );
}