"""
Universal Prompt-to-Animation Semantic Engine.
Interprets arbitrary user prompts to extract subjects, visual environment,
action choreography, camera dynamics, and multi-scene narrative progression.
"""

import math
import re
from typing import Any, Dict, List, Tuple


# Color palettes by keyword
COLOR_KEYWORDS: Dict[str, Tuple[int, int, int]] = {
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
    "black": (30, 41, 59),
    "dark": (15, 23, 42),
    "neon": (56, 189, 248),
}

# Environment definitions
ENVIRONMENTS = {
    "space": {
        "keywords": ["space", "galaxy", "orbit", "cosmos", "stars", "nebula", "planet", "asteroid", "alien", "mars", "moon"],
        "bg_top": (5, 8, 24),
        "bg_bottom": (16, 24, 56),
        "horizon": (30, 41, 89),
        "particles": "stars",
        "ground_type": "surface",
    },
    "ocean": {
        "keywords": ["ocean", "sea", "underwater", "water", "marine", "reef", "depths", "waves", "subsea", "trench", "abyss"],
        "bg_top": (4, 25, 55),
        "bg_bottom": (8, 48, 92),
        "horizon": (14, 80, 130),
        "particles": "bubbles",
        "ground_type": "seabed",
    },
    "cyberpunk": {
        "keywords": ["cyber", "neon", "city", "future", "futuristic", "highway", "metropolis", "robot", "tech", "matrix"],
        "bg_top": (15, 10, 32),
        "bg_bottom": (35, 18, 65),
        "horizon": (65, 24, 105),
        "particles": "rain",
        "ground_type": "road",
    },
    "sky": {
        "keywords": ["sky", "clouds", "flying", "sunset", "soar", "horizon", "atmosphere", "aerial", "flight"],
        "bg_top": (25, 45, 95),
        "bg_bottom": (180, 85, 90),
        "horizon": (245, 158, 60),
        "particles": "dust",
        "ground_type": "clouds",
    },
    "nature": {
        "keywords": ["forest", "trees", "mountain", "jungle", "meadow", "garden", "wild", "valley", "green", "woods"],
        "bg_top": (12, 35, 45),
        "bg_bottom": (24, 65, 55),
        "horizon": (40, 95, 70),
        "particles": "fireflies",
        "ground_type": "grass",
    },
    "desert": {
        "keywords": ["desert", "dune", "sand", "canyon", "pyramid", "sahara", "arid"],
        "bg_top": (45, 25, 20),
        "bg_bottom": (120, 65, 35),
        "horizon": (210, 130, 60),
        "particles": "dust",
        "ground_type": "sand",
    },
    "snow": {
        "keywords": ["snow", "ice", "arctic", "glacier", "frozen", "winter", "cold", "blizzard"],
        "bg_top": (20, 30, 50),
        "bg_bottom": (70, 95, 130),
        "horizon": (180, 205, 230),
        "particles": "snow",
        "ground_type": "ice",
    },
    "magical": {
        "keywords": ["magic", "mystical", "fantasy", "enchanted", "fairy", "crystal", "sparkle", "dream", "glowing"],
        "bg_top": (20, 10, 40),
        "bg_bottom": (50, 20, 80),
        "horizon": (95, 40, 135),
        "particles": "embers",
        "ground_type": "ethereal",
    },
}

# Entity classification patterns
ENTITY_PATTERNS = [
    ("vehicle", ["rocket", "spaceship", "shuttle", "car", "sports car", "automobile", "submarine", "sub", "airplane", "plane", "jet", "boat", "ship", "train", "rover", "hovercraft", "drone"]),
    ("animal", ["dragon", "eagle", "bird", "hawk", "dolphin", "whale", "fish", "shark", "lion", "tiger", "wolf", "horse", "dog", "puppy", "cat", "kitten", "bear", "butterfly", "fox", "deer", "dinosaur", "trex"]),
    ("humanoid", ["astronaut", "cosmonaut", "diver", "robot", "cyborg", "android", "wizard", "mage", "detective", "knight", "warrior", "dancer", "child", "girl", "boy", "scientist", "superhero", "pilot"]),
    ("celestial", ["star", "comet", "meteor", "planet", "asteroid", "sun", "moon", "galaxy", "black hole"]),
    ("nature_object", ["tree", "flower", "lotus", "mushroom", "crystal", "gem", "coral", "mountain", "volcano"]),
    ("architecture", ["lighthouse", "castle", "tower", "bridge", "temple", "pyramid", "cabin", "cottage", "windmill"]),
]


def extract_colors_from_prompt(prompt: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    """Extract primary, secondary, and accent colors from descriptive keywords."""
    words = re.findall(r"\b[a-zA-Z]+\b", prompt.lower())
    found_colors: List[Tuple[int, int, int]] = []

    for word in words:
        if word in COLOR_KEYWORDS:
            col = COLOR_KEYWORDS[word]
            if col not in found_colors:
                found_colors.append(col)

    # Defaults if none or few colors mentioned
    default_palette = [
        (59, 130, 246),   # Electric blue
        (236, 72, 153),   # Vibrant magenta
        (250, 204, 21),   # Golden amber
    ]

    while len(found_colors) < 3:
        found_colors.append(default_palette[len(found_colors)])

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

    # If no strong match, infer from general keywords
    if best_score == 0:
        if any(w in p for w in ["drive", "speed", "road", "street"]):
            best_env = "cyberpunk"
        elif any(w in p for w in ["fly", "soar", "high", "glide"]):
            best_env = "sky"
        elif any(w in p for w in ["swim", "float", "deep"]):
            best_env = "ocean"
        else:
            best_env = "magical"

    cfg = ENVIRONMENTS[best_env].copy()
    cfg["name"] = best_env
    return cfg


def detect_entity(prompt: str) -> Dict[str, Any]:
    """Detect subject entity category, subtype, and descriptive properties."""
    p = prompt.lower()
    primary_col, sec_col, accent_col = extract_colors_from_prompt(prompt)

    # Look for known entity match
    detected_cat = "humanoid"
    detected_subtype = "character"

    for cat, subtypes in ENTITY_PATTERNS:
        for sub in subtypes:
            if re.search(r"\b" + re.escape(sub) + r"\b", p):
                detected_cat = cat
                detected_subtype = sub
                break
        if detected_subtype != "character":
            break

    # If no specific subtype found, extract the most prominent noun phrase
    if detected_subtype == "character":
        # Extract plausible subject from prompt
        tokens = [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", p) if w not in {"the", "and", "with", "from", "that", "this", "over", "into", "through"}]
        if tokens:
            detected_subtype = tokens[0]

    return {
        "category": detected_cat,
        "subtype": detected_subtype,
        "primary_color": primary_col,
        "secondary_color": sec_col,
        "accent_color": accent_col,
        "glowing": any(w in p for w in ["glow", "radiant", "bioluminescent", "neon", "laser", "shining", "crystal", "magic"]),
    }


def compute_scenes_for_duration(prompt: str, style: str, duration: int) -> List[Dict[str, Any]]:
    """
    Universally partitions arbitrary user requests from 5s to 300s
    into sequential cinematic acts and scenes without hardcoded subjects.
    """
    duration = max(5, min(300, duration))

    # Calculate optimal scene count
    if duration <= 10:
        scene_count = 2
    elif duration <= 20:
        scene_count = 3
    elif duration <= 40:
        scene_count = 4
    elif duration <= 75:
        scene_count = 5
    elif duration <= 120:
        scene_count = 7
    elif duration <= 180:
        scene_count = 10
    else:
        scene_count = min(18, duration // 15)

    base_dur = duration // scene_count
    remainder = duration % scene_count

    entity = detect_entity(prompt)
    env = detect_environment(prompt)

    sub_name = entity["subtype"].title()
    env_name = env["name"].title()

    # Cinematic Motion types available in procedural engine
    motion_types = [
        "horizontal_travel",
        "vertical_climb_or_launch",
        "hover_and_sway",
        "dynamic_bounce",
        "pirouette_spin",
        "accelerate_zoom",
        "grand_parade",
    ]

    # Camera movements
    camera_motions = [
        "pan_right",
        "zoom_in",
        "tracking_shot",
        "crane_up",
        "pan_left",
        "dramatic_zoom_out",
        "dynamic_orbit",
    ]

    # Narrative beat archetypes for any subject
    act_templates = [
        # Act 1: Establishing & Awakening
        {
            "title": f"The Awakening of {sub_name}",
            "description": f"Panoramic wide shot establishing the {env_name} environment. {sub_name} appears, coming to life with ambient illumination.",
            "narration": f"In the vast expanse of the {env['name']}, our journey begins with {sub_name}.",
            "motion": "hover_and_sway",
            "camera": "zoom_in",
        },
        # Act 2: Inciting Motion / Setting Off
        {
            "title": f"{sub_name} Sets Off",
            "description": f"{sub_name} gathers momentum, beginning its dynamic movement through layered {env_name} parallax scenery.",
            "narration": f"Gathering power and purpose, {sub_name} pushes forward into the uncharted realm.",
            "motion": "horizontal_travel",
            "camera": "tracking_shot",
        },
        # Act 3: Ascending / Leaping Progression
        {
            "title": f"The Surge Through {env_name}",
            "description": f"Energetic acceleration and elevation. Visual particle streams respond as {sub_name} soars through the atmosphere.",
            "narration": f"Every wave of motion ripples through the surroundings as velocity peaks.",
            "motion": "vertical_climb_or_launch",
            "camera": "crane_up",
        },
        # Act 4: Dynamic Acrobatics & Maneuver
        {
            "title": f"Graceful Maneuvers",
            "description": f"Intricate rotational maneuvers and full-axis choreography showcasing agility and precision.",
            "narration": f"With breathtaking poise, {sub_name} weaves through the radiant light of the horizon.",
            "motion": "pirouette_spin",
            "camera": "dynamic_orbit",
        },
        # Act 5: Climax & High Energy Peak
        {
            "title": f"Triumphant Climax",
            "description": f"Peak visual crescendo! Full environmental resonance with explosive particle trails and high-speed motion.",
            "narration": f"Reaching the summit of the quest, {sub_name} unleashes its full vibrant energy.",
            "motion": "accelerate_zoom",
            "camera": "pan_right",
        },
        # Act 6: Grand Finale / Resolution
        {
            "title": f"Harmonic Resonance",
            "description": f"Sweeping cinematic pull-back as {sub_name} reaches equilibrium in the transformed {env_name} landscape.",
            "narration": f"The echoes of the journey settle into timeless harmony across the glowing horizon.",
            "motion": "grand_parade",
            "camera": "dramatic_zoom_out",
        },
    ]

    scenes: List[Dict[str, Any]] = []

    for i in range(scene_count):
        cur_dur = base_dur + (1 if i < remainder else 0)
        # Select or interpolate narrative beat
        template_idx = min(i, len(act_templates) - 1)
        if i >= len(act_templates):
            # For longer multi-scene videos (e.g. 120s - 300s), generate episodic sequence
            scene_title = f"{sub_name} Expedition - Phase {i + 1}"
            scene_desc = f"Continuing {sub_name}'s voyage across sector {i + 1} of {env_name}. Dynamic terrain shift with atmospheric parallax."
            scene_narr = f"Navigating through the {i+1}th frontier, {sub_name} uncovers deeper wonders of the {env['name']}."
            motion = motion_types[i % len(motion_types)]
            camera = camera_motions[i % len(camera_motions)]
        else:
            tmpl = act_templates[template_idx]
            scene_title = tmpl["title"]
            scene_desc = tmpl["description"]
            scene_narr = tmpl["narration"]
            motion = tmpl["motion"]
            camera = tmpl["camera"]

        # Adapt narration voice according to style
        if style == "Cartoon":
            scene_narr = f"Look at {sub_name} go! Zooming through the wild {env['name']} like a champ!"
        elif style == "Educational":
            scene_narr = f"Observing the kinetic behavior and trajectories of {sub_name} within the {env['name']} medium."
        elif style == "Nursery Rhyme":
            scene_narr = f"Up and down, around they go, {sub_name} shining with a joyful glow!"

        scenes.append({
            "scene_number": i + 1,
            "title": scene_title,
            "description": scene_desc,
            "narration": scene_narr,
            "motion_type": motion,
            "camera_motion": camera,
            "character_action": f"{sub_name} - {motion.replace('_', ' ').title()}",
            "motion_instruction": f"Camera {camera.replace('_', ' ')} with subject executing {motion.replace('_', ' ')}.",
            "duration": cur_dur,
        })

    return scenes
