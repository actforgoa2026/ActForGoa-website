import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

export type Language = 'en' | 'hi' | 'gom-Deva';
const storageKey = 'actforgoa-language';
const valid = (value: string | null): value is Language => value === 'en' || value === 'hi' || value === 'gom-Deva';
const LanguageContext = createContext<{ language: Language; setLanguage: (language: Language) => void }>({ language: 'en', setLanguage: () => {} });

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => {
    try { const saved = localStorage.getItem(storageKey); return valid(saved) ? saved : 'en'; } catch { return 'en'; }
  });
  useEffect(() => { try { localStorage.setItem(storageKey, language); } catch { /* Storage may be unavailable. */ } }, [language]);
  return <LanguageContext.Provider value={{ language, setLanguage }}>{children}</LanguageContext.Provider>;
}
export const useLanguage = () => useContext(LanguageContext);

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();
  return <select className="language-switcher" aria-label="Language / भाषा / भास" value={language} onChange={event => { if (valid(event.target.value)) setLanguage(event.target.value); }}>
    <option value="en">English</option><option value="hi">हिन्दी</option><option value="gom-Deva">कोंकणी (देवनागरी)</option>
  </select>;
}
