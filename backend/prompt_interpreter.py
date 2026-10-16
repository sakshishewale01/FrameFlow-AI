"""
Universal Multilingual Prompt-to-Animation Semantic Engine.
Interprets arbitrary user prompts in English, Hindi (हिंदी), and Marathi (मराठी)
to extract subjects, visual environment, action choreography, camera dynamics,
and multi-scene narrative progression.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple


# Color palettes by keyword (English, Hindi, and Marathi)
COLOR_KEYWORDS: Dict[str, Tuple[int, int, int]] = {
    # English
    "red": (239, 68, 68),
    "crimson": (220, 38, 38),
    "scarlet": (225, 29, 72),
    "blue": (59, 130, 246),
    "azure": (14, 165, 233),
    "cyan": (6, 182, 212),
    "teal": (20, 184, 166),
    "green": (34, 197, 94),
    "emerald": (16, 185, 129),
    "yellow": (234, 179, 8),
    "gold": (245, 158, 11),
    "amber": (217, 119, 6),
    "orange": (249, 115, 22),
    "purple": (168, 85, 247),
    "violet": (139, 92, 246),
    "indigo": (99, 102, 241),
    "pink": (244, 114, 182),
    "magenta": (217, 70, 239),
    "rose": (244, 63, 94),
    "white": (248, 250, 252),
    "silver": (203, 213, 225),
    "gray": (148, 163, 184),
    "grey": (148, 163, 184),
    "black": (30, 41, 59),
    "dark": (15, 23, 42),
    "neon": (56, 189, 248),
    # Hindi / Marathi in Devanagari and Latin
    "गुलाबी": (244, 114, 182),
    "gulabi": (244, 114, 182),
    "लाल": (239, 68, 68),
    "laal": (239, 68, 68),
    "नीला": (59, 130, 246),
    "निळा": (59, 130, 246),
    "neela": (59, 130, 246),
    "nila": (59, 130, 246),
    "हरा": (34, 197, 94),
    "हिरवा": (34, 197, 94),
    "hara": (34, 197, 94),
    "hirva": (34, 197, 94),
    "पीला": (234, 179, 8),
    "पिवळा": (234, 179, 8),
    "peela": (234, 179, 8),
    "pivla": (234, 179, 8),
    "सफेद": (248, 250, 252),
    "पांढरा": (248, 250, 252),
    "safed": (248, 250, 252),
    "pandhra": (248, 250, 252),
    "काला": (30, 41, 59),
    "काळा": (30, 41, 59),
    "kala": (30, 41, 59),
    "सोनेरी": (245, 158, 11),
    "सुनहरा": (245, 158, 11),
    "soneri": (245, 158, 11),
    "sunehra": (245, 158, 11),
}

# Environment definitions with English, Hindi, and Marathi trigger keywords
ENVIRONMENTS = {
    "pond": {
        "keywords": [
            "pond", "lake", "water lily", "lotus pond", "water",
            "तलाव", "तालाब", "पोखर", "सरोवर", "कमल तलाव", "पाणी", "पानी", "talav", "talab",
        ],
        "bg_top": (10, 35, 50),
        "bg_bottom": (18, 70, 75),
        "horizon": (28, 115, 105),
        "particles": "bubbles",
        "ground_type": "water",
    },
    "village": {
        "keywords": [
            "village", "rural", "countryside", "cottage", "field", "farm", "well",
            "गाव", "गावातल्या", "गावात", "गांव", "देहात", "खेडेगाव", "गावकरी", "gaav", "gaon", "khedegaon",
        ],
        "bg_top": (30, 60, 110),
        "bg_bottom": (80, 140, 160),
        "horizon": (140, 185, 120),
        "particles": "fireflies",
        "ground_type": "grass",
    },
    "nature": {
        "keywords": [
            "forest", "trees", "mountain", "jungle", "meadow", "garden", "wild", "valley", "green", "woods",
            "जंगल", "वन", "रान", "अरण्य", "झाड", "झाडे", "पेड़", "पहाड़", "डोंगर", "jungle", "jangle", "ran",
        ],
        "bg_top": (12, 35, 45),
        "bg_bottom": (24, 65, 55),
        "horizon": (40, 95, 70),
        "particles": "fireflies",
        "ground_type": "grass",
    },
    "space": {
        "keywords": [
            "space", "galaxy", "orbit", "cosmos", "stars", "nebula", "planet", "asteroid", "alien", "mars", "moon",
            "अंतरिक्ष", "ब्रह्मांड", "तारे", "ग्रह", "चाँद", "चंद्र", "antariksh", "brahmand",
        ],
        "bg_top": (5, 8, 24),
        "bg_bottom": (16, 24, 56),
        "horizon": (30, 41, 89),
        "particles": "stars",
        "ground_type": "surface",
    },
    "ocean": {
        "keywords": [
            "ocean", "sea", "underwater", "water", "marine", "reef", "depths", "waves", "subsea", "trench", "abyss",
            "समुद्र", "सागर", "अथांग", "लाटा", "samudra", "sagar",
        ],
        "bg_top": (4, 25, 55),
        "bg_bottom": (8, 48, 92),
        "horizon": (14, 80, 130),
        "particles": "bubbles",
        "ground_type": "seabed",
    },
    "cyberpunk": {
        "keywords": [
            "cyber", "neon", "city", "future", "futuristic", "highway", "metropolis", "robot", "tech", "matrix",
            "शहर", "रस्ता", "सड़क", "shahur", "shahar",
        ],
        "bg_top": (15, 10, 32),
        "bg_bottom": (35, 18, 65),
        "horizon": (65, 24, 105),
        "particles": "rain",
        "ground_type": "road",
    },
    "sky": {
        "keywords": [
            "sky", "clouds", "flying", "sunset", "soar", "horizon", "atmosphere", "aerial", "flight",
            "आसमान", "आकाश", "नभ", "ढग", "बादल", "aakash", "aasmaan",
        ],
        "bg_top": (25, 45, 95),
        "bg_bottom": (180, 85, 90),
        "horizon": (245, 158, 60),
        "particles": "dust",
        "ground_type": "clouds",
    },
    "desert": {
        "keywords": [
            "desert", "dune", "sand", "canyon", "pyramid", "sahara", "arid",
            "रेगिस्तान", "वाळवंट", "वाळू", "रेत", "registan", "valvant",
        ],
        "bg_top": (45, 25, 20),
        "bg_bottom": (120, 65, 35),
        "horizon": (210, 130, 60),
        "particles": "dust",
        "ground_type": "sand",
    },
    "snow": {
        "keywords": [
            "snow", "ice", "arctic", "glacier", "frozen", "winter", "cold", "blizzard",
            "बर्फ", "हिम", "थंडी", "barf", "him",
        ],
        "bg_top": (20, 30, 50),
        "bg_bottom": (70, 95, 130),
        "horizon": (180, 205, 230),
        "particles": "snow",
        "ground_type": "ice",
    },
    "magical": {
        "keywords": [
            "magic", "mystical", "fantasy", "enchanted", "fairy", "crystal", "sparkle", "dream", "glowing",
            "जादुई", "जादू", "चमत्कार", "स्वप्न", "सुंदर", "मोहिनी", "jaadu", "jadui", "chamatkar",
        ],
        "bg_top": (20, 10, 40),
        "bg_bottom": (50, 20, 80),
        "horizon": (95, 40, 135),
        "particles": "embers",
        "ground_type": "ethereal",
    },
}

# Multilingual Entity classification specifications
ENTITY_SPECS = [
    {
        "category": "nature_object",
        "subtype": "lotus",
        "keywords": ["lotus", "flower", "water lily", "कमल", "कमळ", "फूल", "blossom", "lily", "kamal"],
        "default_palette": ((244, 114, 182), (251, 207, 232), (250, 204, 21)),
        "names": {"en": "Lotus Flower", "hi": "गुलाबी कमल", "mr": "गुलाबी कमळ"},
    },
    {
        "category": "animal",
        "subtype": "elephant",
        "keywords": ["elephant", "हाथी", "हत्ती", "हत्तीने", "गज", "hathi", "haathi", "hatti"],
        "default_palette": ((148, 163, 184), (244, 114, 182), (255, 255, 255)),
        "names": {"en": "Little Elephant", "hi": "छोटा हाथी", "mr": "छोटा हत्ती"},
    },
    {
        "category": "animal",
        "subtype": "cat",
        "keywords": ["cat", "kitten", "kitty", "मांजर", "मांजरी", "मांजरीने", "मांजरा", "बिल्ली", "बिल्लियां", "manjar", "billi"],
        "default_palette": ((249, 115, 22), (254, 215, 170), (239, 68, 68)),
        "names": {"en": "Playful Cat", "hi": "प्यारी बिल्ली", "mr": "खोडकर मांजर"},
    },
    {
        "category": "animal",
        "subtype": "dinosaur",
        "keywords": ["dinosaur", "trex", "dino", "डायनासोर", "डायनासोअर"],
        "default_palette": ((34, 197, 94), (187, 247, 208), (245, 158, 11)),
        "names": {"en": "Baby Dinosaur", "hi": "नन्हा डायनासोर", "mr": "छोटा डायनासोअर"},
    },
    {
        "category": "humanoid",
        "subtype": "boy",
        "keywords": [
            "boy", "student", "son", "मुलगा", "मुलाने", "मुलाला", "लड़का", "लड़के", "पोरा", "बालक", "mulga", "ladka",
            "गरीब मुलगा", "गरीब लड़का", "मेहनत",
        ],
        "default_palette": ((59, 130, 246), (251, 191, 36), (239, 68, 68)),
        "names": {"en": "Determined Boy", "hi": "मेहनती लड़का", "mr": "कष्टाळू मुलगा"},
    },
    {
        "category": "humanoid",
        "subtype": "girl",
        "keywords": [
            "girl", "daughter", "मुलगी", "मुली", "मुलीने", "मुलीला", "लड़की", "लड़कियों", "कन्या", "हुशार मुलगी", "हुशार मुलीने", "mulgi", "ladki",
        ],
        "default_palette": ((236, 72, 153), (254, 205, 211), (56, 189, 248)),
        "names": {"en": "Clever Girl", "hi": "हुशार लड़की", "mr": "हुशार मुलगी"},
    },
    {
        "category": "vehicle",
        "subtype": "rocket",
        "keywords": ["rocket", "spaceship", "shuttle", "रॉकेट", "अंतरिक्ष यान", "विमान"],
        "default_palette": ((59, 130, 246), (239, 68, 68), (250, 204, 21)),
        "names": {"en": "Starship Rocket", "hi": "अंतरिक्ष रॉकेट", "mr": "अंतराळ रॉकेट"},
    },
    {
        "category": "vehicle",
        "subtype": "car",
        "keywords": ["car", "sports car", "automobile", "कार", "गाड़ी", "गाडी"],
        "default_palette": ((220, 38, 38), (15, 23, 42), (250, 204, 21)),
        "names": {"en": "Super Car", "hi": "सुपर कार", "mr": "वेगवान कार"},
    },
    {
        "category": "vehicle",
        "subtype": "submarine",
        "keywords": ["submarine", "sub", "पनडुब्बी"],
        "default_palette": ((20, 184, 166), (15, 23, 42), (250, 204, 21)),
        "names": {"en": "Submarine", "hi": "पनडुब्बी", "mr": "पाणबुडी"},
    },
    {
        "category": "animal",
        "subtype": "bird",
        "keywords": ["bird", "eagle", "hawk", "चिड़िया", "पक्षी", "गरुड़", "पाखरू"],
        "default_palette": ((245, 158, 11), (180, 83, 9), (255, 255, 255)),
        "names": {"en": "Majestic Bird", "hi": "उड़ता पक्षी", "mr": "उडणारा पक्षी"},
    },
    {
        "category": "animal",
        "subtype": "fish",
        "keywords": ["dolphin", "whale", "fish", "shark", "मछली", "मासा"],
        "default_palette": ((14, 165, 233), (251, 146, 60), (255, 255, 255)),
        "names": {"en": "Marine Creature", "hi": "समुद्री जीव", "mr": "सागरी जीव"},
    },
    {
        "category": "animal",
        "subtype": "dragon",
        "keywords": ["dragon", "ड्रैगन"],
        "default_palette": ((168, 85, 247), (239, 68, 68), (250, 204, 21)),
        "names": {"en": "Mythic Dragon", "hi": "जादुई ड्रैगन", "mr": "जादुई ड्रॅगन"},
    },
    {
        "category": "humanoid",
        "subtype": "astronaut",
        "keywords": ["astronaut", "cosmonaut", "robot", "cyborg", "रोबोट"],
        "default_palette": ((248, 250, 252), (59, 130, 246), (250, 204, 21)),
        "names": {"en": "Explorer", "hi": "अंतरिक्ष यात्री", "mr": "अंतराळवीर"},
    },
    {
        "category": "celestial",
        "subtype": "star",
        "keywords": ["star", "sun", "comet", "तारा", "सूर्य", "चांदणी"],
        "default_palette": ((250, 204, 21), (245, 158, 11), (255, 255, 255)),
        "names": {"en": "Radiant Star", "hi": "चमकता सितारा", "mr": "चमकणारा तारा"},
    },
]


def detect_language(prompt: str, user_selected: Optional[str] = None) -> str:
    """Detect whether prompt or intent is Marathi ('mr'), Hindi ('hi'), or English ('en')."""
    if user_selected in ["mr", "hi", "en"]:
        return user_selected

    p = prompt.lower()
    # Distinctive Marathi indicators
    marathi_markers = [
        "एका", "छोट्या", "मांजरीने", "गावातल्या", "सगळ्यांना", "हसवलं",
        "मुलगा", "मुलगी", "हुशार", "पाण्याच्या", "समस्येतून", "वाचवलं",
        "करून", "मोठं", "मिळवतो", "तळ्यात", "तलाव", "झाडं", "आहेत",
        "केलं", "झाली", "झाला", "कष्टाने", "जिद्दीने",
    ]
    if any(m in prompt for m in marathi_markers):
        return "mr"

    # Devanagari Hindi indicators
    hindi_markers = [
        "छोटा", "हाथी", "जंगल", "ढूँढता", "दोस्त", "खोया", "लड़का",
        "लड़की", "मेहनत", "सफलता", "पानी", "तालाब", "कमल", "नाचता",
        "करता", "करती", "है", "हैं", "था", "थी", "में", "से", "को",
    ]
    if any(m in prompt for m in hindi_markers):
        return "hi"

    # Check Devanagari Unicode range (0x0900 to 0x097F)
    has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in prompt)
    if has_devanagari:
        # Default Devanagari fallback to Hindi if no distinct Marathi word
        return "hi"

    return "en"


def extract_colors_from_prompt(
    prompt: str, default_palette: Optional[Tuple[Tuple[int, int, int], ...]] = None
) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    """Extract primary, secondary, and accent colors from descriptive keywords."""
    p = prompt.lower()
    found_colors: List[Tuple[int, int, int]] = []

    for word, col in COLOR_KEYWORDS.items():
        if word in p:
            if col not in found_colors:
                found_colors.append(col)

    defaults = default_palette or (
        (59, 130, 246),   # Electric blue
        (236, 72, 153),   # Vibrant magenta
        (250, 204, 21),   # Golden amber
    )

    while len(found_colors) < 3:
        found_colors.append(defaults[len(found_colors) % len(defaults)])

    return found_colors[0], found_colors[1], found_colors[2]


def detect_environment(prompt: str) -> Dict[str, Any]:
    """Determine the optimal environmental setting and lighting based on prompt."""
    p = prompt.lower()
    best_env = "space"
    best_score = 0

    for env_name, env_data in ENVIRONMENTS.items():
        score = sum(1 for kw in env_data["keywords"] if kw in p)
        if score > best_score:
            best_score = score
            best_env = env_name

    if best_score == 0:
        if any(w in p for w in ["कमल", "कमळ", "lotus", "pond", "तलाव", "taalab", "lake", "water"]):
            best_env = "pond"
        elif any(w in p for w in ["गाव", "गांव", "village", "कष्ट", "मुलगा", "मुलगी"]):
            best_env = "village"
        elif any(w in p for w in ["जंगल", "forest", "हाथी", "हत्ती", "रान", "jungle"]):
            best_env = "nature"
        elif any(w in p for w in ["drive", "speed", "road", "street", "car", "गाडी", "गाड़ी"]):
            best_env = "cyberpunk"
        elif any(w in p for w in ["fly", "soar", "high", "glide", "bird", "पक्षी"]):
            best_env = "sky"
        elif any(w in p for w in ["swim", "float", "deep", "fish", "मासा"]):
            best_env = "ocean"
        else:
            best_env = "magical"

    cfg = ENVIRONMENTS[best_env].copy()
    cfg["name"] = best_env
    return cfg


def detect_entity(prompt: str, language: Optional[str] = None) -> Dict[str, Any]:
    """Detect subject entity category, subtype, translated name, and descriptive properties."""
    p = prompt.lower()
    lang = detect_language(prompt, language)

    detected_spec = None
    best_score = 0

    for spec in ENTITY_SPECS:
        score = sum(1 for kw in spec["keywords"] if kw in p)
        if score > best_score:
            best_score = score
            detected_spec = spec

    if not detected_spec:
        detected_spec = {
            "category": "humanoid",
            "subtype": "character",
            "default_palette": ((59, 130, 246), (236, 72, 153), (250, 204, 21)),
            "names": {"en": "Hero", "hi": "नायक", "mr": "नायक"},
        }

    c_pri, c_sec, c_acc = extract_colors_from_prompt(prompt, detected_spec.get("default_palette"))
    name_display = detected_spec["names"].get(lang, detected_spec["names"]["en"])

    return {
        "category": detected_spec["category"],
        "subtype": detected_spec["subtype"],
        "display_name": name_display,
        "language": lang,
        "primary_color": c_pri,
        "secondary_color": c_sec,
        "accent_color": c_acc,
        "glowing": any(w in p for w in ["glow", "radiant", "neon", "shining", "crystal", "magic", "चमक", "जादुई", "प्रकाश"]),
    }


def compute_scenes_for_duration(
    prompt: str,
    style: str,
    duration: int,
    language: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Universally partitions arbitrary user requests from 5s to 300s
    into sequential cinematic acts and scenes in Hindi, Marathi, or English.
    """
    duration = max(5, min(300, duration))
    lang = detect_language(prompt, language)

    # Calculate optimal scene count
    if duration <= 15:
        scene_count = 3
    elif duration <= 30:
        scene_count = 4
    elif duration <= 60:
        scene_count = 5
    elif duration <= 120:
        scene_count = 7
    elif duration <= 180:
        scene_count = 10
    else:
        scene_count = min(16, duration // 18)

    base_dur = duration // scene_count
    remainder = duration % scene_count

    entity = detect_entity(prompt, lang)
    env = detect_environment(prompt)

    sub_name = entity["display_name"]
    subtype = entity["subtype"]

    # Cinematic Motion types available in procedural engine
    motion_types = [
        "hover_and_sway",
        "horizontal_travel",
        "dynamic_bounce",
        "vertical_climb_or_launch",
        "pirouette_spin",
        "accelerate_zoom",
        "grand_parade",
    ]

    camera_motions = [
        "zoom_in",
        "tracking_shot",
        "crane_up",
        "pan_right",
        "dynamic_orbit",
        "dramatic_zoom_out",
        "pan_left",
    ]

    # Generate language-specific narrative arcs
    beats = []
    if lang == "mr":
        # Marathi narrative arcs
        if subtype == "lotus":
            beats = [
                ("जादुई तळ्यात कमळाचा उदय", "शांत आणि निर्मळ पाण्याच्या तळ्यात एक सुंदर गुलाबी कमळ हळूच डोलू लागतं.", "शांत पाण्याच्या सोनेरी प्रकाशात गुलाबी कमळाचा प्रवास सुरू होतो."),
                ("पाण्यावर तालबद्ध नृत्य", "हळुवार वाऱ्याच्या लहरींवर कमळाच्या पाकळ्या तालात नाचू लागतात.", "वाऱ्याच्या मंद झुळुकीवर कमळ आनंदाने डोलत आहे."),
                ("कमळाचा मोहक फुलोरा", "सूर्याच्या कोवळ्या किरणांनी कमळाचे तेज अधिकच खुलून दिसते.", "सभोवतालचे पाणी कमळाच्या सौंदर्याने उजळून निघते."),
                ("सगळ्यांना मोहित करणारा आनंद", "तळ्यातील मासे आणि पाखरं कमळाचे नृत्य पाहून मंत्रमुग्ध होतात.", "प्रत्येक क्षणात एक नवीन चैतन्य आणि गोडवा भरलेला आहे."),
                ("सोनियाचा क्षण", "संध्याकाळच्या सोनेरी प्रकाशात कमळ शांतपणे सर्वांना आल्हाददायक सुख देऊन विसावते.", "अशा रीतीने या जादुई कमळाने संपूर्ण तळ्याला सुगंधी आनंदाने भरून टाकले."),
            ]
        elif subtype == "elephant":
            beats = [
                ("मित्राचा शोध सुरू", "हिरव्यागार घनदाट जंगलात एक छोटा हत्ती आपल्या हरवलेल्या मित्राला शोधायला निघतो.", "सुंदर जंगलात आपला लाडका छोटा हत्ती मित्राच्या शोधात पावले टाकतो."),
                ("जंगलाच्या पाऊलवाटेवर", "मोठे कान हलवत आणि सोंड उंचावत तो मित्राला हाक मारतो.", "प्रत्येक झाडामागे आणि झुडुपांजवळ तो उत्सुकतेने मित्राचा शोध घेतो."),
                ("नदीकाठचा सुगावा", "झुळझुळ वाहणाऱ्या नदीकाठी त्याला मित्राच्या पावलांचे ठसे दिसतात.", "नदीच्या थंडगार पाण्यात त्याला आपल्या मित्राचा सुगावा मिळतो."),
                ("आनंदाचा क्षण", "दोन्ही मित्रांची नजरानजर होते आणि जंगलात आनंदाचे वातावरण पसरते.", "आपल्या मित्राला सुखरूप पाहून छोट्या हत्तीचा आनंद गगनात मावेनासा होतो."),
                ("मैत्रीचा विजय", "दोन्ही मित्र एकत्र येऊन आनंदाने सोंड उंचावून नाचू लागतात.", "अशा प्रकारे जंगलात दोघा मित्रांची अतूट मैत्री पुन्हा एकदा जिंकली!"),
            ]
        elif subtype == "cat":
            beats = [
                ("खोडकर मांजरीची गावात एन्ट्री", "आपल्या गोड गावात एक चंचल मांजर आनंदाने उड्या मारत प्रवेश करते.", "सकाळच्या कोवळ्या उन्हात मांजरीची पावले गावात पडतात."),
                ("मजेदार खोड्या", "ती घरांच्या छतावरून आणि अंगणातून पळत सगळ्यांचे लक्ष वेधून घेते.", "तिच्या प्रत्येक हालचालीत एक गोड खोडकरपणा आणि चपळता दिसते."),
                ("गावकऱ्यांचे हास्य", "तिची मजेदार उडी आणि खेळ पाहून लहान-मोठे सगळे खळाळून हसतात.", "गावातल्या प्रत्येकाच्या चेहऱ्यावर गोड हास्य उमटले आहे."),
                ("आनंदाचा खेळ", "गावातली मुले तिच्या मागे आनंदाने धावतात आणि खेळ सुरू होतो.", "सगळ्या गावाचे वातावरण हसऱ्या आणि आनंदी क्षणांनी भरून गेले."),
                ("गावाची लाडकी मांजर", "आपल्या प्रेमाने आणि चंचलपणाने मांजरीने संपूर्ण गावाचे मन जिंकून घेतले.", "अशी ही खोडकर मांजर आता संपूर्ण गावाची सर्वात लाडकी झाली आहे!"),
            ]
        elif subtype == "dinosaur":
            beats = [
                ("डान्सर बनण्याचे स्वप्न", "एक लहान गोंडस डायनासोअर जगातील सर्वात मोठा डान्सर बनण्याचे स्वप्न पाहतो.", "आपल्या मनात नृत्याची आवड जपणारा छोटा डायनासोअर तालात पावले टाकतो."),
                ("सराव आणि ताल", "तो मजेदार पद्धतीने शेपूट हलवत आणि उड्या मारत नृत्याचा सराव करतो.", "प्रत्येक बीटवर त्याचे शरीर तालात थिरकायला लागते."),
                ("जंगलात डान्स स्टेज", "जंगलातील सर्व प्राणी त्याचा उत्साहवर्धक डान्स पाहण्यासाठी गोळा होतात.", "त्याच्या नृत्यातील ऊर्जा पाहून सगळे अवाक होतात."),
                ("अप्रतिम नृत्याविष्कार", "त्याने एकामागून एक अफलातून स्टेप्स करून सर्वांना चकित केले.", "त्याच्या अद्भूत डान्सने संपूर्ण वातावरण थरारून निघाले."),
                ("जंगलाचा सुपरस्टार", "टाळ्यांच्या कडकडाटात छोटा डायनासोअर आजचा सर्वात मोठा डान्स स्टार बनला!", "कष्टाने आणि जिद्दीने त्याने आपले स्वप्न पूर्ण करून दाखवले!"),
            ]
        elif subtype == "boy":
            beats = [
                ("मोठ्या स्वप्नाची सुरुवात", "एका गरीब कुटुंबातील कष्टाळू मुलगा मोठे ध्येय डोळ्यांसमोर ठेवून कामाला लागतो.", "अनेक अडचणी असल्या तरी त्याच्या डोळ्यात जिद्दीची चमक आहे."),
                ("अखंड परिश्रम", "दिवस असो वा रात्र, तो न थकता प्रामाणिकपणे अभ्यास आणि मेहनत करतो.", "कठीण परिस्थितीतही त्याचा आत्मविश्वास तसूभरही डगमगला नाही."),
                ("संकटांवर मात", "प्रत्येक अडथळा त्याने आपल्या हुशारीने आणि धैर्याने पार केला.", "त्याच्या अथक प्रयत्नांना यश मिळण्याची दिशा दिसू लागली."),
                ("यशाची मोठी झेप", "त्याच्या बुद्धिमत्तेने आणि कष्टाने त्याला सर्वात मोठे यश मिळवून दिले.", "त्याच्या यशाची बातमी संपूर्ण गावात अभिमानाने पसरली."),
                ("गावाचा अभिमान", "गरीबीवर मात करून यशाच्या शिखरावर पोहोचलेल्या या मुलाने नवा इतिहास घडवला!", "कष्टाला कल्पकतेची जोड दिली की काहीही शक्य होते, हेच त्याने सिद्ध केले!"),
            ]
        elif subtype == "girl":
            beats = [
                ("गावातील पाण्याचा प्रश्न", "गावातल्या भीषण पाणीटंचाईवर तोडगा काढण्यासाठी हुशार मुलीने निश्चय केला.", "गावातील महिलांचे कष्ट पाहून तिने मदतीचा निर्धार केला."),
                ("अभिनव उपाय", "तिने वैज्ञानिक विचार करून पावसाचे पाणी साठवण्याची सोपी योजना आखली.", "गावातील लोकांना एकत्र आणून तिने बंधारे बांधण्याची कल्पना मांडली."),
                ("गावकऱ्यांची साथ", "तिच्या आवाहनाला प्रतिसाद देऊन अवघे गाव एकजुटीने कामाला लागले.", "मुलीच्या नेतृत्वाखाली श्रमदानातून पाण्याचे मार्ग मोकळे झाले."),
                ("पाण्याचे तुडुंब साठे", "पहिल्याच पावसात गावातील विहिरी आणि तलाव पाण्याने तुडुंब भरले.", "दुष्काळाचे संकट दूर झाले आणि गावकऱ्यांच्या चेहऱ्यावर समाधान दिसले."),
                ("पाणीदार गावाचा गौरव", "आपल्या बुद्धिमत्तेने गावाला नवसंजीवनी देणाऱ्या या कन्येचा सर्वांनी जयजयकार केला!", "हुशारी आणि एकजूट असेल तर अशक्यही शक्य होते!"),
            ]
        else:
            beats = [
                (f"{sub_name} चे आगमन", f"{sub_name} एका नव्या उत्साहाने आपल्या प्रवासाची सुरुवात करतो.", f"{sub_name} च्या रूपाने एका अद्भुत प्रवासाची सुरुवात झाली आहे."),
                (f"{sub_name} चा वेगवान प्रवास", f"{sub_name} सभोवतालच्या निसर्गातून वेगाने पुढे सरकतो.", f"प्रत्येक पावलावर नवा उत्साह आणि चैतन्य अनुभवायला मिळते."),
                (f"{sub_name} ची मोठी भरारी", f"{sub_name} नवीन उंची गाठत आपल्या ध्येयाकडे वाटचाल करतो.", f"आकाशाला गवसणी घालणारा हा अनोखा क्षण आहे."),
                (f"{sub_name} ची किमया", f"{sub_name} आपल्या अद्भुत हालचालींनी सर्वांना चकित करतो.", f"वातावरणातील प्रत्येक घटक त्याच्या तालावर डोलू लागतो."),
                (f"{sub_name} चा गौरव", f"{sub_name} आपल्या प्रवासाच्या अंतिम टप्प्यात यशाची पताका फडकवतो.", f"अशा प्रकारे हा अविस्मरणीय प्रवास एका देखण्या समाप्तीकडे पोहोचतो."),
            ]

    elif lang == "hi":
        # Hindi narrative arcs
        if subtype == "lotus":
            beats = [
                ("जादुई तालाब पर कमल", "शांत और निर्मल पानी के बीच एक सुंदर गुलाबी कमल हौले-हौले खिलता है।", "जादुई तालाब की गोद में नन्हे कमल की सुबह मुस्कुराती है।"),
                ("लहरों पर थिरकता नृत्य", "हवा के हल्के झोंकों के साथ कमल की पंखुड़ियां खुशी से झूम उठती हैं।", "पानी की मंद तरंगों पर कमल ताल से ताल मिला रहा है।"),
                ("स्वर्णिम धूप का उजाला", "सूरज की किरणें कमल पर पड़ते ही पूरा तालाब चमक उठता है।", "गुलाबी रंग की आभा से सारा वातावरण मनमोहक हो गया है।"),
                ("प्रकृति का सुंदर संगीत", "तितलियाँ और भौंरे कमल के चारों ओर खुशी से मँडराने लगते हैं।", "तालाब का हर कोना इस नृत्य से आनंदित हो उठा है।"),
                ("अविस्मरणीय सौंदर्य", "शाम ढलते ही कमल शांति और सुकून का सुंदर संदेश देकर विदा लेता है।", "इस तरह गुलाबी कमल ने सबको अपनी खूबसूरती से मंत्रमुग्ध कर दिया।"),
            ]
        elif subtype == "elephant":
            beats = [
                ("दोस्त की तलाश", "घने और हरे-भरे जंगल में एक छोटा हाथी अपने खोए हुए दोस्त को ढूँढने निकलता है।", "नन्हा हाथी जंगल के रास्ते पर अपने प्यारे दोस्त की खोज में आगे बढ़ता है।"),
                ("जंगल की पगडंडियाँ", "कान फड़फड़ाते और सूंड़ हिलाते हुए वह दोस्त को पुकारता है।", "वह हर पेड़ और झाड़ी के पास जाकर दोस्त के कदमों के निशान देखता है।"),
                ("नदी किनारे उम्मीद", "बहती नदी के किनारे उसे अपने दोस्त के ताजा पैरों के निशान मिलते हैं।", "दोस्त की आहट पाकर नन्हे हाथी का दिल खुशी से भर जाता है।"),
                ("खुशियों का मिलन", "झाड़ियों के पीछे से दोस्त बाहर आता है और दोनों एक-दूसरे को गले लगाते हैं।", "दोनों दोस्तों की आँखों में खुशी के आँसू छलक आते हैं।"),
                ("सच्ची दोस्ती की जीत", "दोनों दोस्त सूंड़ उठाकर खुशी से नाचते हैं और जंगल में उत्सव छा जाता है।", "सच्ची दोस्ती हमेशा जीतती है, यह साबित हो गया!"),
            ]
        elif subtype == "cat":
            beats = [
                ("गाँव में नटखट बिल्ली", "गाँव की गलियों में एक चंचल और प्यारी बिल्ली मस्ती से दौड़ती है।", "सुबह की धूप में बिल्ली गाँव की छतों पर मजे से कूदती है।"),
                ("शरारतें और अठखेलियाँ", "उसकी उछलकूद और नटखट अदाएँ सबका ध्यान अपनी ओर खींच लेती हैं।", "हर घर के आगे वह अपनी मीठी आवाज से सबका दिल बहलाती है।"),
                ("सबके चेहरे पर मुस्कान", "उसकी मजेदार कलाबाजियाँ देखकर गाँव के बच्चे और बुजुर्ग खिलखिला उठते हैं।", "गाँव के हर चेहरे पर हंसी और खुशी की लहर दौड़ जाती है।"),
                ("मस्ती भरा खेल", "बच्चे उसके साथ खेलने लगते हैं और पूरा गाँव एक मेले जैसा बन जाता है।", "बिल्ली की मासूमियत ने माहौल को खुशियों से सराबोर कर दिया।"),
                ("गाँव की चहेती रानी", "अपनी मीठी शरारतों से बिल्ली ने पूरे गाँव का दिल जीत लिया।", "अब वह केवल एक बिल्ली नहीं, बल्कि पूरे गाँव की लाडली बन चुकी है!"),
            ]
        elif subtype == "dinosaur":
            beats = [
                ("डांसर बनने का सपना", "एक नन्हा प्यारा डायनासोर दुनिया का मशहूर डांसर बनने की ठान लेता है।", "संगीत की धुन सुनते ही नन्हे डायनासोर के कदम थिरकने लगते हैं।"),
                ("लगन से रियाज", "वह अपनी पूँछ हिलाकर और पंजों को हवा में उछालकर नए डांस स्टेप्स सीखता है।", "दिन-रात वह अपने डांस को बेहतर बनाने में जुटा रहता है।"),
                ("जंगल का डांस फ्लोर", "जंगल के सारे जानवर उसका अनोखा डांस देखने के लिए इकट्ठे हो जाते हैं।", "दर्शकों की तालियों के साथ वह मंच पर पूरी ऊर्जा से उतरता है।"),
                ("शानदार परफॉर्मेंस", "उसने ऐसे हैरतअंगेज डांस मूव्स दिखाए कि सब दंग रह गए।", "हर कोई उसके ताल और लय की तारीफ करते नहीं थक रहा था।"),
                ("जंगल का डांस स्टार", "तालियों की गड़गड़ाहट के बीच नन्हा डायनासोर जंगल का सबसे बड़ा डांसर बन गया!", "सच्ची लगन से देखा गया हर सपना सच होता है!"),
            ]
        elif subtype == "boy":
            beats = [
                ("सपनों की नई शुरुआत", "एक गरीब परिवार का लड़का अपने बड़े सपनों को पूरा करने का पक्का इरादा करता है।", "मुश्किल हालात के बावजूद उसकी आँखों में कामयाबी का जुनून है।"),
                ("कठिन मेहनत की डगर", "वह दिन-रात ईमानदारी और लगन के साथ पढ़ाई और मेहनत करता है।", "हार न मानने का जज्बा उसे हर मुश्किल से लड़ने की ताकत देता है।"),
                ("मुसीबतों का सामना", "हर चुनौती को उसने अपनी सूझबूझ और धैर्य से मात दी।", "उसकी कड़ी मेहनत का रंग अब धीरे-धीरे दिखने लगा है।"),
                ("सफलता का शिखर", "आखिरकार उसकी मेहनत रंग लाई और उसने सबसे बड़ा मुकाम हासिल कर लिया।", "उसकी सफलता की गूंज पूरे इलाके में गर्व से गूंज उठी।"),
                ("गर्व का नया सवेरा", "गरीबी को मात देकर उसने साबित कर दिया कि हौसले बुलंद हों तो हर मंजिल आसान है!", "गाँव का सिर फख्र से ऊँचा हो गया!"),
            ]
        elif subtype == "girl":
            beats = [
                ("गाँव का जल संकट", "गाँव में पानी की गंभीर समस्या देखकर एक होशियार लड़की ने समाधान निकालने का फैसला किया।", "गाँव की महिलाओं की परेशानी देखकर उसका दिल पसीज गया।"),
                ("वैज्ञानिक योजना", "उसने वर्षा जल संचयन और तालाबों की सफाई का एक शानदार प्लान तैयार किया।", "उसने पूरे गाँव को इकट्ठा करके योजना के फायदे समझाए।"),
                ("एकजुट गाँव की ताकत", "उसके नेतृत्व में सभी ग्रामीणों ने मिलकर श्रमदान शुरू किया।", "नहरों और तालाबों का पुनर्निर्माण तेजी से पूरा हुआ।"),
                ("पानी से लबालब जलाशय", "पहली ही बारिश में गाँव के सारे कुएँ और तालाब लबालब भर गए।", "सूखे का डर खत्म हुआ और खेतों में हरियाली लौट आई।"),
                ("गाँव की बहादुर बेटी", "अपनी सूझबूझ से गाँव को जल संकट से बचाने वाली बेटी का सबने सम्मान किया!", "दृढ़ संकल्प से बड़ा कोई हथियार नहीं होता!"),
            ]
        else:
            beats = [
                (f"{sub_name} का आगमन", f"{sub_name} अपने अनोखे अंदाज में सफर की शुरुआत करता है।", f"{sub_name} के साथ एक नए और रोमांचक सफर का आरंभ हुआ है।"),
                (f"{sub_name} की तेज रफ्तार", f"{sub_name} पूरी ऊर्जा के साथ आगे बढ़ता है।", f"हर कदम पर नया रोमांच और खूबसूरती देखने को मिलती है।"),
                (f"{sub_name} की ऊँची उड़ान", f"{sub_name} नई ऊंचाइयों को छूते हुए मंजिल की ओर अग्रसर है।", f"चारों तरफ उसकी चमक और प्रभाव छा गया है।"),
                (f"{sub_name} का करिश्मा", f"{sub_name} अपने अद्भुत करतबों से सबका दिल जीत लेता है।", f"वातावरण में एक अनोखा जादू घुल चुका है।"),
                (f"{sub_name} की विजय", f"{sub_name} ने सफलता के साथ अपने सफर को मुकाम तक पहुंचाया।", f"इस तरह यह खूबसूरत सफर एक यादगार जीत के साथ पूरा हुआ।"),
            ]

    else:
        # English narrative arcs
        if subtype == "lotus":
            beats = [
                ("The Awakening Lotus", "A delicate pink lotus unfolds its petals over the tranquil pond.", "At dawn, the magical pink lotus awakens in crystal clear waters."),
                ("Dance of the Petals", "Gentle ripples pulse across the water as the flower sways rhythmically.", "Drifting with the breeze, every petal dances in harmonic grace."),
                ("Golden Solar Rays", "Sunlight illuminates golden pollen, radiating warm reflections.", "The lotus glows brightly, mirroring the morning sun upon the pond."),
                ("Enchanted Water Ballet", "Dragonflies and water gliders gather to admire the choreography.", "Sparkling ripples scatter soft light throughout the peaceful cove."),
                ("Serenade at Dusk", "The lotus rests softly on its lily pad, leaving a lingering aura.", "Our journey concludes in timeless serenity over the enchanted waters."),
            ]
        elif subtype == "elephant":
            beats = [
                ("The Quest Begins", "A spirited baby elephant journeys deep into the jungle to find a lost companion.", "Determined and curious, the little elephant steps into the dense wild."),
                ("Trail Through the Canopy", "Flapping large ears and curling its trunk, it follows playful footprints.", "Through winding paths and towering vines, it sounds a friendly call."),
                ("Clues by the Riverbank", "Fresh tracks beside the shimmering river bring newfound hope.", "Splashing through cool waters, the scent of reunion grows stronger."),
                ("A Joyful Reunion", "Parting the reeds, both friends spot each other and trumpet with glee.", "Tears of relief turn into enthusiastic cheers across the forest."),
                ("Celebration in the Wild", "Dancing side by side with raised trunks, harmony returns to the woods.", "True friendship triumphs once more under the sunlit canopy!"),
            ]
        elif subtype == "cat":
            beats = [
                ("The Village Arrival", "A mischievous cat trots playfully into the sunlit village square.", "Prancing along terracotta rooftops, the clever cat catches every eye."),
                ("Whimsical Antics", "Leaping from fences to porches, its humorous antics amuse the locals.", "Every playful twist brings a smile to the busy villagers."),
                ("Laughter Along the Streets", "Children and elders alike stop to giggle at its acrobatic hops.", "The whole village resonates with warm laughter and cheerful spirit."),
                ("Game of Chase", "Chasing playful butterflies, the cat leads a spirited dance through town.", "A wave of joyful energy sweeps through every cozy street."),
                ("Crown of the Town", "Basking in affection, the charming cat becomes the village's darling hero.", "With purrs and high spirits, laughter unites the entire community!"),
            ]
        elif subtype == "dinosaur":
            beats = [
                ("A Big Dancing Dream", "A cheerful baby dinosaur aspires to become the world's most famous dancer.", "Listening to the jungle beat, its tiny feet begin to tap."),
                ("Rhythm and Practice", "Wagging its tail and swinging its claws, it practices dynamic spins.", "Day by day, the little dancer masters energetic routines."),
                ("The Jungle Stage", "Wild creatures gather around the clearing to watch the debut performance.", "Spotlights of sunlight pierce through the trees onto the dance floor."),
                ("Showstopping Routine", "Unleashing a spectacular flurry of hops and pirouettes, it dazzles the crowd.", "Roars of applause echo through the valley as the tempo peaks."),
                ("The Dancing Sensation", "Bowing to roaring cheers, the little dinosaur claims its superstar crown!", "Proof that passion and rhythm know no bounds!"),
            ]
        elif subtype == "boy":
            beats = [
                ("Humble Beginnings", "A hardworking boy with big dreams sets his sights on overcoming all odds.", "Armed with resolve, he turns every hardship into a stepping stone."),
                ("Relentless Dedication", "Burning the midnight oil, he studies and strives tirelessly day and night.", "Neither fatigue nor doubt can shake his iron determination."),
                ("Overcoming the Obstacles", "Every hurdle is met with intellect, patience, and courage.", "His relentless perseverance begins to unlock doors once thought shut."),
                ("The Breakthrough", "Achieving top honors, he stands triumphant as his hard work bears fruit.", "News of his grand triumph echoes with pride across the village."),
                ("Inspiration to All", "Rising from poverty to glorious victory, he proves perseverance conquers all!", "A shining beacon of hope for every dreamer!"),
            ]
        elif subtype == "girl":
            beats = [
                ("A Community's Challenge", "Faced with severe drought, an ingenious village girl steps forward with a plan.", "Seeing her community struggle, she dedicates her mind to a solution."),
                ("The Innovative Blueprint", "She designs a sustainable rainwater harvesting and reservoir restoration plan.", "Gathering elders and youths, she explains the vision with clarity."),
                ("United Efforts", "Inspired by her leadership, the entire village unites in communal action.", "Canals are cleared and check dams built with collective vigor."),
                ("Overflowing Reservoirs", "With the first seasonal rains, the lakes and wells fill to the brim.", "Fresh water flows abundantly, banishing drought from the soil."),
                ("The Village Savior", "Celebrating the clever girl who brought life back to their homeland!", "Wisdom, empathy, and unity turn adversity into triumph!"),
            ]
        else:
            beats = [
                (f"Awakening of {sub_name}", f"{sub_name} steps into the vibrant world, commencing a new journey.", f"In the expanse of the {env['name']}, our tale begins with {sub_name}."),
                (f"{sub_name} Moves Forward", f"{sub_name} picks up velocity, navigating scenic parallax terrain.", f"Gathering strength and pace, {sub_name} ventures into the horizon."),
                (f"Elevation and Climax", f"Dynamic acceleration and ascending flight across the landscape.", f"Every motion creates ripples of excitement in the atmosphere."),
                (f"Graceful Mastery", f"Acrobatic maneuvers showcase agility, beauty, and control.", f"With poised elegance, {sub_name} commands the setting."),
                (f"Grand Harmony", f"Reaching full equilibrium, {sub_name} concludes this cinematic odyssey.", f"The echoes of this heroic journey settle into lasting glory."),
            ]

    scenes: List[Dict[str, Any]] = []

    for i in range(scene_count):
        cur_dur = base_dur + (1 if i < remainder else 0)
        # Select beat from templates
        beat_idx = min(i, len(beats) - 1)
        title, desc, narr = beats[beat_idx]

        motion = motion_types[i % len(motion_types)]
        camera = camera_motions[i % len(camera_motions)]

        # If more scenes than default beats, adjust descriptions
        if i >= len(beats):
            if lang == "mr":
                title = f"{sub_name} - टप्पा {i + 1}"
                desc = f"{sub_name} चा पुढील रोमांचक प्रवास भाग {i + 1}."
                narr = f"प्रवासाचा {i + 1} वा टप्पा पार करताना {sub_name} ची ऊर्जा अजून वाढते."
            elif lang == "hi":
                title = f"{sub_name} - चरण {i + 1}"
                desc = f"{sub_name} का अगला रोमांचक सफर भाग {i + 1}."
                narr = f"सफर के {i + 1} वें पड़ाव पर {sub_name} नए उत्साह से आगे बढ़ता है।"
            else:
                title = f"{sub_name} - Act {i + 1}"
                desc = f"Continuing {sub_name}'s voyage across sector {i + 1}."
                narr = f"Advancing through stage {i + 1}, {sub_name} demonstrates relentless energy."

        scenes.append({
            "scene_number": i + 1,
            "title": title,
            "description": desc,
            "narration": narr,
            "motion_type": motion,
            "camera_motion": camera,
            "character_action": f"{sub_name} - {motion.replace('_', ' ').title()}",
            "motion_instruction": f"Camera {camera.replace('_', ' ')} with {sub_name} executing {motion.replace('_', ' ')}.",
            "duration": cur_dur,
        })

    return scenes
