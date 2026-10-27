import type { Language } from './language';

// Draft UI copy. A local speaker should review both languages before publication.
const translations: Record<string, { hi: string; 'gom-Deva': string }> = {
  'Emergency services': { hi: 'आपातकालीन सेवाएँ', 'gom-Deva': 'आणीबाणी सेवा' },
  'Back': { hi: 'वापस', 'gom-Deva': 'फाटीं' },
  'Goa helplines. Tap a number to call.': { hi: 'गोवा हेल्पलाइन। फ़ोन करने के लिए नंबर दबाएँ।', 'gom-Deva': 'गोंयच्या मदत क्रमांकां. फोन करपाक क्रमांकाचेर दाबात.' },
  'All emergencies': { hi: 'सभी आपात स्थितियाँ', 'gom-Deva': 'सगळ्या आणीबाणी प्रसंगां खातीर' },
  'Ambulance': { hi: 'एम्बुलेंस', 'gom-Deva': 'रुग्णवाहिका' },
  'Police': { hi: 'पुलिस', 'gom-Deva': 'पोलीस' },
  'Fire & rescue': { hi: 'अग्निशमन और बचाव', 'gom-Deva': 'उजो पालोवप आनी बचाव' },
  'Women’s helpline': { hi: 'महिला हेल्पलाइन', 'gom-Deva': 'महिला मदत क्रमांक' },
  'Child helpline': { hi: 'बाल हेल्पलाइन', 'gom-Deva': 'भुरग्यां खातीर मदत क्रमांक' },
  'Senior citizens': { hi: 'वरिष्ठ नागरिक', 'gom-Deva': 'ज्येष्ठ नागरिक' },
  'Electricity helpline': { hi: 'बिजली हेल्पलाइन', 'gom-Deva': 'वीज मदत क्रमांक' },
  'Waste & recycling': { hi: 'कचरा और पुनर्चक्रण', 'gom-Deva': 'कचरो आनी पुनर्वापर' },
  'Nature & wildlife': { hi: 'प्रकृति और वन्यजीव', 'gom-Deva': 'निसर्ग आनी वन्यजीव' },
  'Water & environment': { hi: 'पानी और पर्यावरण', 'gom-Deva': 'उदक आनी पर्यावरण' },
  'Building & transport': { hi: 'निर्माण और परिवहन', 'gom-Deva': 'बांदकाम आनी वाहतूक' },
  'Water': { hi: 'पानी', 'gom-Deva': 'उदक' },
  'Community & rights': { hi: 'समुदाय और अधिकार', 'gom-Deva': 'समाज आनी हक्क' },
  'Food & farming': { hi: 'भोजन और खेती', 'gom-Deva': 'अन्न आनी शेती' },
  'Culture & heritage': { hi: 'संस्कृति और विरासत', 'gom-Deva': 'संस्कृती आनी वारसो' },
  'Planning & mobility': { hi: 'योजना और आवागमन', 'gom-Deva': 'नियोजन आनी येवजाव' },
  'Health & wellbeing': { hi: 'स्वास्थ्य और देखभाल', 'gom-Deva': 'भलायकी आनी देखभाल' },
};
export function translatePriority(text: string, language: Language): string {
  return language === 'en' ? text : translations[text]?.[language] ?? text;
}
