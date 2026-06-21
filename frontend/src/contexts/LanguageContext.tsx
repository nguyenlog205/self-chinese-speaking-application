import { createContext, useContext, useState, ReactNode } from "react";

type Language = "vi" | "en";

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  vi: {
    "app.name": "Tập Shuỏ",
    "nav.home": "Trang chủ",
    "nav.practice": "Luyện nói",
    "nav.about": "Về chúng tôi",
    "status.online": "Online",
    "status.offline": "Offline",
    "about.title": "Về đội ngũ phát triển",
    "about.team": "Đội ngũ phát triển",
    "about.member": "Thành viên",
    "footer.credit": "© 2026 Tập Shuỏ - Phát triển bởi đội ngũ Luyện nghe tiếng Trung",
    "practice.title": "Luyện nói",
    "practice.text": "Nhập văn bản",
    "practice.speak": "Phát âm",
    "practice.record": "Ghi âm",
    "practice.score": "Điểm số",
    "practice.generating": "Đang tạo...",
    "practice.recording": "Đang ghi âm...",
    "practice.wer_explanation": "WER (Word Error Rate): tỷ lệ lỗi so với văn bản tham khảo. 0.00 là hoàn hảo, 1.00 là sai hoàn toàn.",
    "practice.you_said": "Bạn nói",
    "practice.reference": "Văn bản tham khảo",
    "practice.instructions": "Nhập văn bản, nghe mẫu, sau đó bấm Ghi âm và đọc theo. Hệ thống sẽ chấm điểm phát âm của bạn dựa trên độ chính xác.",
    "practice.alert.empty_text": "Vui lòng nhập văn bản.",
    "practice.alert.server_error": "Máy chủ trả về lỗi: ",
    "practice.alert.backend_error": "Lỗi backend: ",
    "practice.alert.network_error": "Lỗi mạng: ",
    "practice.alert.mic_error": "Không thể truy cập microphone.",
    "practice.alert.empty_ref": "Vui lòng nhập văn bản tham khảo.",
    "practice.alert.scoring_error": "Chấm điểm thất bại.",
  },
  en: {
    "app.name": "Tập Shuỏ",
    "nav.home": "Home",
    "nav.practice": "Practice",
    "nav.about": "About Us",
    "status.online": "Online",
    "status.offline": "Offline",
    "about.title": "About the Development Team",
    "about.team": "Development Team",
    "about.member": "Members",
    "footer.credit": "© 2026 Tập Shuỏ - Developed by Chinese Listening Team",
    "practice.title": "Speaking Practice",
    "practice.text": "Enter text",
    "practice.speak": "Speak",
    "practice.record": "Record",
    "practice.score": "Score",
    "practice.generating": "Generating...",
    "practice.recording": "Recording...",
    "practice.wer_explanation": "WER (Word Error Rate): ratio of errors compared to reference text. 0.00 is perfect, 1.00 is completely wrong.",
    "practice.you_said": "You said",
    "practice.reference": "Reference",
    "practice.instructions": "Enter text, listen to the sample, then click Record and read aloud. The system will score your pronunciation based on accuracy.",
    "practice.alert.empty_text": "Please enter some text.",
    "practice.alert.server_error": "Server returned error: ",
    "practice.alert.backend_error": "Backend error: ",
    "practice.alert.network_error": "Network error: ",
    "practice.alert.mic_error": "Cannot access microphone.",
    "practice.alert.empty_ref": "Please enter reference text.",
    "practice.alert.scoring_error": "Scoring failed.",
  },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [lang, setLang] = useState<Language>(() => {
    const saved = localStorage.getItem("lang") as Language;
    return saved || "vi";
  });

  const t = (key: string): string => {
    return translations[lang]?.[key] || key;
  };

  const handleSetLang = (l: Language) => {
    setLang(l);
    localStorage.setItem("lang", l);
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang: handleSetLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
};