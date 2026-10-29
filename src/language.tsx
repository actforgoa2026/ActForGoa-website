import {MorphSelect} from './components/arc/morph-select/morph-select';
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
  return <MorphSelect className="language-control" label="Language / भाषा / भास" hideLabel value={language} onValueChange={value => {if (valid(value)) setLanguage(value);}} align="end" items={[{value:'en',label:'English'},{value:'hi',label:'हिन्दी'},{value:'gom-Deva',label:'कोंकणी (देवनागरी)'}]}/>;
}
