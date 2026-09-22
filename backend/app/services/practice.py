"""Practical readings of the retrieved lines. A benefit is included only when that line states it."""

from __future__ import annotations

# Each item fires only when every phrase in `need` is in the quotation.
# `benefit_need`, when set, must also be present before the benefit sentence is used.
PRACTICES = [
    {
        "need": ["30 मिनट", "समर्पित"],
        "benefit_need": ["आध्यात्मिक स्थिति", "प्राप्त"],
        "hi": "ग्रंथ के अनुसार यह करें: इस ध्यान में प्रतिदिन केवल 30 मिनट अपने गुरु के प्रति संपूर्ण समर्पित हो जाएँ।",
        "en": "According to these lines: in this dhyan, become fully surrendered to the Guru for only 30 minutes a day.",
        "gu": "ગ્રંથ પ્રમાણે આ કરો: આ ધ્યાનમાં દરરોજ માત્ર 30 મિનિટ ગુરુ પ્રત્યે સંપૂર્ણ સમર્પિત થાઓ.",
        "hinglish": "Granth ke anusar aap yeh karo: is dhyan mein roz sirf 30 minute apne guru ke prati sampurna samarpit ho jao.",
        "benefit": {
            "hi": " इन्हीं पंक्तियों में लिखा है कि तब गुरु की आध्यात्मिक स्थिति अनायास शिष्य को प्राप्त हो जाती है। यह फल यहाँ जोड़ा नहीं गया। आपकी व्यक्तिगत गारंटी नहीं है।",
            "en": " The same lines say the Guru’s spiritual state is then received by the disciple. That result is not a personal guarantee.",
            "gu": " એ જ પંક્તિમાં લખ્યું છે કે ત્યારે ગુરુની આધ્યાત્મિક સ્થિતિ અનાયાસ શિષ્યને પ્રાપ્ત થાય છે. આ તમારી અંગત ખાતરી નથી.",
            "hinglish": " Inhi panktiyon mein likha hai ki tab guru ki adhyatmik sthiti anayas shishya ko prapt ho jati hai. Yeh aapki personal guarantee nahi hai.",
        },
    },
    {
        "need": ["अशांत मत होने दो", "ध्यान करो"],
        "benefit_need": ["शांति"],
        "hi": "ग्रंथ के अनुसार यह करें: भीतर की स्थिति अशांत मत होने दें। ध्यान करें, गुरुमंत्र का जाप करें।",
        "en": "According to these lines: do not let the inner state become restless. Do dhyan, and do gurumantra jaap.",
        "gu": "ગ્રંથ પ્રમાણે આ કરો: અંદરની સ્થિતિ અશાંત ન થવા દો. ધ્યાન કરો, ગુરુમંત્રનો જાપ કરો.",
        "hinglish": "Granth ke anusar aap yeh karo: andar ki sthiti ashant mat hone do. Dhyan karo, gurumantra ka jaap karo.",
        "benefit": {
            "hi": " इन्हीं पंक्तियों में मन को शांति मिलने की बात है। यह चिकित्सा सलाह नहीं है और कोई गारंटी नहीं है।",
            "en": " The same lines speak of peace of mind. This is not medical advice, and it is not a guarantee.",
            "gu": " એ જ પંક્તિમાં મનને શાંતિ મળવાની વાત છે. આ તબીબી સલાહ નથી અને ખાતરી નથી.",
            "hinglish": " Inhi panktiyon mein man ko shanti milne ki baat hai. Yeh medical advice nahi hai, aur koi guarantee nahi hai.",
        },
    },
    {
        "need": ["आज में जियो"],
        "hi": (
            "ग्रंथ के अनुसार यह करें: आज में जियो और आज में रहो। "
            "{extra}"
            "ग्रंथ कहता है, बस यही हाथ में है। यह स्वामीजी का व्यक्तिगत आदेश नहीं है — यही ऊपर की पंक्ति है।"
        ),
        "en": (
            "According to these lines: live in today and remain in today. "
            "{extra}"
            "The granth says that is what is in hand. This is not Swamiji’s personal instruction — it is the line above."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે આ કરો: આજમાં જીવો અને આજમાં રહો. "
            "{extra}"
            "ગ્રંથ કહે છે, બસ એ જ હાથમાં છે. આ સ્વામીજીનો અંગત આદેશ નથી."
        ),
        "hinglish": (
            "Granth ke anusar aap yeh karo: aaj mein jiyo aur aaj mein raho. "
            "{extra}"
            "Granth kehta hai, bas yahi haath mein hai. Yeh Swamiji ka personal order nahi hai — yahi upar ki pankti hai."
        ),
        "extra": {
            "अहंकार": {
                "hi": "‘मैं’ के अहंकार को छोड़ दें। ",
                "en": "Leave the ego of ‘I’. ",
                "gu": "‘હું’ના અહંકારને છોડો. ",
                "hinglish": "‘Main’ ka ahankar chhodo. ",
            },
            "चिंता मत": {
                "hi": "चिंता मत करें — यह भी उसी अंश में है। ",
                "en": "Do not carry worry — that too is in the same passage. ",
                "gu": "ચિંતા ન કરો — એ પણ એ જ અંશમાં છે. ",
                "hinglish": "Chinta mat karo — yeh bhi usi ansh mein hai. ",
            },
        },
    },
    {
        "need": ["पद्धति नहीं", "एक संस्कार"],
        "hi": (
            "ग्रंथ के अनुसार समर्पण ध्यान कोई ध्यान की पद्धति नहीं है। यह एक संस्कार है। "
            "संस्कार के लिए परमात्मा के माध्यम द्वारा परमात्मा को पूर्ण समर्पित होना इन पंक्तियों में है। "
            "कोई अलग विधि या फल यहाँ जोड़ा नहीं गया।"
        ),
        "en": (
            "According to these lines, Samarpan Dhyan is not a method of meditation. It is a sanskar. "
            "The lines say the sanskar is received by surrendering fully to Paramatma through the medium. "
            "No separate method or result has been added."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે સમર્પણ ધ્યાન કોઈ ધ્યાનની પદ્ધતિ નથી. તે એક સંસ્કાર છે. "
            "સંસ્કાર માટે પરમાત્માને માધ્યમ દ્વારા સંપૂર્ણ સમર્પિત થવાની વાત આ પંક્તિઓમાં છે. "
            "અલગ વિધિ અહીં ઉમેરાઈ નથી."
        ),
        "hinglish": (
            "Granth ke anusar samarpan dhyan koi dhyan ki paddhati nahi hai. Yeh ek sanskar hai. "
            "Sanskar ke liye parmatma ke madhyam se parmatma ko poora samarpit hona in panktiyon mein hai. "
            "Koi alag method ya benefit yahan joda nahi gaya."
        ),
    },
    {
        "need": ["साधक", "साधनारत"],
        "hi": (
            "ग्रंथ के अनुसार साधक वह है जो साधनारत है: शरीर पर नियंत्रण साध चुका है, और अब आत्मा की ओर है। "
            "अभ्यास यही दिशा है। यह आपका व्यक्तिगत माप नहीं है।"
        ),
        "en": (
            "According to these lines, a sadhak is one engaged in sadhana: the body has been brought under discipline, and the work has turned toward the atma. "
            "That is the direction of the practice. It is not a personal measure of you."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે સાધક એ છે જે સાધનારત છે: શરીર પર નિયંત્રણ સાધી ચૂક્યો છે, અને હવે આત્મા તરફ છે. "
            "અભ્યાસ એ જ દિશા છે. આ તમારો અંગત માપ નથી."
        ),
        "hinglish": (
            "Granth ke anusar sadhak woh hai jo sadhanarat hai: shareer par niyantran saadh chuka hai, aur ab aatma ki ore hai. "
            "Practice yahi disha hai. Yeh aapka personal measure nahi hai."
        ),
    },
    {
        "need": ["माध्यम है वह गुरुतत्व"],
        "hi": "ग्रंथ के अनुसार परमात्मा की शक्ति ग्रहण करने का माध्यम गुरुतत्व है। व्यावहारिक बात यही है। यह नया उपदेश नहीं है।",
        "en": "According to these lines, gurutattva is the medium through which Paramatma’s shakti is received. That is the practical point. No new teaching has been added.",
        "gu": "ગ્રંથ પ્રમાણે પરમાત્માની શક્તિ ગ્રહણ કરવાનું માધ્યમ ગુરુતત્ત્વ છે. વ્યાવહારિક વાત એ જ છે. આ નવો ઉપદેશ નથી.",
        "hinglish": "Granth ke anusar parmatma ki shakti lene ka madhyam gurutattva hai. Practical baat yahi hai. Yeh naya updesh nahi hai.",
        "extra": {
            "शरीर नहीं": {
                "hi": "गुरु को शरीर न मानें। ",
                "en": "Do not take the Guru as the body. ",
                "gu": "ગુરુને શરીર ન માનો. ",
                "hinglish": "Guru ko shareer mat maano. ",
            },
        },
    },
    {
        "need": ["गुणधर्म है - प्रेम"],
        "hi": (
            "ग्रंथ के अनुसार मनुष्य का गुणधर्म प्रेम करना है। व्यावहारिक बात यही है: प्रेम करना। "
            "कोई अलग फल यहाँ जोड़ा नहीं गया।"
        ),
        "en": (
            "According to these lines, a human being’s quality is to love. The practice is that: to love. "
            "No separate result has been added."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે મનુષ્યનો ગુણધર્મ પ્રેમ કરવાનો છે. વ્યાવહારિક વાત એ જ છે: પ્રેમ કરવો. "
            "અલગ ફળ અહીં ઉમેરાયું નથી."
        ),
        "hinglish": (
            "Granth ke anusar manushya ka gunadharm prem karna hai. Practical baat yahi hai: prem karo. "
            "Koi alag benefit yahan joda nahi gaya."
        ),
    },
    {
        "need": ["अहिंसा", "प्रथम धर्म"],
        "hi": (
            "ग्रंथ के अनुसार अहिंसा मनुष्य का प्रथम धर्म है। व्यावहारिक बात यही है: अहिंसा को प्रथम रखें। "
            "यह व्यक्तिगत आदेश नहीं है।"
        ),
        "en": (
            "According to these lines, ahimsa is a human being’s first dharma. The practice is to keep ahimsa first. "
            "This is not a personal order."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે અહિંસા મનુષ્યનો પ્રથમ ધર્મ છે. વ્યાવહારિક વાત એ જ છે: અહિંસાને પ્રથમ રાખો. "
            "આ અંગત આદેશ નથી."
        ),
        "hinglish": (
            "Granth ke anusar ahimsa manushya ka pratham dharma hai. Practical baat yahi hai: ahimsa ko pratham rakho. "
            "Yeh personal order nahi hai."
        ),
    },
    {
        "need": ["परमात्मा सर्वत्र है", "के अलावा और कुछ है ही नहीं"],
        "hi": (
            "ग्रंथ के अनुसार परमात्मा को कहीं दूर मत खोजें। परमात्मा सर्वत्र है, और इस ब्रह्माण्ड में परमात्मा के अलावा और कुछ है ही नहीं। "
            "देखने की बात यही है। यह आपका निजी संदेश नहीं है।"
        ),
        "en": (
            "According to these lines, do not look for Paramatma somewhere far away. Paramatma is everywhere, and there is nothing in this universe apart from Paramatma. "
            "That is the point of seeing. This is not a private message to you."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે પરમાત્માને ક્યાંક દૂર ન શોધો. પરમાત્મા સર્વત્ર છે, અને આ બ્રહ્માંડમાં પરમાત્મા સિવાય બીજું કશું છે જ નહીં. "
            "જોવાની વાત એ જ છે. આ તમારો અંગત સંદેશ નથી."
        ),
        "hinglish": (
            "Granth ke anusar parmatma ko kahin door mat dhoondo. Parmatma sarvatra hai, aur is brahmand mein parmatma ke alawa aur kuch hai hi nahi. "
            "Dekhne ki baat yahi hai. Yeh aapka private message nahi hai."
        ),
    },
    {
        "need": ["देव तत्त्व", "दानव तत्त्व", "मनुष्य तत्त्व"],
        "hi": (
            "ग्रंथ के अनुसार किसी को संपूर्ण अच्छा या संपूर्ण बुरा मत मानें। देव तत्त्व और दानव तत्त्व के बीच मनुष्य तत्त्व है, कम या ज्यादा अनुपात में। "
            "समझ यही है। यह आप पर थोपा हुआ निर्णय नहीं है।"
        ),
        "en": (
            "According to these lines, do not take any person as wholly good or wholly bad. Manushya tattva lies between dev tattva and danav tattva, in a lesser or greater proportion. "
            "That is the understanding. It is not a judgment imposed on you."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે કોઈને સંપૂર્ણ સારો કે સંપૂર્ણ ખરાબ ન માનો. દેવ તત્ત્વ અને દાનવ તત્ત્વની વચ્ચે મનુષ્ય તત્ત્વ છે. "
            "સમજ એ જ છે. આ તમારા પર થોપેલો નિર્ણય નથી."
        ),
        "hinglish": (
            "Granth ke anusar kisi ko sampurna accha ya sampurna bura mat maano. Dev tattva aur danav tattva ke beech manushya tattva hai, kam ya zyada. "
            "Samajh yahi hai. Yeh aap par thopa hua faisla nahi hai."
        ),
    },
    {
        "need": ["समाधि", "होती है"],
        "hi": (
            "ग्रंथ के अनुसार सदगुरु की शक्तियों का स्थाई निवास उनकी समाधि है। वहाँ चित्त से भी जाया जा सकता है — यही इन पंक्तियों में है। "
            "कोई और विधि यहाँ जोड़ी नहीं गई।"
        ),
        "en": (
            "According to these lines, the Sadguru’s samadhi is the lasting dwelling of those powers. One can go there with the chitta — that is what these lines say. "
            "No other method has been added."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે સદ્ગુરુની શક્તિઓનું સ્થાયી નિવાસ તેમની સમાધિ છે. ત્યાં ચિત્તથી પણ જઈ શકાય છે — એ જ આ પંક્તિઓમાં છે. "
            "બીજી વિધિ અહીં ઉમેરાઈ નથી."
        ),
        "hinglish": (
            "Granth ke anusar sadguru ki shaktiyon ka sthayi nivas unki samadhi hai. Wahan chitta se bhi jaya ja sakta hai — yahi in panktiyon mein hai. "
            "Koi aur method yahan jodi nahi gayi."
        ),
    },
    {
        "need": ["समर्पण ध्यान का मिशन"],
        "hi": (
            "ग्रंथ के अनुसार समर्पण ध्यान का मिशन उन मनुष्यों का निर्माण है जिन्होंने जीवन को ‘वो’ पर छोड़ दिया है। "
            "दिशा यही है। यह आप पर थोपा हुआ लक्ष्य नहीं है।"
        ),
        "en": (
            "According to these lines, the mission of Samarpan Dhyan is to form people who have left their life upon ‘That’. "
            "That is the direction. It is not a goal imposed on you."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે સમર્પણ ધ્યાનનું મિશન એ મનુષ્યોનું નિર્માણ છે જેમણે જીવન ‘તે’ પર છોડી દીધું છે. "
            "દિશા એ જ છે. આ તમારા પર થોપેલું લક્ષ્ય નથી."
        ),
        "hinglish": (
            "Granth ke anusar samarpan dhyan ka mission un logon ka nirmaan hai jinhone jeevan ‘Woh’ par chhod diya hai. "
            "Disha yahi hai. Yeh aap par thopa hua target nahi hai."
        ),
    },
    {
        "need": ["सौंप देना समर्पण है"],
        "hi": (
            "ग्रंथ के अनुसार समर्पण यह है: अपने जीवन का नियंत्रण संपूर्णतः सदगुरु के माध्यम से परमात्मा को सौंप देना। "
            "करने की बात यही है। कोई अलग फल यहाँ जोड़ा नहीं गया।"
        ),
        "en": (
            "According to these lines, surrender is this: hand the whole control of one’s life to Paramatma through the Sadguru. "
            "That is the practice. No separate result has been added."
        ),
        "gu": (
            "ગ્રંથ પ્રમાણે સમર્પણ એ છે: જીવનનું સંપૂર્ણ નિયંત્રણ સદ્ગુરુના માધ્યમથી પરમાત્માને સોંપી દેવું. "
            "કરવાની વાત એ જ છે. અલગ ફળ અહીં ઉમેરાયું નથી."
        ),
        "hinglish": (
            "Granth ke anusar samarpan yeh hai: apne jeevan ka niyantran sampurnatah sadguru ke madhyam se parmatma ko saump dena. "
            "Karne ki baat yahi hai. Koi alag benefit yahan joda nahi gaya."
        ),
    },
]


def _fill(lang: str, item: dict, text: str) -> str:
    body = item[lang]
    extra_map = item.get("extra") or {}
    extra = ""
    for needle, copies in extra_map.items():
        if needle in text:
            extra += copies.get(lang) or copies.get("hi") or ""
    if "{extra}" in body:
        body = body.replace("{extra}", extra)
    elif extra:
        body = extra + body
    benefit_need = item.get("benefit_need") or []
    benefit = (item.get("benefit") or {}).get(lang)
    if benefit and all(part in text for part in benefit_need):
        body = body.rstrip() + benefit
    if lang == "en" and "not " not in body.lower():
        body += " This is not a personal guarantee."
    elif lang == "gu" and "નથી" not in body:
        body += " આ અંગત ખાતરી નથી."
    elif lang == "hi" and "नहीं" not in body:
        body += " यह व्यक्तिगत गारंटी नहीं है।"
    elif lang == "hinglish" and "nahi" not in body.lower() and "नहीं" not in body:
        body += " Yeh personal guarantee nahi hai."
    return body


def granth_practice(lang: str, text: str) -> str | None:
    blob = text or ""
    lang = lang if lang in {"hi", "en", "gu", "hinglish"} else "hi"
    for item in PRACTICES:
        if all(part in blob for part in item["need"]):
            return _fill(lang, item, blob)
    return None
