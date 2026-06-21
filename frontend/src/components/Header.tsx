import { Link, useLocation } from "react-router-dom";
import { useLanguage } from "../contexts/LanguageContext";
import StatusBadge from "./StatusBadge";
import ThemeToggle from "./ThemeToggle";
import LanguageToggle from "./LanguageToggle";

export default function Header() {
  const { t } = useLanguage();
  const location = useLocation();

  const navItems = [
    { path: "/", label: t("nav.home") },
    { path: "/practice", label: t("nav.practice") },
    { path: "/about", label: t("nav.about") },
  ];

  return (
    <header className="bg-primary text-white shadow-lg">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between flex-wrap gap-3">
        {/* Logo */}
        <Link to="/" className="text-2xl font-bold tracking-wide">
          {t("app.name")}
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-6 flex-wrap">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`hover:text-gray-200 transition ${
                location.pathname === item.path
                  ? "border-b-2 border-white font-semibold"
                  : ""
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Right controls */}
        <div className="flex items-center gap-3">
          <StatusBadge />
          <LanguageToggle />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}