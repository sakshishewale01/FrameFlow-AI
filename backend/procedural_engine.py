"""
FrameFlow AI - Procedural 2D Multi-Layer Animation Engine.
Renders visually appropriate animated scenes with:
- Category-aware dynamic procedural sprites (vehicles, animals, humanoids, celestial, nature, architecture)
- Multi-depth parallax backgrounds (distant sky/stars/nebulae, midground silhouettes/terrain, ground physics)
- Fluid dynamic animations (squash & stretch, swimming undulation, wing flapping, thruster particle trails)
- Virtual 2D camera viewport motion (pan, tilt, push-in zoom, tracking, camera shake)
- Dynamic environmental particle systems (rain, snow, embers, bubbles, stars, fireflies)
- Cinematic overlay with scene title, choreography badge, and subtitles.
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
    """Load system font with graceful fallbacks."""
    names = ["arialbd.ttf", "segoeuib.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
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
    like wing flapping, thruster flickering, swimming undulation, wheel rotation.
    """
    sprite = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)
    cx, cy = size // 2, size // 2

    cat = entity.get("category", "humanoid")
    sub = entity.get("subtype", "character").lower()
    c_pri = entity.get("primary_color", (59, 130, 246))
    c_sec = entity.get("secondary_color", (236, 72, 153))
    c_acc = entity.get("accent_color", (250, 204, 21))

    if cat == "vehicle":
        if any(w in sub for w in ["rocket", "spaceship", "shuttle", "missile"]):
            # Aerodynamic Rocket / Spaceship
            body_w = int(size * 0.22)
            body_h = int(size * 0.52)
            top_y = cy - body_h // 2
            bot_y = cy + body_h // 2 - 25

            # Dynamic exhaust flame
            flame_len = int(size * 0.22 + math.sin(frame_phase * 6.0) * 15)
            flame_w = int(body_w * 0.7)
            flame_pts = [
                (cx - flame_w // 2, bot_y),
                (cx + flame_w // 2, bot_y),
                (cx + int(math.sin(frame_phase * 8.0) * 6), bot_y + flame_len),
            ]
            draw.polygon(flame_pts, fill=(*c_acc, 230))
            # Inner white hot flame
            inner_pts = [
                (cx - flame_w // 4, bot_y),
                (cx + flame_w // 4, bot_y),
                (cx, bot_y + int(flame_len * 0.6)),
            ]
            draw.polygon(inner_pts, fill=(255, 255, 255, 255))

            # Booster fins
            fin_pts_l = [(cx - body_w // 2, bot_y - 30), (cx - body_w, bot_y + 10), (cx - body_w // 2, bot_y)]
            fin_pts_r = [(cx + body_w // 2, bot_y - 30), (cx + body_w, bot_y + 10), (cx + body_w // 2, bot_y)]
            draw.polygon(fin_pts_l, fill=(*c_sec, 255), outline=(255, 255, 255, 220), width=2)
            draw.polygon(fin_pts_r, fill=(*c_sec, 255), outline=(255, 255, 255, 220), width=2)

            # Main fuselage
            body_rect = [cx - body_w // 2, top_y + 35, cx + body_w // 2, bot_y]
            draw.rounded_rectangle(body_rect, radius=12, fill=(*c_pri, 255), outline=(255, 255, 255, 240), width=2)
            # Nosecone
            nose_pts = [(cx - body_w // 2, top_y + 35), (cx + body_w // 2, top_y + 35), (cx, top_y)]
            draw.polygon(nose_pts, fill=(*c_sec, 255), outline=(255, 255, 255, 240), width=2)

            # Cockpit Porch / Porthole Window
            p_r = int(body_w * 0.3)
            p_y = top_y + int(body_h * 0.35)
            draw.ellipse([cx - p_r, p_y - p_r, cx + p_r, p_y + p_r], fill=(15, 23, 42, 255), outline=(*c_acc, 255), width=3)
            # Specular gleam
            draw.ellipse([cx - p_r + 3, p_y - p_r + 3, cx - p_r + 9, p_y - p_r + 9], fill=(255, 255, 255, 240))

        elif any(w in sub for w in ["car", "automobile", "sports car", "vehicle"]):
            # Sleek aerodynamic car with glowing headlights
            w_car = int(size * 0.65)
            h_car = int(size * 0.28)
            y_base = cy + 20

            # Car body
            pts = [
                (cx - w_car // 2, y_base),
                (cx - w_car // 2 + 30, y_base - h_car // 2),
                (cx - w_car // 4, y_base - h_car),
                (cx + w_car // 5, y_base - h_car),
                (cx + w_car // 2 - 20, y_base - h_car // 3),
                (cx + w_car // 2, y_base),
            ]
            draw.polygon(pts, fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

            # Windshield / Windows
            win_pts = [
                (cx - w_car // 4 + 8, y_base - h_car + 6),
                (cx + w_car // 5 - 8, y_base - h_car + 6),
                (cx + w_car // 5 + 15, y_base - h_car // 2),
                (cx - w_car // 4 - 10, y_base - h_car // 2),
            ]
            draw.polygon(win_pts, fill=(15, 23, 42, 255), outline=(*c_sec, 200), width=2)

            # Headlights beam (projecting rightwards)
            hl_x = cx + w_car // 2 - 5
            hl_y = y_base - 10
            draw.ellipse([hl_x - 6, hl_y - 6, hl_x + 6, hl_y + 6], fill=(*c_acc, 255))
            # Volumetric cone of light
            draw.polygon([(hl_x, hl_y), (size - 10, hl_y - 30), (size - 10, hl_y + 40)], fill=(*c_acc, 50))

            # Spinning Wheels
            wheel_r = int(size * 0.08)
            for wx in (cx - w_car // 3, cx + w_car // 3):
                draw.ellipse([wx - wheel_r, y_base - 5, wx + wheel_r, y_base - 5 + wheel_r * 2], fill=(20, 20, 25, 255), outline=(*c_sec, 255), width=3)
                # Spoke rotation
                ang = frame_phase * 4.0
                sx = wx + math.cos(ang) * (wheel_r * 0.7)
                sy = (y_base - 5 + wheel_r) + math.sin(ang) * (wheel_r * 0.7)
                draw.line([(wx, y_base - 5 + wheel_r), (sx, sy)], fill=(*c_acc, 255), width=2)

        elif any(w in sub for w in ["submarine", "sub"]):
            # Submersible
            w_sub = int(size * 0.55)
            h_sub = int(size * 0.3)
            draw.rounded_rectangle([cx - w_sub // 2, cy - h_sub // 2, cx + w_sub // 2, cy + h_sub // 2], radius=35, fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)
            # Conning tower
            draw.rounded_rectangle([cx - 25, cy - h_sub // 2 - 35, cx + 25, cy - h_sub // 2], radius=10, fill=(*c_sec, 255), outline=(255, 255, 255, 220), width=2)
            # Portholes
            for px in (cx - 50, cx, cx + 50):
                draw.ellipse([px - 14, cy - 14, px + 14, cy + 14], fill=(15, 23, 42, 255), outline=(*c_acc, 255), width=2)
                draw.ellipse([px - 5, cy - 5, px + 2, cy + 2], fill=(*c_acc, 180))
            # Propeller
            prop_x = cx - w_sub // 2 - 8
            prop_ang = frame_phase * 7.0
            p_top = (prop_x, cy + math.sin(prop_ang) * 22)
            p_bot = (prop_x, cy - math.sin(prop_ang) * 22)
            draw.line([p_top, p_bot], fill=(*c_acc, 255), width=4)
        else:
            # Generic aircraft / drone / flyer
            draw.ellipse([cx - size * 0.3, cy - size * 0.15, cx + size * 0.3, cy + size * 0.15], fill=(*c_pri, 255), outline=(255, 255, 255), width=2)
            draw.ellipse([cx - 20, cy - 10, cx + 20, cy + 10], fill=(*c_acc, 255))

    elif cat == "animal":
        if any(w in sub for w in ["bird", "eagle", "hawk", "falcon", "crow"]):
            # Majestic soaring bird with animated flapping wings
            wing_flap = math.sin(frame_phase * 4.5) * (size * 0.22)
            # Torso & Head
            draw.ellipse([cx - 22, cy - 35, cx + 22, cy + 45], fill=(*c_pri, 255), outline=(255, 255, 255, 200), width=2)
            # Head & Beak
            draw.ellipse([cx - 16, cy - 55, cx + 16, cy - 25], fill=(*c_sec, 255))
            draw.polygon([(cx + 10, cy - 42), (cx + 32, cy - 38), (cx + 10, cy - 34)], fill=(*c_acc, 255))
            # Left wing
            pts_lw = [(cx - 15, cy - 10), (cx - int(size * 0.38), cy - 25 + wing_flap), (cx - int(size * 0.22), cy + 20)]
            draw.polygon(pts_lw, fill=(*c_pri, 255), outline=(*c_sec, 255), width=2)
            # Right wing
            pts_rw = [(cx + 15, cy - 10), (cx + int(size * 0.38), cy - 25 + wing_flap), (cx + int(size * 0.22), cy + 20)]
            draw.polygon(pts_rw, fill=(*c_pri, 255), outline=(*c_sec, 255), width=2)
            # Eye
            draw.ellipse([cx + 4, cy - 44, cx + 8, cy - 40], fill=(255, 255, 255, 255))

        elif any(w in sub for w in ["dolphin", "whale", "fish", "shark"]):
            # Undulating marine animal with caudal fin
            swim_curve = math.sin(frame_phase * 4.0) * 16
            # Body ellipse
            draw.ellipse([cx - size * 0.32, cy - size * 0.16 + swim_curve * 0.3, cx + size * 0.25, cy + size * 0.16 + swim_curve * 0.3], fill=(*c_pri, 255), outline=(*c_sec, 255), width=2)
            # Dorsal fin
            draw.polygon([(cx - 20, cy - size * 0.15), (cx - 5, cy - size * 0.28), (cx + 25, cy - size * 0.15)], fill=(*c_sec, 255))
            # Fluke / Tail
            tail_x = cx - size * 0.32
            tail_y = cy + swim_curve
            draw.polygon([(tail_x, tail_y), (tail_x - 35, tail_y - 25), (tail_x - 20, tail_y), (tail_x - 35, tail_y + 25)], fill=(*c_acc, 255))
            # Eye
            draw.ellipse([cx + size * 0.15, cy - 10, cx + size * 0.15 + 7, cy - 3], fill=(255, 255, 255, 255))

        elif any(w in sub for w in ["dragon"]):
            # Mythical winged dragon
            wing_f = math.sin(frame_phase * 3.5) * (size * 0.2)
            # Dragon Body
            draw.ellipse([cx - 30, cy - 40, cx + 30, cy + 50], fill=(*c_pri, 255), outline=(*c_acc, 255), width=2)
            # Dragon Head & Horns
            draw.ellipse([cx - 22, cy - 65, cx + 25, cy - 25], fill=(*c_pri, 255))
            draw.polygon([(cx - 15, cy - 60), (cx - 32, cy - 85), (cx - 5, cy - 65)], fill=(*c_acc, 255))
            draw.polygon([(cx + 5, cy - 65), (cx + 25, cy - 85), (cx + 15, cy - 60)], fill=(*c_acc, 255))
            # Huge bat wings
            draw.polygon([(cx - 20, cy - 15), (cx - int(size * 0.42), cy - 40 + wing_f), (cx - int(size * 0.2), cy + 30)], fill=(*c_sec, 240), outline=(*c_acc, 255), width=2)
            draw.polygon([(cx + 20, cy - 15), (cx + int(size * 0.42), cy - 40 + wing_f), (cx + int(size * 0.2), cy + 30)], fill=(*c_sec, 240), outline=(*c_acc, 255), width=2)
            # Glowing eye
            draw.ellipse([cx + 5, cy - 50, cx + 12, cy - 43], fill=(*c_acc, 255))

        else:
            # Quadruped / Cat / Dog / Creature
            r_body = int(size * 0.25)
            draw.ellipse([cx - r_body, cy - r_body // 2, cx + r_body, cy + r_body], fill=(*c_pri, 255), outline=(*c_sec, 255), width=2)
            # Head
            draw.ellipse([cx + r_body // 3, cy - r_body + 10, cx + r_body + 20, cy], fill=(*c_sec, 255))
            # Ears
            draw.polygon([(cx + r_body // 2, cy - r_body + 15), (cx + r_body // 2 + 10, cy - r_body - 15), (cx + r_body // 2 + 25, cy - r_body + 15)], fill=(*c_acc, 255))
            # Tail
            tail_wag = math.sin(frame_phase * 5.0) * 15
            draw.arc([cx - r_body - 20, cy - 20, cx - r_body + 20, cy + 20 + tail_wag], start=90, end=270, fill=(*c_sec, 255), width=4)

    elif cat == "humanoid":
        # Articulated astronaut / explorer / hero
        stride = math.sin(frame_phase * 4.0) * 15
        # Torso
        torso_w = int(size * 0.22)
        torso_h = int(size * 0.32)
        draw.rounded_rectangle([cx - torso_w // 2, cy - torso_h // 2, cx + torso_w // 2, cy + torso_h // 2], radius=14, fill=(*c_pri, 255), outline=(255, 255, 255, 220), width=2)

        # Helmet / Visor
        helm_r = int(size * 0.16)
        helm_y = cy - torso_h // 2 - helm_r + 10
        draw.ellipse([cx - helm_r, helm_y - helm_r, cx + helm_r, helm_y + helm_r], fill=(*c_sec, 255), outline=(255, 255, 255), width=2)
        # Gold Reflective Visor
        v_w = int(helm_r * 0.75)
        v_h = int(helm_r * 0.55)
        draw.rounded_rectangle([cx - v_w, helm_y - v_h + 3, cx + v_w, helm_y + v_h], radius=10, fill=(15, 23, 42, 255), outline=(*c_acc, 255), width=2)
        # Specular glint
        draw.ellipse([cx - v_w + 4, helm_y - v_h + 5, cx - v_w + 12, helm_y - v_h + 12], fill=(255, 255, 255, 240))

        # Legs (walking / floating)
        draw.line([(cx - 18, cy + torso_h // 2), (cx - 18 - stride, cy + torso_h // 2 + 45)], fill=(*c_pri, 255), width=7)
        draw.line([(cx + 18, cy + torso_h // 2), (cx + 18 + stride, cy + torso_h // 2 + 45)], fill=(*c_pri, 255), width=7)

        # Arms
        draw.line([(cx - torso_w // 2, cy - 10), (cx - torso_w // 2 - 20, cy + 20 + stride)], fill=(*c_sec, 255), width=6)
        draw.line([(cx + torso_w // 2, cy - 10), (cx + torso_w // 2 + 20, cy + 20 - stride)], fill=(*c_sec, 255), width=6)

    elif cat == "celestial":
        # Radiant pulsing star / comet
        pulse_r = int(size * 0.25 + math.sin(frame_phase * 3.0) * 12)
        # Corona rays
        for a in range(0, 360, 30):
            rad = math.radians(a + frame_phase * 20.0)
            ray_len = pulse_r + 35 + (20 if a % 60 == 0 else 0)
            rx = cx + math.cos(rad) * ray_len
            ry = cy + math.sin(rad) * ray_len
            draw.line([(cx, cy), (rx, ry)], fill=(*c_acc, 180), width=3)
        # Core
        draw.ellipse([cx - pulse_r, cy - pulse_r, cx + pulse_r, cy + pulse_r], fill=(*c_pri, 255), outline=(255, 255, 255), width=3)
        draw.ellipse([cx - pulse_r // 2, cy - pulse_r // 2, cx + pulse_r // 2, cy + pulse_r // 2], fill=(255, 255, 255, 255))

    else:
        # Nature Object / Crystal / Architecture
        r = int(size * 0.28)
        # Faceted crystal or natural bloom
        pts_poly = []
        for i in range(6):
            ang = math.radians(i * 60 + frame_phase * 5.0)
            pts_poly.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        draw.polygon(pts_poly, fill=(*c_pri, 255), outline=(*c_acc, 255), width=3)
        # Inner facet
        inner_pts = []
        for i in range(6):
            ang = math.radians(i * 60 + frame_phase * 5.0)
            inner_pts.append((cx + math.cos(ang) * (r * 0.5), cy + math.sin(ang) * (r * 0.5)))
        draw.polygon(inner_pts, fill=(*c_sec, 220), outline=(255, 255, 255), width=2)

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
    - Layer 2 (Distant terrain / skyline): 0.35x parallax
    - Layer 3 (Ground / Water / Road): 1.0x parallax
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

    # 2. Celestial / Environmental Features (Layer 1 - deep background)
    p_offset_1 = int(camera_offset_x * 0.1)

    if env_name == "space":
        # Orbiting planet with rings
        planet_x = int((width * 0.75 - p_offset_1) % (width + 200)) - 100
        planet_y = int(height * 0.28)
        p_rad = int(height * 0.12)
        draw.ellipse([planet_x - p_rad, planet_y - p_rad, planet_x + p_rad, planet_y + p_rad], fill=(168, 85, 247, 240), outline=(216, 180, 254, 255), width=2)
        # Ring
        draw.ellipse([planet_x - int(p_rad * 1.8), planet_y - int(p_rad * 0.35), planet_x + int(p_rad * 1.8), planet_y + int(p_rad * 0.35)], outline=(244, 114, 182, 180), width=4)

    elif env_name in ["sky", "sunset"]:
        # Golden sun
        sun_x = int((width * 0.7 - p_offset_1) % width)
        sun_y = int(height * 0.42)
        draw.ellipse([sun_x - 55, sun_y - 55, sun_x + 55, sun_y + 55], fill=(255, 230, 100, 220))
        draw.ellipse([sun_x - 85, sun_y - 85, sun_x + 85, sun_y + 85], fill=(255, 200, 80, 60))

    # 3. Layer 2: Distant Silhouettes / Mountains / City Skyline (0.35x parallax)
    p_offset_2 = int(camera_offset_x * 0.35)

    if env_name == "cyberpunk":
        # High tech skyscraper silhouette with illuminated windows
        building_w = 48
        for b_idx in range(-2, width // building_w + 3):
            bx = b_idx * building_w - (p_offset_2 % building_w)
            bh = int(120 + ((b_idx * 37) % 180))
            draw.rectangle([bx, horizon_y - bh, bx + building_w - 4, horizon_y], fill=(20, 16, 38, 255), outline=(56, 189, 248, 80))
            # Neon windows
            for wy in range(horizon_y - bh + 12, horizon_y - 10, 18):
                if (b_idx + wy) % 3 == 0:
                    draw.rectangle([bx + 8, wy, bx + 16, wy + 8], fill=(236, 72, 153, 200))
                elif (b_idx + wy) % 5 == 0:
                    draw.rectangle([bx + 24, wy, bx + 32, wy + 8], fill=(56, 189, 248, 200))
    else:
        # Rolling hills / mountains
        step = 6
        prev_pt = None
        pts = [(0, horizon_y)]
        for x in range(0, width + step, step):
            world_x = x + p_offset_2
            m_h = math.sin(world_x * 0.003) * 60 + math.cos(world_x * 0.008) * 30
            y = int(horizon_y - 45 + m_h)
            pts.append((x, y))
        pts.append((width, horizon_y))
        draw.polygon(pts, fill=(horizon_c[0], horizon_c[1], horizon_c[2], 255))

    # 4. Layer 3: Ground / Sea Surface / Road (1.0x parallax)
    p_offset_3 = int(camera_offset_x * 1.0)
    ground_type = env.get("ground_type", "surface")

    for y in range(horizon_y, height):
        factor = (y - horizon_y) / max(1, height - horizon_y)
        if ground_type == "seabed":
            # Deep sea floor with gentle waves
            wave = math.sin(y * 0.08 + frame_time * 3.0) * (3 * factor)
            draw.line([(0, y), (width, y)], fill=(int(10 + factor * 20), int(30 + factor * 40 + wave), int(60 + factor * 60), 255))
        elif ground_type == "road":
            # Futuristic cyber road with perspective lanes
            draw.line([(0, y), (width, y)], fill=(int(15 + factor * 15), int(15 + factor * 15), int(25 + factor * 25), 255))
        else:
            # Solid terrain
            draw.line([(0, y), (width, y)], fill=(int(c_bot[0] * (0.8 + factor * 0.4)), int(c_bot[1] * (0.8 + factor * 0.4)), int(c_bot[2] * (0.8 + factor * 0.4)), 255))

    # Perspective road lines or wave crests
    if ground_type == "road":
        # Dashed center line moving with frame_time
        dash_y_start = horizon_y
        for d in range(12):
            t_dash = ((d / 12.0) + frame_time * 1.5) % 1.0
            dy = int(dash_y_start + t_dash * (height - dash_y_start))
            dw = int(4 + t_dash * 16)
            dh = int(6 + t_dash * 20)
            draw.rectangle([width // 2 - dw // 2, dy, width // 2 + dw // 2, dy + dh], fill=(250, 204, 21, 230))
    elif ground_type == "seabed":
        # Swaying bioluminescent coral on seabed
        for cx_i in range(0, width, 140):
            bx = (cx_i - p_offset_3) % width
            sway = math.sin(frame_time * 2.5 + cx_i) * 12
            draw.line([(bx, height), (bx + sway, height - 55)], fill=(56, 189, 248, 160), width=3)
            draw.ellipse([bx + sway - 5, height - 60, bx + sway + 5, height - 50], fill=(244, 114, 182, 220))

    return bg


# ============================================================================
# Dynamic Environmental Particles
# ============================================================================

def render_particles(draw: ImageDraw.ImageDraw, width: int, height: int, particle_type: str, frame_time: float, accent_col: Tuple[int, int, int]):
    """Renders animated atmospheric particle field (rain, bubbles, embers, stars, snow)."""
    random.seed(99)  # Deterministic particle seed
    count = 45 if particle_type in ["rain", "stars"] else 30

    for i in range(count):
        bx = random.randint(0, width)
        by = random.randint(0, height)
        speed = random.uniform(30, 90)

        if particle_type == "rain":
            py = int((by + frame_time * speed * 4.5) % height)
            px = int((bx - frame_time * speed * 1.2) % width)
            draw.line([(px, py), (px - 6, py + 18)], fill=(147, 197, 253, 140), width=1)

        elif particle_type == "snow":
            py = int((by + frame_time * speed * 0.8) % height)
            px = int((bx + math.sin(frame_time * 2.0 + i) * 20) % width)
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255, 180))

        elif particle_type == "bubbles":
            py = int((by - frame_time * speed * 1.2) % height)
            px = int((bx + math.sin(frame_time * 2.5 + i) * 15) % width)
            r = int(2 + (i % 4) * 2)
            draw.ellipse([px - r, py - r, px + r, py + r], outline=(147, 197, 253, 180), width=1)
            draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255, 120))

        elif particle_type == "embers":
            py = int((by - frame_time * speed * 1.5) % height)
            px = int((bx + math.sin(frame_time * 3.0 + i) * 25) % width)
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(249, 115, 22, 220))

        else:
            # Twinkling stars / fireflies
            px = int((bx + math.sin(frame_time * 1.2 + i) * 10) % width)
            py = int((by + math.cos(frame_time * 0.9 + i) * 10) % height)
            alpha = int(120 + math.sin(frame_time * 4.0 + i) * 100)
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(*accent_col, alpha))


# ============================================================================
# Complete Frame Compositor
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
) -> Image.Image:
    """
    Renders an animated HD video frame incorporating:
    - Multi-depth parallax backgrounds
    - 2D camera viewport transform (pan, tilt, zoom, tracking)
    - Dynamic subject transformation, physical squash/stretch, and secondary animation
    - Particle fields (bubbles, rain, embers, stars)
    - Professional cinematic overlay and subtitles.
    """
    frame_time = frame_idx / fps
    norm_t = frame_idx / max(1, total_frames_in_scene)

    # 1. Compute Camera Motion Parameters
    cam_offset_x = 0.0
    cam_zoom = 1.0
    cam_offset_y = 0.0

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
    base_ground_y = int(height * 0.62)

    pos_x = float(cx)
    pos_y = float(base_ground_y)
    scale_x = 1.0
    scale_y = 1.0
    rot_deg = 0.0

    if motion_type == "horizontal_travel":
        # Smooth forward travel across camera
        travel_range = width * 0.55
        pos_x = (cx - travel_range * 0.5) + norm_t * travel_range
        pos_y = base_ground_y - 20 + math.sin(frame_time * 3.5) * 12
        rot_deg = math.sin(frame_time * 3.5) * 4

    elif motion_type == "vertical_climb_or_launch":
        # Launching upwards with acceleration and aerodynamic stretch
        launch_progress = norm_t ** 1.6
        pos_y = base_ground_y - launch_progress * (height * 0.6)
        scale_y = 1.15
        scale_x = 0.9
        rot_deg = math.sin(frame_time * 5.0) * 3

    elif motion_type == "dynamic_bounce":
        # Classical squash and stretch bounce
        hop_cycle = (frame_time * 4.0) % (math.pi * 2)
        h_val = math.sin(hop_cycle)
        if h_val > 0:
            pos_y = base_ground_y - h_val * 85
            scale_y = 1.0 + h_val * 0.25
            scale_x = 1.0 - h_val * 0.15
        else:
            pos_y = base_ground_y
            squash = abs(h_val)
            scale_y = 1.0 - squash * 0.22
            scale_x = 1.0 + squash * 0.2

    elif motion_type == "pirouette_spin":
        # 360-degree rotation & floating acrobatics
        spin_phase = frame_time * 5.5
        scale_x = math.cos(spin_phase)
        scale_y = 1.05 + math.sin(frame_time * 2.5) * 0.1
        pos_y = base_ground_y - 40 + math.sin(frame_time * 2.5) * 20
        rot_deg = math.sin(frame_time * 2.0) * 8

    elif motion_type == "accelerate_zoom":
        # High-speed sprint or warp thrust
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

    # Contact shadow on ground
    shadow_w = int(140 * max(0.3, abs(scale_x)))
    shadow_h = int(28 * max(0.3, abs(scale_y)))
    draw.ellipse([pos_x - shadow_w // 2, base_ground_y - shadow_h // 2 + 10, pos_x + shadow_w // 2, base_ground_y + shadow_h // 2 + 10], fill=(5, 10, 20, 140))

    # 5. Render Dynamic Animated Subject Sprite
    sprite_base_size = int(min(width, height) * 0.38 * cam_zoom)
    subject_sprite = create_subject_sprite(entity, size=sprite_base_size, frame_phase=frame_time * 4.0)

    # Apply transform
    eff_w = max(10, int(subject_sprite.width * abs(scale_x)))
    eff_h = max(10, int(subject_sprite.height * abs(scale_y)))
    transformed = subject_sprite.resize((eff_w, eff_h), Image.Resampling.BILINEAR)

    if scale_x < 0:
        transformed = transformed.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    if abs(rot_deg) > 0.5:
        transformed = transformed.rotate(rot_deg, expand=True, resample=Image.Resampling.BILINEAR)

    # Composite Sprite
    paste_x = int(pos_x - transformed.width // 2)
    paste_y = int(pos_y - transformed.height // 2)
    bg.paste(transformed, (paste_x, paste_y), transformed)

    # 6. Cinematic Header & Subtitle Overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    # Header Top Bar
    header_h = max(34, int(height * 0.052))
    ov_draw.rounded_rectangle([20, 16, width - 20, 16 + header_h], radius=10, fill=(10, 15, 30, 205), outline=(99, 102, 241, 150), width=1)
    tag_font = get_font(max(11, int(height * 0.02)), bold=True)
    ov_draw.text((35, 24), f"FRAMEFLOW AI  •  SCENE {scene_number:02d}/{total_scenes:02d}  •  {scene_title.upper()}", font=tag_font, fill=(244, 114, 182, 255))

    # Engine badge (top-right)
    engine_badge = "PROCEDURAL 2D ENGINE"
    ov_draw.text((width - 240, 24), engine_badge, font=tag_font, fill=(56, 189, 248, 255))

    # Bottom Subtitle & Narration Bar
    bar_h = max(70, int(height * 0.12))
    bar_y = height - bar_h - 20
    ov_draw.rounded_rectangle([20, bar_y, width - 20, bar_y + bar_h], radius=12, fill=(8, 12, 26, 220), outline=(147, 197, 253, 110), width=1)

    motion_font = get_font(max(10, int(height * 0.016)), bold=True)
    ov_draw.text((36, bar_y + 10), f"CHOREOGRAPHY: {motion_type.replace('_', ' ').upper()}  |  CAMERA: {camera_motion.replace('_', ' ').upper()}", font=motion_font, fill=(251, 191, 36, 255))

    sub_font = get_font(max(13, int(height * 0.022)))
    display_sub = narration_text if narration_text else scene_description
    ov_draw.text((36, bar_y + 30), display_sub[:120], font=sub_font, fill=(241, 245, 249, 255))

    # Scene progress micro-bar
    prog_y = bar_y + bar_h - 6
    ov_draw.rectangle([20, prog_y, width - 20, prog_y + 4], fill=(30, 41, 59, 180))
    prog_w = int((width - 40) * norm_t)
    ov_draw.rectangle([20, prog_y, 20 + prog_w, prog_y + 4], fill=(236, 72, 153, 255))

    return Image.alpha_composite(bg, overlay).convert("RGB")
