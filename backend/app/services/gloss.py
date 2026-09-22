"""Close readings that fire only when the retrieved quotation contains the source phrases."""

from __future__ import annotations

GLOSSES = [
    {
        "need": ["परमात्मा सर्वत्र है", "के अलावा और कुछ है ही नहीं"],
        "en": "The granth says Paramatma is everywhere. In this universe there is nothing apart from Paramatma.",
        "hi": "ग्रंथ कहता है कि परमात्मा सर्वत्र है। इस ब्रह्माण्ड में परमात्मा के अलावा और कुछ है ही नहीं।",
        "gu": "ગ્રંથ કહે છે કે પરમાત્મા સર્વત્ર છે. આ બ્રહ્માંડમાં પરમાત્મા સિવાય બીજું કશું છે જ નહીં.",
        "hinglish": "Granth kehta hai ki parmatma sarvatra hai. Is brahmand mein parmatma ke alawa aur kuch hai hi nahi.",
    },
    {
        "need": ["देव तत्त्व", "दानव तत्त्व", "मनुष्य तत्त्व"],
        "en": "In the granth’s wording, manushya tattva lies between dev tattva and danav tattva. These tattvas are present in a lesser or greater proportion, so no person is wholly good or wholly bad.",
        "hi": "ग्रंथ के शब्दों में, देव तत्त्व और दानव तत्त्व के बीच मनुष्य तत्त्व होता है। ये तत्त्व कम या ज्यादा अनुपात में होते हैं, इसलिए कोई मनुष्य संपूर्ण अच्छा या संपूर्ण बुरा नहीं होता।",
        "gu": "ગ્રંથના શબ્દોમાં, દેવ તત્ત્વ અને દાનવ તત્ત્વની વચ્ચે મનુષ્ય તત્ત્વ છે. આ તત્ત્વો ઓછા અથવા વધુ પ્રમાણમાં હોય છે, તેથી કોઈ મનુષ્ય સંપૂર્ણ સારો કે સંપૂર્ણ ખરાબ નથી.",
        "hinglish": "Granth ke shabdon mein, dev tattva aur danav tattva ke beech manushya tattva hota hai. Ye tattva kam ya zyada hote hain, isliye koi manushya sampurna accha ya bura nahi hota.",
    },
    {
        "need": ["सौंप देना समर्पण है"],
        "en": "The granth says surrender is handing the whole control of one’s life to Paramatma through the Sadguru.",
        "hi": "ग्रंथ कहता है कि अपने जीवन के नियंत्रण को संपूर्णतः सदगुरु के माध्यम से परमात्मा को सौंप देना समर्पण है।",
        "gu": "ગ્રંથ કહે છે કે જીવનનું સંપૂર્ણ નિયંત્રણ સદ્ગુરુના માધ્યમથી પરમાત્માને સોંપી દેવું એ સમર્પણ છે.",
        "hinglish": "Granth kehta hai ki apne jeevan ka niyantran sadguru ke madhyam se parmatma ko saump dena samarpan hai.",
    },
    {
        "need": ["साधक’ यानी", "साधनारत"],
        "en": "The granth says a sadhak is one who is engaged in sadhana: the body has been brought under discipline, and the work has turned toward the atma.",
        "hi": "ग्रंथ कहता है कि साधक वह है जो साधनारत है, साधना में लीन है। शरीर पर नियंत्रण साध चुका है और अब आत्मा पर नियंत्रण कर रहा है।",
        "gu": "ગ્રંથ કહે છે કે સાધક એ છે જે સાધનારત છે, સાધનામાં લીન છે. શરીર પર નિયંત્રણ સાધી ચૂક્યો છે અને હવે આત્મા તરફ વળ્યો છે.",
        "hinglish": "Granth kehta hai ki sadhak woh hai jo sadhanarat hai. Shareer par niyantran saadh chuka hai, aur ab aatma par niyantran kar raha hai.",
    },
    {
        "need": ["माध्यम है वह गुरुतत्व"],
        "en": "The granth says the medium through which Paramatma’s shakti is received is gurutattva.",
        "hi": "ग्रंथ कहता है कि परमात्मा की शक्ति को ग्रहण करने का जो माध्यम है, वह गुरुतत्व है।",
        "gu": "ગ્રંથ કહે છે કે પરમાત્માની શક્તિને ગ્રહણ કરવાનું જે માધ્યમ છે, તે ગુરુતત્ત્વ છે.",
        "hinglish": "Granth kehta hai ki parmatma ki shakti ko lene ka jo madhyam hai, woh gurutattva hai.",
    },
    {
        "need": ["अहिंसा", "प्रथम धर्म"],
        "en": "The granth states that ahimsa is a human being’s first dharma.",
        "hi": "ग्रंथ कहता है कि अहिंसा मनुष्य का प्रथम धर्म है।",
        "gu": "ગ્રંથ કહે છે કે અહિંસા મનુષ્યનો પ્રથમ ધર્મ છે.",
        "hinglish": "Granth kehta hai ki ahimsa manushya ka pratham dharma hai.",
    },
    {
        "need": ["आज में जियो", "अहंकार"],
        "en": "The granth says: live in today and remain in today; that is what is in hand. It also says to leave the ego of ‘I’.",
        "hi": "ग्रंथ कहता है: आज में जियो और आज में रहो, बस यही हाथ में है। और ‘मैं’ के अहंकार को छोड़ो।",
        "gu": "ગ્રંથ કહે છે: આજમાં જીવો અને આજમાં રહો, બસ એ જ હાથમાં છે. અને ‘હું’ના અહંકારને છોડો.",
        "hinglish": "Granth kehta hai: aaj mein jiyo aur aaj mein raho, bas yahi haath mein hai. Aur ‘main’ ka ahankar chhodo.",
    },
    {
        "need": ["आज में जियो"],
        "en": "The granth says: live in today and remain in today; that is what is in hand.",
        "hi": "ग्रंथ कहता है: आज में जियो और आज में रहो, बस यही हाथ में है।",
        "gu": "ગ્રંથ કહે છે: આજમાં જીવો અને આજમાં રહો, બસ એ જ હાથમાં છે.",
        "hinglish": "Granth kehta hai: aaj mein jiyo aur aaj mein raho, bas yahi haath mein hai.",
    },
    {
        "need": ["गुणधर्म है - प्रेम", "पानी का गुणधर्म", "आग का गुणधर्म"],
        "en": "The granth says love is the quality of a human being, just as flowing is the quality of water and burning is the quality of fire.",
        "hi": "ग्रंथ कहता है कि जैसे पानी का गुणधर्म बहना और आग का गुणधर्म जलना है, वैसे ही मनुष्य का गुणधर्म प्रेम करना है।",
        "gu": "ગ્રંથ કહે છે કે જેમ પાણીનો ગુણધર્મ વહેવાનો અને અગ્નિનો ગુણધર્મ બળવાનો છે, તેમ મનુષ્યનો ગુણધર્મ પ્રેમ કરવાનો છે.",
        "hinglish": "Granth kehta hai ki jaise paani ka gunadharm behna aur aag ka gunadharm jalna hai, waise hi manushya ka gunadharm prem karna hai.",
    },
    {
        "need": ["विश्वशांति", "आत्मशांति"],
        "en": "The granth says world peace begins with one’s own inner peace.",
        "hi": "ग्रंथ कहता है कि विश्वशांति की शुरुआत स्वयं की आत्मशांति से होगी।",
        "gu": "ગ્રંથ કહે છે કે વિશ્વશાંતિની શરૂઆત પોતાની આત્મશાંતિથી થશે.",
        "hinglish": "Granth kehta hai ki vishwashanti ki shuruaat khud ki aatmashanti se hogi.",
    },
    {
        "need": ["भीतर की अशांति"],
        "en": "The granth says outer unrest comes from inner unrest. It asks that the inner state not be allowed to become restless, and it points to dhyan and gurumantra jaap for peace of mind. This is not a personal instruction to you, and it is not medical advice.",
        "hi": "ग्रंथ कहता है कि बाहर की अशांति भीतर की अशांति से बढ़ती है। भीतर की स्थिति अशांत न होने दे, और मन की शांति के लिए ध्यान तथा गुरुमंत्र जाप की बात है। यह आपका व्यक्तिगत आदेश नहीं है और चिकित्सा सलाह नहीं है।",
        "gu": "ગ્રંથ કહે છે કે બહારની અશાંતિ અંદરની અશાંતિથી વધે છે. અંદરની સ્થિતિ અશાંત ન થવા દો, અને મનની શાંતિ માટે ધ્યાન તથા ગુરુમંત્ર જાપની વાત છે. આ તમારો અંગત આદેશ નથી અને તબીબી સલાહ નથી.",
        "hinglish": "Granth kehta hai ki bahar ki ashanti andar ki ashanti se badhti hai. Andar ki sthiti ashant mat hone do. Man ki shanti ke liye dhyan aur gurumantra jaap ki baat hai. Yeh aapka personal order nahi hai, aur medical advice nahi hai.",
    },
    {
        "need": ["पद्धति नहीं है", "एक संस्कार"],
        "en": "The granth says Samarpan Dhyan is not a method of holding the mind on the breath, a flame, or pranayama. It is a sanskar of one pure atma upon another, received by surrendering fully to Paramatma through the medium.",
        "hi": "ग्रंथ कहता है कि समर्पण ध्यान साँस, ज्योति या प्राणायाम की पद्धति नहीं है। यह एक पवित्र आत्मा द्वारा दूसरी पवित्र आत्मा पर किया गया संस्कार है।",
        "gu": "ગ્રંથ કહે છે કે સમર્પણ ધ્યાન શ્વાસ, જ્યોત કે પ્રાણાયામની પદ્ધતિ નથી. તે એક પવિત્ર આત્મા દ્વારા બીજી પવિત્ર આત્મા પર થયેલું સંસ્કાર છે.",
        "hinglish": "Granth kehta hai ki samarpan dhyan saans, jyoti ya pranayama ki paddhati nahi hai. Yeh ek pavitra aatma dwara doosri pavitra aatma par kiya gaya sanskar hai.",
    },
    {
        "need": ["30 मिनट"],
        "en": "The granth speaks of a disciple who, in this dhyan, becomes fully surrendered to the Guru for only 30 minutes a day, and of the Guru’s spiritual state then being received. No result is promised here.",
        "hi": "ग्रंथ एक शिष्य की बात करता है जो इस ध्यान में प्रतिदिन केवल 30 मिनट गुरु के प्रति संपूर्ण समर्पित हो जाता है, और तब गुरु की आध्यात्मिक स्थिति अनायास प्राप्त होने की बात है। यहाँ किसी फल की गारंटी नहीं जोड़ी गई।",
        "gu": "ગ્રંથ એક શિષ્યની વાત કરે છે જે આ ધ્યાનમાં દરરોજ માત્ર 30 મિનિટ ગુરુ પ્રત્યે સંપૂર્ણ સમર્પિત થાય છે. અહીં કોઈ ફળની ખાતરી ઉમેરાઈ નથી.",
        "hinglish": "Granth ek shishya ki baat karta hai jo is dhyan mein roz sirf 30 minute guru ke prati sampurna samarpit ho jata hai. Yahan koi guarantee nahi jodi gayi.",
    },
    {
        "need": ["आदर्श साधक"],
        "en": "The granth says the ideal is always the ideal sadhak: one whose chitta remains at the Guru’s feet and who lives in the present.",
        "hi": "ग्रंथ कहता है कि आदर्श सदैव आदर्श साधक ही होना चाहिए, जिसका चित्त गुरुचरण पर रहता है और जो वर्तमान में रहता है।",
        "gu": "ગ્રંથ કહે છે કે આદર્શ હંમેશા આદર્શ સાધક હોવો જોઈએ, જેનું ચિત્ત ગુરુચરણ પર રહે છે અને જે વર્તમાનમાં રહે છે.",
        "hinglish": "Granth kehta hai ki aadarsh hamesha aadarsh sadhak hona chahiye, jiska chitta gurucharan par rehta hai aur jo vartaman mein rehta hai.",
    },
    {
        "need": ["स्वाभिमान और अहंकार"],
        "en": "The granth says the difference between self-respect and ego is very subtle, and one may not notice when self-respect has turned into ego.",
        "hi": "ग्रंथ कहता है कि स्वाभिमान और अहंकार में बड़ा सूक्ष्म अंतर है, और स्वाभिमान कब अहंकार बन गया, इसका पता नहीं चलता।",
        "gu": "ગ્રંથ કહે છે કે સ્વાભિમાન અને અહંકાર વચ્ચે બહુ સૂક્ષ્મ અંતર છે, અને સ્વાભિમાન ક્યારે અહંકાર બની ગયું તે ખબર પડતી નથી.",
        "hinglish": "Granth kehta hai ki swabhiman aur ahankar mein bahut sookshma antar hai, aur swabhiman kab ahankar ban gaya, pata nahi chalta.",
    },
    {
        "need": ["आभामण्डल है यानी"],
        "en": "The granth says the aura means the person is alive, and that it ends three days after death.",
        "hi": "ग्रंथ कहता है कि आभामण्डल है यानी मनुष्य जीवित है, और मृत्यु के तीन दिन बाद यह समाप्त हो जाता है।",
        "gu": "ગ્રંથ કહે છે કે આભામંડળ એટલે મનુષ્ય જીવિત છે, અને મૃત્યુના ત્રણ દિવસ પછી તે સમાપ્ત થાય છે.",
        "hinglish": "Granth kehta hai ki aabhamandal hai yaani manushya jeevit hai, aur mrityu ke teen din baad yeh samaapt ho jata hai.",
    },
    {
        "need": ["समाधि' होती है"],
        "en": "The granth says the Sadguru’s samadhi is the lasting dwelling of those powers. One can go there with the chitta, and after leaving the body the chitta itself returns there.",
        "hi": "ग्रंथ कहता है कि सदगुरु की शक्तियों का स्थाई निवास स्थान उसकी समाधि होती है। वहाँ चित्त से भी जाया जा सकता है।",
        "gu": "ગ્રંથ કહે છે કે સદ્ગુરુની શક્તિઓનું સ્થાયી નિવાસસ્થાન તેમની સમાધિ છે. ત્યાં ચિત્તથી પણ જઈ શકાય છે.",
        "hinglish": "Granth kehta hai ki sadguru ki shaktiyon ka sthayi nivas unki samadhi hoti hai. Wahan chitta se bhi jaya ja sakta hai.",
    },
]


def close_reading(lang: str, text: str) -> str | None:
    blob = text or ""
    for item in GLOSSES:
        if all(part in blob for part in item["need"]):
            return item.get(lang) or item.get("hi")
    return None
