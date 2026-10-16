"""
FrameFlow AI - Procedural 2D Multi-Layer Animation Engine.
Supports:
- Multilingual Unicode fonts (Devanagari for Hindi & Marathi via Nirmala UI, Latin for English)
- Category-aware dynamic procedural sprites (lotus, elephant, cat, dinosaur, boy, girl, rocket, car, bird, dragon, astronaut, star)
- Multi-depth parallax backgrounds (pond, village, jungle, space, cyberpunk, sky, ocean, desert, snow, magical)
- Fluid procedural kinematics (squash & stretch, swimming undulation, wing flapping, ear fluttering, trunk swinging)
- Virtual 2D camera viewport motion (pan, tilt, push-in zoom, tracking, camera shake)
- Dynamic environmental particle systems (bubbles, fireflies, rain, snow, embers, stars)
- Cinematic overlay with scene title, choreography badge, and native subtitles.
"""

import math
import os
import random
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


RESOLUTIONS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (1080, 1080),
}


def get_font(size: int, bold: bool = False):
    """Load Unicode font with full Devanagari (Hindi & Marathi) and Latin support."""
    # Preferred fonts with native Devanagari and Latin glyph sets
    font_candidates = [
        "C:/Windows/Fonts/NirmalaB.ttc" if bold else "C:/Windows/Fonts/Nirmala.ttc",
        "C:/Windows/Fonts/Nirmala.ttc",
        "Nirmala.ttc",
        "C:/Windows/Fonts/mangal.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "arial.ttf",
    ]

    for candidate in font_candidates:
        if os.path.isabs(candidate) and not os.path.exists(candidate):
            continue
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue

    try:
        return ImageFont.load_default()
    except Exception:
        return None


# ============================================================================
# Dynamic Subject Sprite Generators
# ============================================================================

def create_subject_sprite(entity: Dict[str, Any], size: int = 400, frame_phase: float = 0.0) -> Image.Image:
    """
    Renders a prompt-specific procedural subject sprite.
    Uses frame_phase (0.0 to 2*pi) for internal skeletal/anatomical animations
    like wing flapping, ear fluttering, trunk swinging, swimming undulation.
    """
    sprite = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)
    cx, cy = size // 2, size // 2

    cat = entity.get("category", "humanoid")
    sub = entity.get("subtype", "character").lower()
    c_pri = entity.get("primary_color", (59, 130, 246))
    c_sec = entity.get("secondary_color", (236, 72, 153))
    c_acc = entity.get("accent_color", (250, 204, 21))

    # 1. LOTUS / FLOWER (Pink lotus dancing on pond)
    if sub in ["lotus", "flower", "कमल", "कमळ"]:
        # Animated floating lily pad base
        pad_r = int(size * 0.32)
        pad_y = cy + int(size * 0.16 + math.sin(frame_phase * 2.0) * 6)
        pad_color = (22, 101, 52, 230)
        draw.ellipse([cx - pad_r, pad_y - int(pad_r * 0.35), cx + pad_r, pad_y + int(pad_r * 0.35)], fill=pad_color, outline=(34, 197, 94, 255), width=2)
        # Lily pad cleft cutout
        cleft_pts = [(cx, pad_y), (cx + pad_r, pad_y - int(pad_r * 0.2)), (cx + int(pad_r * 0.8), pad_y + int(pad_r * 0.2))]
        draw.polygon(cleft_pts, fill=(0, 0, 0, 0))

        # Blooming / breathing petal oscillation
        bloom = math.sin(frame_phase * 3.0) * 0.08
        petal_len = int(size * (0.24 + bloom))
        petal_w = int(size * 0.11)
        lotus_cy = pad_y - 25

        # Background outer petals
        for angle in range(-70, 71, 35):
            rad = math.radians(angle + math.sin(frame_phase * 2.5) * 4)
            px = cx + math.sin(rad) * petal_len
            py = lotus_cy - math.cos(rad) * petal_len
            ctrl_x = cx + math.sin(rad) * (petal_len * 0.5)
            ctrl_y = lotus_cy - math.cos(rad) * (petal_len * 0.5)
            petal_pts = [
                (cx - petal_w // 2, lotus_cy),
                (ctrl_x - petal_w, ctrl_y),
                (px, py),
                (ctrl_x + petal_w, ctrl_y),
                (cx + petal_w // 2, lotus_cy),
            ]
            draw.polygon(petal_pts, fill=(*c_sec, 235), outline=(255, 255, 255, 200), width=2)

        # Foreground central blooming petals
        for angle in range(-45, 46, 30):
            rad = math.radians(angle)
            px = cx + math.sin(rad) * (petal_len * 0.9)
            py = lotus_cy - math.cos(rad) * (petal_len * 0.9)
            ctrl_x = cx + math.sin(rad) * (petal_len * 0.45)
            ctrl_y = lotus_cy - math.cos(rad) * (petal_len * 0.45)
            petal_pts = [
                (cx - int(petal_w * 0.4), lotus_cy),
                (ctrl_x - int(petal_w * 0.7), ctrl_y),
                (px, py),
                (ctrl_x + int(petal_w * 0.7), ctrl_y),
                (cx + int(petal_w * 0.4), lotus_cy),
            ]
            draw.polygon(petal_pts, fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

        # Golden stamen center & pollen glow
        stamen_r = int(size * 0.065)
        draw.ellipse([cx - stamen_r, lotus_cy - stamen_r, cx + stamen_r, lotus_cy + stamen_r], fill=(*c_acc, 255), outline=(254, 240, 138, 255), width=2)
        # Golden pollen dots
        for a in range(0, 360, 45):
            s_rad = math.radians(a + frame_phase * 20.0)
            dot_x = cx + math.cos(s_rad) * (stamen_r * 0.55)
            dot_y = lotus_cy + math.sin(s_rad) * (stamen_r * 0.55)
            draw.ellipse([dot_x - 2, dot_y - 2, dot_x + 2, dot_y + 2], fill=(255, 255, 255, 240))

    # 2. ELEPHANT (Little elephant looking for friend)
    elif sub in ["elephant", "हाथी", "हत्ती"]:
        walk_stride = math.sin(frame_phase * 4.0) * 12
        ear_flap = math.sin(frame_phase * 3.5) * 14
        trunk_curl = math.sin(frame_phase * 4.0) * 18

        # Main stout rounded body
        body_w = int(size * 0.38)
        body_h = int(size * 0.32)
        body_rect = [cx - body_w // 2 - 15, cy - body_h // 2, cx + body_w // 2 - 15, cy + body_h // 2]
        draw.ellipse(body_rect, fill=(*c_pri, 255), outline=(226, 232, 240, 220), width=2)

        # Stout elephant legs (walking motion)
        leg_w = int(size * 0.075)
        leg_h = int(size * 0.20)
        leg_y = cy + body_h // 2 - 12
        for lx, offset in [(cx - 55, walk_stride), (cx - 15, -walk_stride), (cx + 15, walk_stride), (cx + 55, -walk_stride)]:
            draw.rounded_rectangle([lx - leg_w // 2, leg_y, lx + leg_w // 2, leg_y + leg_h + int(offset * 0.3)], radius=6, fill=(*c_pri, 255), outline=(203, 213, 225, 200), width=1)
            # Toenails
            draw.ellipse([lx - leg_w // 2 + 2, leg_y + leg_h - 4, lx + leg_w // 2 - 2, leg_y + leg_h + 4], fill=(255, 255, 255, 220))

        # Big friendly head
        head_r = int(size * 0.16)
        head_x = cx + body_w // 2 - 10
        head_y = cy - 20
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=(*c_pri, 255), outline=(226, 232, 240, 220), width=2)

        # Flapping fan ear
        ear_w = int(head_r * 1.05)
        ear_h = int(head_r * 1.25)
        ear_x = head_x - head_r + int(ear_flap * 0.3)
        ear_y = head_y - 10
        draw.ellipse([ear_x - ear_w // 2, ear_y - ear_h // 2, ear_x + ear_w // 2, ear_y + ear_h // 2], fill=(*c_pri, 255), outline=(241, 245, 249, 240), width=2)
        # Soft pink inner ear
        draw.ellipse([ear_x - ear_w // 3, ear_y - ear_h // 3, ear_x + ear_w // 3, ear_y + ear_h // 3], fill=(*c_sec, 220))

        # Expressive eye
        eye_x = head_x + int(head_r * 0.35)
        eye_y = head_y - int(head_r * 0.2)
        draw.ellipse([eye_x - 6, eye_y - 6, eye_x + 6, eye_y + 6], fill=(15, 23, 42, 255))
        draw.ellipse([eye_x - 4, eye_y - 4, eye_x - 1, eye_y - 1], fill=(255, 255, 255, 255))

        # Ivory tusk
        tusk_pts = [(head_x + int(head_r * 0.5), head_y + 12), (head_x + int(head_r * 0.85), head_y + 20), (head_x + int(head_r * 0.5), head_y + 18)]
        draw.polygon(tusk_pts, fill=(255, 255, 255, 255), outline=(203, 213, 225, 200), width=1)

        # Animated curving trunk
        trunk_base_x = head_x + int(head_r * 0.65)
        trunk_base_y = head_y + 6
        tip_x = trunk_base_x + 35 + int(trunk_curl * 0.6)
        tip_y = trunk_base_y + 30 - int(trunk_curl)
        draw.line([(trunk_base_x, trunk_base_y), (trunk_base_x + 18, trunk_base_y + 22), (tip_x, tip_y)], fill=(*c_pri, 255), width=12)
        draw.ellipse([tip_x - 6, tip_y - 6, tip_x + 6, tip_y + 6], fill=(*c_sec, 255))

        # Wagging tail
        tail_x = cx - body_w // 2 - 15
        tail_y = cy - 5
        draw.line([(tail_x, tail_y), (tail_x - 22, tail_y + 25 + int(walk_stride))], fill=(*c_pri, 255), width=4)
        draw.ellipse([tail_x - 26, tail_y + 25 + int(walk_stride) - 4, tail_x - 18, tail_y + 25 + int(walk_stride) + 4], fill=(30, 41, 59, 255))

    # 3. CAT / KITTEN (Playful cat making village laugh)
    elif sub in ["cat", "kitten", "मांजर", "बिल्ली"]:
        bounce = math.sin(frame_phase * 4.5) * 8
        tail_sway = math.sin(frame_phase * 5.0) * 22

        # Fluffy body
        body_w = int(size * 0.32)
        body_h = int(size * 0.26)
        draw.ellipse([cx - body_w // 2, cy - body_h // 2 + bounce, cx + body_w // 2, cy + body_h // 2 + bounce], fill=(*c_pri, 255), outline=(255, 255, 255, 200), width=2)
        # White belly patch
        draw.ellipse([cx - int(body_w * 0.3), cy - int(body_h * 0.2) + bounce, cx + int(body_w * 0.3), cy + int(body_h * 0.35) + bounce], fill=(255, 255, 255, 220))

        # Head
        head_r = int(size * 0.14)
        head_x = cx + int(body_w * 0.28)
        head_y = cy - 25 + bounce
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

        # Pointed perky ears
        draw.polygon([(head_x - head_r + 6, head_y - int(head_r * 0.4)), (head_x - int(head_r * 0.7), head_y - head_r - 18), (head_x - 6, head_y - head_r + 4)], fill=(*c_pri, 255))
        draw.polygon([(head_x - head_r + 10, head_y - int(head_r * 0.4)), (head_x - int(head_r * 0.7), head_y - head_r - 12), (head_x - 10, head_y - head_r + 4)], fill=(*c_sec, 255))
        draw.polygon([(head_x + 6, head_y - head_r + 4), (head_x + int(head_r * 0.7), head_y - head_r - 18), (head_x + head_r - 6, head_y - int(head_r * 0.4))], fill=(*c_pri, 255))
        draw.polygon([(head_x + 10, head_y - head_r + 4), (head_x + int(head_r * 0.7), head_y - head_r - 12), (head_x + head_r - 10, head_y - int(head_r * 0.4))], fill=(*c_sec, 255))

        # Big glossy cat eyes
        eye_y = head_y - 4
        for ex in (head_x - 14, head_x + 14):
            draw.ellipse([ex - 7, eye_y - 7, ex + 7, eye_y + 7], fill=(52, 211, 153, 255), outline=(15, 23, 42, 255), width=2)
            # Vertical pupil
            draw.ellipse([ex - 2, eye_y - 6, ex + 2, eye_y + 6], fill=(15, 23, 42, 255))
            draw.ellipse([ex - 4, eye_y - 4, ex - 1, eye_y - 1], fill=(255, 255, 255, 240))

        # Cute pink nose & whiskers
        draw.polygon([(head_x - 3, head_y + 7), (head_x + 3, head_y + 7), (head_x, head_y + 11)], fill=(244, 114, 182, 255))
        for wy in (-3, 2):
            draw.line([(head_x - 8, head_y + 10 + wy), (head_x - 32, head_y + 7 + wy * 3)], fill=(255, 255, 255, 240), width=2)
            draw.line([(head_x + 8, head_y + 10 + wy), (head_x + 32, head_y + 7 + wy * 3)], fill=(255, 255, 255, 240), width=2)

        # Expressive curling tail
        tail_start_x = cx - body_w // 2 + 5
        tail_start_y = cy + 5 + bounce
        draw.line([(tail_start_x, tail_start_y), (tail_start_x - 25, tail_start_y - 30), (tail_start_x - 15 + tail_sway, tail_start_y - 55)], fill=(*c_pri, 255), width=7)

        # Paws
        paw_y = cy + body_h // 2 - 4 + bounce
        for px in (cx - 30, cx - 10, cx + 15, cx + 35):
            draw.rounded_rectangle([px - 6, paw_y, px + 6, paw_y + 14], radius=4, fill=(255, 255, 255, 255), outline=(203, 213, 225, 200), width=1)

    # 4. DINOSAUR (Cute baby dino dancing)
    elif sub in ["dinosaur", "trex", "dino", "डायनासोर"]:
        dance_hop = math.sin(frame_phase * 5.0) * 16
        tail_wag = math.cos(frame_phase * 5.0) * 20
        arm_clap = math.sin(frame_phase * 6.0) * 12

        # Round cute baby dino body
        body_w = int(size * 0.30)
        body_h = int(size * 0.35)
        draw.ellipse([cx - body_w // 2, cy - body_h // 2 + dance_hop, cx + body_w // 2, cy + body_h // 2 + dance_hop], fill=(*c_pri, 255), outline=(255, 255, 255, 200), width=2)
        # Yellow belly patch
        draw.ellipse([cx - int(body_w * 0.25), cy - int(body_h * 0.1) + dance_hop, cx + int(body_w * 0.35), cy + int(body_h * 0.4) + dance_hop], fill=(254, 240, 138, 240))

        # Big head with rounded snout
        head_w = int(size * 0.22)
        head_h = int(size * 0.20)
        head_x = cx + 25
        head_y = cy - body_h // 2 + dance_hop
        draw.ellipse([head_x - head_w // 2, head_y - head_h // 2, head_x + head_w // 2, head_y + head_h // 2], fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

        # Back ridge spikes
        for sy in range(-25, 35, 15):
            draw.polygon([(cx - body_w // 2 + 5, cy + sy + dance_hop), (cx - body_w // 2 - 14, cy + sy - 6 + dance_hop), (cx - body_w // 2 + 5, cy + sy - 12 + dance_hop)], fill=(*c_acc, 255))

        # Happy friendly eye
        eye_x = head_x + 10
        eye_y = head_y - 10
        draw.ellipse([eye_x - 8, eye_y - 8, eye_x + 8, eye_y + 8], fill=(15, 23, 42, 255))
        draw.ellipse([eye_x - 5, eye_y - 5, eye_x - 1, eye_y - 1], fill=(255, 255, 255, 255))
        # Cheek blush
        draw.ellipse([eye_x - 12, eye_y + 12, eye_x - 2, eye_y + 18], fill=(244, 114, 182, 190))

        # Clapping front arms
        draw.line([(cx + 10, cy - 10 + dance_hop), (cx + 35 + arm_clap, cy + dance_hop)], fill=(*c_pri, 255), width=8)

        # Thick tail
        tail_base_x = cx - body_w // 2 + 5
        tail_base_y = cy + 20 + dance_hop
        draw.line([(tail_base_x, tail_base_y), (tail_base_x - 35, tail_base_y + tail_wag)], fill=(*c_pri, 255), width=14)

        # Dancing feet
        for fx in (cx - 20, cx + 20):
            draw.rounded_rectangle([fx - 12, cy + body_h // 2 - 5 + dance_hop, fx + 12, cy + body_h // 2 + 18 + dance_hop], radius=6, fill=(*c_pri, 255), outline=(22, 101, 52, 255), width=2)

    # 5. BOY / STUDENT / EXPLORER (Hardworking boy achieving success)
    elif sub in ["boy", "मुलगा", "लड़का"]:
        stride = math.sin(frame_phase * 4.0) * 14
        # Torso & Shirt
        torso_w = int(size * 0.20)
        torso_h = int(size * 0.28)
        draw.rounded_rectangle([cx - torso_w // 2, cy - torso_h // 2, cx + torso_w // 2, cy + torso_h // 2], radius=10, fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

        # Student Backpack
        draw.rounded_rectangle([cx - torso_w // 2 - 16, cy - torso_h // 2 + 6, cx - torso_w // 2 + 4, cy + torso_h // 2 - 6], radius=6, fill=(*c_acc, 255), outline=(15, 23, 42, 200), width=2)

        # Head & Stylized Hair
        head_r = int(size * 0.12)
        head_y = cy - torso_h // 2 - head_r + 6
        # Face skin tone
        draw.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r], fill=(254, 215, 170, 255), outline=(217, 119, 6, 180), width=1)
        # Hair
        draw.ellipse([cx - head_r, head_y - head_r - 4, cx + head_r, head_y - int(head_r * 0.2)], fill=(30, 41, 59, 255))
        draw.polygon([(cx - head_r, head_y - 5), (cx - head_r - 4, head_y - head_r), (cx, head_y - head_r - 8), (cx + head_r, head_y - head_r), (cx + head_r, head_y - 5)], fill=(30, 41, 59, 255))

        # Expressive eyes & smile
        draw.ellipse([cx - 8, head_y - 2, cx - 4, head_y + 2], fill=(15, 23, 42, 255))
        draw.ellipse([cx + 4, head_y - 2, cx + 8, head_y + 2], fill=(15, 23, 42, 255))
        draw.arc([cx - 8, head_y + 4, cx + 8, head_y + 12], start=0, end=180, fill=(220, 38, 38, 255), width=2)

        # Legs (Walking stride)
        draw.line([(cx - 14, cy + torso_h // 2), (cx - 14 - stride, cy + torso_h // 2 + 45)], fill=(30, 41, 59, 255), width=7)
        draw.line([(cx + 14, cy + torso_h // 2), (cx + 14 + stride, cy + torso_h // 2 + 45)], fill=(30, 41, 59, 255), width=7)

        # Arms (One raised in triumph / waving)
        draw.line([(cx - torso_w // 2, cy - 10), (cx - torso_w // 2 - 18, cy + 20 + stride)], fill=(*c_pri, 255), width=6)
        draw.line([(cx + torso_w // 2, cy - 10), (cx + torso_w // 2 + 25, cy - 35)], fill=(*c_pri, 255), width=6)
        # Raised hand
        draw.ellipse([cx + torso_w // 2 + 20, cy - 42, cx + torso_w // 2 + 32, cy - 30], fill=(254, 215, 170, 255))

    # 6. GIRL / STUDENT / VILLAGE HEROINE (Clever girl saving village)
    elif sub in ["girl", "मुलगी", "लड़की"]:
        stride = math.sin(frame_phase * 4.0) * 12
        # Traditional or modern bright dress
        torso_w = int(size * 0.18)
        torso_h = int(size * 0.32)
        dress_pts = [
            (cx - torso_w // 2, cy - torso_h // 2 + 10),
            (cx + torso_w // 2, cy - torso_h // 2 + 10),
            (cx + int(torso_w * 0.9), cy + torso_h // 2 + 20),
            (cx - int(torso_w * 0.9), cy + torso_h // 2 + 20),
        ]
        draw.polygon(dress_pts, fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

        # Head & Braided Hair
        head_r = int(size * 0.11)
        head_y = cy - torso_h // 2 - head_r + 14
        draw.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r], fill=(254, 215, 170, 255), outline=(217, 119, 6, 180), width=1)
        # Hair & Braids
        draw.ellipse([cx - head_r - 2, head_y - head_r - 4, cx + head_r + 2, head_y - 2], fill=(20, 20, 25, 255))
        # Flowing braid down shoulder
        braid_wave = math.sin(frame_phase * 3.5) * 6
        draw.line([(cx - head_r, head_y + 2), (cx - head_r - 8, head_y + 35 + braid_wave)], fill=(20, 20, 25, 255), width=7)

        # Bright expressive eyes & bindi / smile
        draw.ellipse([cx - 7, head_y - 2, cx - 3, head_y + 2], fill=(15, 23, 42, 255))
        draw.ellipse([cx + 3, head_y - 2, cx + 7, head_y + 2], fill=(15, 23, 42, 255))
        draw.ellipse([cx - 2, head_y - 8, cx + 2, head_y - 4], fill=(220, 38, 38, 255))  # Red bindi
        draw.arc([cx - 6, head_y + 4, cx + 6, head_y + 10], start=0, end=180, fill=(220, 38, 38, 255), width=2)

        # Arms (carrying symbolic water pot or notebook)
        draw.line([(cx - torso_w // 2, cy - 5), (cx - torso_w // 2 - 14, cy + 22)], fill=(254, 215, 170, 255), width=5)
        draw.line([(cx + torso_w // 2, cy - 5), (cx + torso_w // 2 + 15, cy + 15)], fill=(254, 215, 170, 255), width=5)
        # Notebook / vessel
        draw.rounded_rectangle([cx + torso_w // 2 + 10, cy + 5, cx + torso_w // 2 + 28, cy + 25], radius=4, fill=(*c_acc, 255), outline=(255, 255, 255, 220), width=1)

        # Feet stepping
        draw.line([(cx - 10, cy + torso_h // 2 + 20), (cx - 10 - stride, cy + torso_h // 2 + 45)], fill=(254, 215, 170, 255), width=5)
        draw.line([(cx + 10, cy + torso_h // 2 + 20), (cx + 10 + stride, cy + torso_h // 2 + 45)], fill=(254, 215, 170, 255), width=5)

    # 7. ROCKET / SPACESHIP
    elif sub in ["rocket", "spaceship", "shuttle"]:
        body_w = int(size * 0.22)
        body_h = int(size * 0.52)
        top_y = cy - body_h // 2
        bot_y = cy + body_h // 2 - 25

        flame_len = int(size * 0.22 + math.sin(frame_phase * 6.0) * 15)
        flame_w = int(body_w * 0.7)
        draw.polygon([(cx - flame_w // 2, bot_y), (cx + flame_w // 2, bot_y), (cx + int(math.sin(frame_phase * 8.0) * 6), bot_y + flame_len)], fill=(*c_acc, 230))
        draw.polygon([(cx - flame_w // 4, bot_y), (cx + flame_w // 4, bot_y), (cx, bot_y + int(flame_len * 0.6))], fill=(255, 255, 255, 255))

        fin_pts_l = [(cx - body_w // 2, bot_y - 30), (cx - body_w, bot_y + 10), (cx - body_w // 2, bot_y)]
        fin_pts_r = [(cx + body_w // 2, bot_y - 30), (cx + body_w, bot_y + 10), (cx + body_w // 2, bot_y)]
        draw.polygon(fin_pts_l, fill=(*c_sec, 255), outline=(255, 255, 255, 220), width=2)
        draw.polygon(fin_pts_r, fill=(*c_sec, 255), outline=(255, 255, 255, 220), width=2)

        draw.rounded_rectangle([cx - body_w // 2, top_y + 35, cx + body_w // 2, bot_y], radius=12, fill=(*c_pri, 255), outline=(255, 255, 255, 240), width=2)
        draw.polygon([(cx - body_w // 2, top_y + 35), (cx + body_w // 2, top_y + 35), (cx, top_y)], fill=(*c_sec, 255), outline=(255, 255, 255, 240), width=2)

        p_r = int(body_w * 0.3)
        p_y = top_y + int(body_h * 0.35)
        draw.ellipse([cx - p_r, p_y - p_r, cx + p_r, p_y + p_r], fill=(15, 23, 42, 255), outline=(*c_acc, 255), width=3)
        draw.ellipse([cx - p_r + 3, p_y - p_r + 3, cx - p_r + 9, p_y - p_r + 9], fill=(255, 255, 255, 240))

    # 8. CAR / VEHICLE
    elif sub in ["car", "automobile", "sports car", "गाडी", "गाड़ी"]:
        w_car = int(size * 0.65)
        h_car = int(size * 0.28)
        y_base = cy + 20
        pts = [
            (cx - w_car // 2, y_base),
            (cx - w_car // 2 + 30, y_base - h_car // 2),
            (cx - w_car // 4, y_base - h_car),
            (cx + w_car // 5, y_base - h_car),
            (cx + w_car // 2 - 20, y_base - h_car // 3),
            (cx + w_car // 2, y_base),
        ]
        draw.polygon(pts, fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

        win_pts = [
            (cx - w_car // 4 + 8, y_base - h_car + 6),
            (cx + w_car // 5 - 8, y_base - h_car + 6),
            (cx + w_car // 5 + 15, y_base - h_car // 2),
            (cx - w_car // 4 - 10, y_base - h_car // 2),
        ]
        draw.polygon(win_pts, fill=(15, 23, 42, 255), outline=(*c_sec, 200), width=2)

        hl_x = cx + w_car // 2 - 5
        hl_y = y_base - 10
        draw.ellipse([hl_x - 6, hl_y - 6, hl_x + 6, hl_y + 6], fill=(*c_acc, 255))
        draw.polygon([(hl_x, hl_y), (size - 10, hl_y - 30), (size - 10, hl_y + 40)], fill=(*c_acc, 50))

        wheel_r = int(size * 0.08)
        for wx in (cx - w_car // 3, cx + w_car // 3):
            draw.ellipse([wx - wheel_r, y_base - 5, wx + wheel_r, y_base - 5 + wheel_r * 2], fill=(20, 20, 25, 255), outline=(*c_sec, 255), width=3)
            ang = frame_phase * 4.0
            sx = wx + math.cos(ang) * (wheel_r * 0.7)
            sy = (y_base - 5 + wheel_r) + math.sin(ang) * (wheel_r * 0.7)
            draw.line([(wx, y_base - 5 + wheel_r), (sx, sy)], fill=(*c_acc, 255), width=2)

    # 9. BIRD / FLYING
    elif sub in ["bird", "eagle", "hawk", "पक्षी"]:
        wing_flap = math.sin(frame_phase * 4.5) * (size * 0.22)
        draw.ellipse([cx - 22, cy - 35, cx + 22, cy + 45], fill=(*c_pri, 255), outline=(255, 255, 255, 200), width=2)
        draw.ellipse([cx - 16, cy - 55, cx + 16, cy - 25], fill=(*c_sec, 255))
        draw.polygon([(cx + 10, cy - 42), (cx + 32, cy - 38), (cx + 10, cy - 34)], fill=(*c_acc, 255))
        draw.polygon([(cx - 15, cy - 10), (cx - int(size * 0.38), cy - 25 + wing_flap), (cx - int(size * 0.22), cy + 20)], fill=(*c_pri, 255), outline=(*c_sec, 255), width=2)
        draw.polygon([(cx + 15, cy - 10), (cx + int(size * 0.38), cy - 25 + wing_flap), (cx + int(size * 0.22), cy + 20)], fill=(*c_pri, 255), outline=(*c_sec, 255), width=2)
        draw.ellipse([cx + 4, cy - 44, cx + 8, cy - 40], fill=(255, 255, 255, 255))

    # 10. CELESTIAL / STAR
    elif sub in ["star", "sun", "तारा"]:
        pulse_r = int(size * 0.25 + math.sin(frame_phase * 3.0) * 12)
        for a in range(0, 360, 30):
            rad = math.radians(a + frame_phase * 20.0)
            ray_len = pulse_r + 35 + (20 if a % 60 == 0 else 0)
            draw.line([(cx, cy), (cx + math.cos(rad) * ray_len, cy + math.sin(rad) * ray_len)], fill=(*c_acc, 180), width=3)
        draw.ellipse([cx - pulse_r, cy - pulse_r, cx + pulse_r, cy + pulse_r], fill=(*c_pri, 255), outline=(255, 255, 255), width=3)
        draw.ellipse([cx - pulse_r // 2, cy - pulse_r // 2, cx + pulse_r // 2, cy + pulse_r // 2], fill=(255, 255, 255, 255))

    # 11. DEFAULT ASTRONAUT / HERO / EXPLORER
    else:
        stride = math.sin(frame_phase * 4.0) * 15
        torso_w = int(size * 0.22)
        torso_h = int(size * 0.32)
        draw.rounded_rectangle([cx - torso_w // 2, cy - torso_h // 2, cx + torso_w // 2, cy + torso_h // 2], radius=14, fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

        helm_r = int(size * 0.16)
        helm_y = cy - torso_h // 2 - helm_r + 10
        draw.ellipse([cx - helm_r, helm_y - helm_r, cx + helm_r, helm_y + helm_r], fill=(*c_sec, 255), outline=(255, 255, 255), width=2)
        v_w = int(helm_r * 0.75)
        v_h = int(helm_r * 0.55)
        draw.rounded_rectangle([cx - v_w, helm_y - v_h + 3, cx + v_w, helm_y + v_h], radius=10, fill=(15, 23, 42, 255), outline=(*c_acc, 255), width=2)
        draw.ellipse([cx - v_w + 4, helm_y - v_h + 5, cx - v_w + 12, helm_y - v_h + 12], fill=(255, 255, 255, 240))

        draw.line([(cx - 18, cy + torso_h // 2), (cx - 18 - stride, cy + torso_h // 2 + 45)], fill=(*c_pri, 255), width=7)
        draw.line([(cx + 18, cy + torso_h // 2), (cx + 18 + stride, cy + torso_h // 2 + 45)], fill=(*c_pri, 255), width=7)
        draw.line([(cx - torso_w // 2, cy - 10), (cx - torso_w // 2 - 20, cy + 20 + stride)], fill=(*c_sec, 255), width=6)
        draw.line([(cx + torso_w // 2, cy - 10), (cx + torso_w // 2 + 20, cy + 20 - stride)], fill=(*c_sec, 255), width=6)

    return sprite


# ============================================================================
# Multi-Layer Parallax Background Rendering
# ============================================================================

def render_parallax_environment(
    width: int,
    height: int,
    env: Dict[str, Any],
    camera_offset_x: float,
    camera_zoom: float,
    frame_time: float,
) -> Image.Image:
    """
    Renders layered parallax background based on environment theme:
    - Layer 1 (Sky / Deep cosmos): 0.1x parallax
    - Layer 2 (Distant terrain / village / skyline / water reeds): 0.35x parallax
    - Layer 3 (Ground / Pond water / Road): 1.0x parallax
    """
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(bg)

    c_top = env.get("bg_top", (10, 15, 30))
    c_bot = env.get("bg_bottom", (22, 36, 68))
    horizon_c = env.get("horizon", (40, 60, 100))
    env_name = env.get("name", "space")

    horizon_y = int(height * 0.62)

    # 1. Sky Gradient
    for y in range(horizon_y):
        t = y / max(1, horizon_y)
        r = int(c_top[0] * (1 - t) + c_bot[0] * t)
        g = int(c_top[1] * (1 - t) + c_bot[1] * t)
        b = int(c_top[2] * (1 - t) + c_bot[2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Celestial / Environmental Features (Layer 1 - deep background, 0.1x parallax)
    p_offset_1 = int(camera_offset_x * 0.1)

    if env_name == "space":
        planet_x = int((width * 0.75 - p_offset_1) % (width + 200)) - 100
        planet_y = int(height * 0.28)
        p_rad = int(height * 0.12)
        draw.ellipse([planet_x - p_rad, planet_y - p_rad, planet_x + p_rad, planet_y + p_rad], fill=(168, 85, 247, 240), outline=(216, 180, 254, 255), width=2)
        draw.ellipse([planet_x - int(p_rad * 1.8), planet_y - int(p_rad * 0.35), planet_x + int(p_rad * 1.8), planet_y + int(p_rad * 0.35)], outline=(244, 114, 182, 180), width=4)

    elif env_name in ["pond", "nature", "village", "sky"]:
        # Golden morning / twilight sun or moon
        sun_x = int((width * 0.7 - p_offset_1) % width)
        sun_y = int(height * 0.32)
        draw.ellipse([sun_x - 50, sun_y - 50, sun_x + 50, sun_y + 50], fill=(254, 240, 138, 220))
        draw.ellipse([sun_x - 80, sun_y - 80, sun_x + 80, sun_y + 80], fill=(251, 191, 36, 60))

    # 3. Layer 2: Distant Midground (0.35x parallax)
    p_offset_2 = int(camera_offset_x * 0.35)

    if env_name == "pond":
        # Water reeds, cattails, and willow reflections on shore
        shore_y = horizon_y
        for x in range(0, width + 60, 40):
            rx = (x - p_offset_2) % (width + 40) - 20
            sway = math.sin(frame_time * 2.0 + x) * 8
            draw.line([(rx, shore_y), (rx + sway, shore_y - 45)], fill=(13, 148, 136, 220), width=3)
            draw.ellipse([rx + sway - 4, shore_y - 52, rx + sway + 4, shore_y - 40], fill=(180, 83, 9, 230))

    elif env_name == "village":
        # Rolling green hills and cozy village cottage silhouettes
        hill_pts = [(0, horizon_y)]
        for x in range(0, width + 50, 50):
            hx = x
            hy = horizon_y - 35 + int(math.sin((x + p_offset_2) * 0.008) * 25)
            hill_pts.append((hx, hy))
        hill_pts.extend([(width, height), (0, height)])
        draw.polygon(hill_pts, fill=(34, 197, 94, 230))

        # Village cottages & stone well
        for cx_base in [width * 0.25, width * 0.65]:
            cx_pos = int((cx_base - p_offset_2) % (width + 100)) - 50
            cy_pos = horizon_y - 30
            # Thatched terracotta roof
            draw.polygon([(cx_pos - 35, cy_pos), (cx_pos, cy_pos - 30), (cx_pos + 35, cy_pos)], fill=(234, 88, 12, 255))
            # Hut wall
            draw.rectangle([cx_pos - 28, cy_pos, cx_pos + 28, cy_pos + 28], fill=(254, 243, 199, 255), outline=(180, 83, 9, 200), width=1)
            # Door
            draw.rectangle([cx_pos - 8, cy_pos + 8, cx_pos + 8, cy_pos + 28], fill=(120, 53, 15, 255))

    elif env_name == "cyberpunk":
        building_w = 48
        for i in range(-2, width // building_w + 3):
            bx = i * building_w - (p_offset_2 % building_w)
            bh = 120 + int(math.sin(i * 1.7) * 70)
            draw.rectangle([bx, horizon_y - bh, bx + building_w - 6, horizon_y], fill=(*horizon_c, 240))
            for wy in range(horizon_y - bh + 15, horizon_y - 15, 24):
                if (i + wy) % 2 == 0:
                    draw.rectangle([bx + 8, wy, bx + 16, wy + 10], fill=(56, 189, 248, 220))
                elif (i + wy) % 3 == 0:
                    draw.rectangle([bx + 26, wy, bx + 34, wy + 10], fill=(244, 114, 182, 220))

    else:
        # Organic mountain / hill silhouettes
        pts = [(0, horizon_y)]
        for x in range(0, width + 40, 30):
            nx = x
            ny = horizon_y - 45 + int(math.sin((x + p_offset_2) * 0.012) * 35 + math.cos((x + p_offset_2) * 0.025) * 15)
            pts.append((nx, ny))
        pts.extend([(width, height), (0, height)])
        draw.polygon(pts, fill=(*horizon_c, 240))

    # 4. Layer 3: Foreground Ground / Water / Road
    ground_type = env.get("ground_type", "surface")
    p_offset_3 = int(camera_offset_x * 1.0)

    if ground_type == "water" or env_name == "pond":
        # Shimmering reflective water surface with undulating animated wavelets
        water_top = (14, 116, 144)
        water_bot = (4, 47, 46)
        for y in range(horizon_y, height):
            wt = (y - horizon_y) / max(1, height - horizon_y)
            wr = int(water_top[0] * (1 - wt) + water_bot[0] * wt)
            wg = int(water_top[1] * (1 - wt) + water_bot[1] * wt)
            wb = int(water_top[2] * (1 - wt) + water_bot[2] * wt)
            draw.line([(0, y), (width, y)], fill=(wr, wg, wb, 255))

        # Dynamic reflective wave ripples
        for wy in range(horizon_y + 10, height, 18):
            wave_phase = frame_time * 3.5 + wy * 0.1
            for wx in range(0, width, 60):
                wave_x = (wx - p_offset_3 + int(math.sin(wave_phase) * 15)) % width
                draw.arc([wave_x - 20, wy - 4, wave_x + 20, wy + 4], start=0, end=180, fill=(204, 251, 241, 160), width=2)

    elif ground_type == "road":
        draw.rectangle([0, horizon_y, width, height], fill=(20, 24, 38, 255))
        for lane_y in range(horizon_y + 20, height, 40):
            draw.line([(0, lane_y), (width, lane_y)], fill=(56, 189, 248, 60), width=1)
        dash_w = 40
        dash_gap = 35
        cycle = dash_w + dash_gap
        offset = int(frame_time * 240) % cycle
        mid_y = horizon_y + (height - horizon_y) // 2
        for x in range(-cycle, width + cycle, cycle):
            dx = x - offset
            draw.line([(dx, mid_y), (dx + dash_w, mid_y)], fill=(251, 191, 36, 230), width=4)

    else:
        # Lush grass / terrain
        g_col_top = (22, 101, 52) if env_name in ["nature", "village"] else (15, 23, 42)
        g_col_bot = (20, 83, 45) if env_name in ["nature", "village"] else (5, 10, 20)
        for y in range(horizon_y, height):
            gt = (y - horizon_y) / max(1, height - horizon_y)
            gr = int(g_col_top[0] * (1 - gt) + g_col_bot[0] * gt)
            gg = int(g_col_top[1] * (1 - gt) + g_col_bot[1] * gt)
            gb = int(g_col_top[2] * (1 - gt) + g_col_bot[2] * gt)
            draw.line([(0, y), (width, y)], fill=(gr, gg, gb, 255))

        for tx in range(0, width, 18):
            blade_x = (tx - p_offset_3) % width
            draw.line([(blade_x, horizon_y), (blade_x + 3, horizon_y - 8)], fill=(34, 197, 94, 200), width=2)

    return bg


# ============================================================================
# Dynamic Particle Systems
# ============================================================================

def render_particles(draw: ImageDraw.ImageDraw, width: int, height: int, p_type: str, frame_time: float, accent_col: Tuple[int, int, int]):
    """Renders flowing animated particles (bubbles, fireflies, rain, stars, snow)."""
    random.seed(42)
    count = 35

    for i in range(count):
        base_x = random.randint(0, width)
        base_y = random.randint(0, height)
        speed = random.uniform(25, 75)
        size_p = random.randint(2, 5)

        if p_type == "bubbles":
            py = int((base_y - frame_time * speed) % height)
            px = int((base_x + math.sin(frame_time * 2.0 + i) * 15) % width)
            draw.ellipse([px - size_p, py - size_p, px + size_p, py + size_p], outline=(153, 246, 228, 200), width=1)
            draw.ellipse([px - size_p + 1, py - size_p + 1, px - 1, py - 1], fill=(255, 255, 255, 180))

        elif p_type == "fireflies":
            glow = math.sin(frame_time * 3.5 + i)
            if glow > 0:
                px = int((base_x + math.sin(frame_time + i) * 20) % width)
                py = int((base_y + math.cos(frame_time + i) * 15) % height)
                draw.ellipse([px - size_p, py - size_p, px + size_p, py + size_p], fill=(*accent_col, int(glow * 220)))

        elif p_type == "rain":
            py = int((base_y + frame_time * speed * 3.0) % height)
            px = int((base_x + frame_time * speed * 0.5) % width)
            draw.line([(px, py), (px + 4, py + 16)], fill=(147, 197, 253, 180), width=1)

        elif p_type == "snow":
            py = int((base_y + frame_time * speed * 0.6) % height)
            px = int((base_x + math.sin(frame_time * 1.5 + i) * 25) % width)
            draw.ellipse([px - size_p, py - size_p, px + size_p, py + size_p], fill=(255, 255, 255, 220))

        else:
            # stars / space dust
            twinkle = abs(math.sin(frame_time * 3.0 + i))
            px = base_x
            py = base_y
            draw.ellipse([px - size_p, py - size_p, px + size_p, py + size_p], fill=(255, 255, 255, int(twinkle * 240)))


# ============================================================================
# Main Procedural Frame Renderer
# ============================================================================

def render_procedural_frame(
    width: int,
    height: int,
    entity: Dict[str, Any],
    env: Dict[str, Any],
    scene_number: int,
    total_scenes: int,
    scene_title: str,
    scene_description: str,
    narration_text: str,
    motion_type: str,
    camera_motion: str,
    frame_idx: int,
    total_frames_in_scene: int,
    fps: int = 15,
    show_subtitles: bool = True,
) -> Image.Image:
    """
    Renders a single frame of animated multi-layer procedural video.
    Integrates camera transform, parallax scenery, articulated subject sprite,
    particle systems, and Devanagari/Latin subtitle bar.
    """
    norm_t = frame_idx / max(1, total_frames_in_scene - 1)
    frame_time = frame_idx / float(fps)

    # 1. Camera Viewport Calculation
    cam_offset_x = 0.0
    cam_offset_y = 0.0
    cam_zoom = 1.0

    if camera_motion == "pan_right":
        cam_offset_x = norm_t * (width * 0.35)
    elif camera_motion == "pan_left":
        cam_offset_x = -norm_t * (width * 0.35)
    elif camera_motion == "zoom_in":
        cam_zoom = 1.0 + norm_t * 0.18
    elif camera_motion == "dramatic_zoom_out":
        cam_zoom = 1.18 - norm_t * 0.18
    elif camera_motion == "crane_up":
        cam_offset_y = -norm_t * 60
    elif camera_motion == "tracking_shot":
        cam_offset_x = norm_t * (width * 0.25)
        cam_zoom = 1.0 + math.sin(norm_t * math.pi) * 0.06

    # 2. Render Parallax Scenery
    bg = render_parallax_environment(width, height, env, cam_offset_x, cam_zoom, frame_time)
    draw = ImageDraw.Draw(bg)

    # 3. Dynamic Particle Field
    render_particles(draw, width, height, env.get("particles", "stars"), frame_time, entity.get("accent_color", (250, 204, 21)))

    # 4. Subject Choreography
    cx = width // 2
    base_ground_y = int(height * (0.64 if env.get("name") == "pond" else 0.62))

    pos_x = float(cx)
    pos_y = float(base_ground_y)
    scale_x = 1.0
    scale_y = 1.0
    rot_deg = 0.0

    if motion_type == "horizontal_travel":
        travel_range = width * 0.55
        pos_x = (cx - travel_range * 0.5) + norm_t * travel_range
        pos_y = base_ground_y - 20 + math.sin(frame_time * 3.5) * 12
        rot_deg = math.sin(frame_time * 3.5) * 4

    elif motion_type == "vertical_climb_or_launch":
        launch_progress = norm_t ** 1.6
        pos_y = base_ground_y - launch_progress * (height * 0.55)
        scale_y = 1.15
        scale_x = 0.9
        rot_deg = math.sin(frame_time * 5.0) * 3

    elif motion_type == "dynamic_bounce":
        hop_cycle = (frame_time * 4.5) % (math.pi * 2)
        h_val = math.sin(hop_cycle)
        if h_val > 0:
            pos_y = base_ground_y - h_val * 85
            scale_y = 1.0 + h_val * 0.22
            scale_x = 1.0 - h_val * 0.14
        else:
            pos_y = base_ground_y
            squash = abs(h_val)
            scale_y = 1.0 - squash * 0.20
            scale_x = 1.0 + squash * 0.18

    elif motion_type == "pirouette_spin":
        spin_phase = frame_time * 5.5
        scale_x = math.cos(spin_phase)
        scale_y = 1.05 + math.sin(frame_time * 2.5) * 0.1
        pos_y = base_ground_y - 40 + math.sin(frame_time * 2.5) * 20
        rot_deg = math.sin(frame_time * 2.0) * 8

    elif motion_type == "accelerate_zoom":
        sprint_cycle = math.sin(frame_time * 8.0) * 14
        pos_x = cx + norm_t * (width * 0.3) + sprint_cycle
        pos_y = base_ground_y - 25
        scale_x = 1.1
        rot_deg = 8.0

    else:
        # hover_and_sway / grand_parade
        pos_y = base_ground_y - 30 + math.sin(frame_time * 2.5) * 16
        rot_deg = math.sin(frame_time * 2.0) * 10
        pos_x = cx + math.sin(frame_time * 1.5) * 25

    # Ground shadow or water ripple reflection
    if env.get("name") == "pond":
        # Expanding circular water ripple rings
        for wr in range(1, 4):
            ring_r = int(((frame_time * 30 + wr * 25) % 80) * cam_zoom)
            ring_alpha = max(0, 180 - int(ring_r * 2.2))
            draw.ellipse([pos_x - ring_r * 2, base_ground_y - ring_r // 2, pos_x + ring_r * 2, base_ground_y + ring_r // 2], outline=(153, 246, 228, ring_alpha), width=2)
    else:
        shadow_w = int(140 * max(0.3, abs(scale_x)))
        shadow_h = int(28 * max(0.3, abs(scale_y)))
        draw.ellipse([pos_x - shadow_w // 2, base_ground_y - shadow_h // 2 + 10, pos_x + shadow_w // 2, base_ground_y + shadow_h // 2 + 10], fill=(5, 10, 20, 140))

    # 5. Render Animated Subject Sprite
    sprite_base_size = int(min(width, height) * 0.40 * cam_zoom)
    subject_sprite = create_subject_sprite(entity, size=sprite_base_size, frame_phase=frame_time * 4.0)

    eff_w = max(10, int(subject_sprite.width * abs(scale_x)))
    eff_h = max(10, int(subject_sprite.height * abs(scale_y)))
    transformed = subject_sprite.resize((eff_w, eff_h), Image.Resampling.BILINEAR)

    if scale_x < 0:
        transformed = transformed.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    if abs(rot_deg) > 0.5:
        transformed = transformed.rotate(rot_deg, expand=True, resample=Image.Resampling.BILINEAR)

    paste_x = int(pos_x - transformed.width // 2)
    paste_y = int(pos_y - transformed.height // 2)
    bg.paste(transformed, (paste_x, paste_y), transformed)

    # 6. Cinematic Header & Native Subtitle Overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    # Header Top Bar
    header_h = max(36, int(height * 0.054))
    ov_draw.rounded_rectangle([20, 16, width - 20, 16 + header_h], radius=10, fill=(10, 15, 30, 210), outline=(99, 102, 241, 160), width=1)
    tag_font = get_font(max(12, int(height * 0.022)), bold=True)
    header_text = f"FRAMEFLOW AI  •  SCENE {scene_number:02d}/{total_scenes:02d}  •  {scene_title.upper()}"
    ov_draw.text((35, 24), header_text, font=tag_font, fill=(244, 114, 182, 255))

    # Bottom Subtitle & Narration Bar (with Devanagari support)
    if show_subtitles:
        bar_h = max(78, int(height * 0.13))
        bar_y = height - bar_h - 20
        ov_draw.rounded_rectangle([20, bar_y, width - 20, bar_y + bar_h], radius=12, fill=(8, 12, 26, 225), outline=(147, 197, 253, 120), width=1)

        motion_font = get_font(max(10, int(height * 0.016)), bold=True)
        ov_draw.text((36, bar_y + 10), f"CHOREOGRAPHY: {motion_type.replace('_', ' ').upper()}  |  CAMERA: {camera_motion.replace('_', ' ').upper()}", font=motion_font, fill=(251, 191, 36, 255))

        sub_font = get_font(max(14, int(height * 0.024)))
        display_sub = narration_text if narration_text else scene_description

        # Word wrap text for both vertical 9:16 and landscape 16:9
        max_chars = 38 if width < height else 75
        words = display_sub.split(" ")
        lines = []
        current_line = ""
        for w in words:
            if len(current_line) + len(w) + 1 <= max_chars:
                current_line = f"{current_line} {w}".strip()
            else:
                lines.append(current_line)
                current_line = w
        if current_line:
            lines.append(current_line)

        # Draw up to 2 lines cleanly
        line_spacing = max(18, int(height * 0.028))
        for l_idx, line_str in enumerate(lines[:2]):
            ov_draw.text((36, bar_y + 32 + l_idx * line_spacing), line_str, font=sub_font, fill=(241, 245, 249, 255))

        # Scene progress micro-bar
        prog_y = bar_y + bar_h - 6
        ov_draw.rectangle([20, prog_y, width - 20, prog_y + 4], fill=(30, 41, 59, 180))
        prog_w = int((width - 40) * norm_t)
        ov_draw.rectangle([20, prog_y, 20 + prog_w, prog_y + 4], fill=(236, 72, 153, 255))

    return Image.alpha_composite(bg, overlay).convert("RGB")
