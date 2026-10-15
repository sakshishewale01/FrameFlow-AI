import math
import os
import random
from typing import Dict, List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Resolutions
RESOLUTIONS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (1080, 1080),
}


def get_font(size: int, bold: bool = False):
    try:
        name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(name, size)
    except Exception:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()


def parse_prompt_entities(prompt: str) -> dict:
    """Analyze the prompt to extract character traits, colors, setting, and actions."""
    p = prompt.lower()

    # Detect character theme
    if "lotus" in p or "flower" in p or "blossom" in p:
        character_type = "lotus"
        primary_color = (255, 120, 180)  # Pink
        secondary_color = (255, 200, 230)
        accent_color = (255, 230, 90)     # Golden center
    elif "robot" in p or "bot" in p or "droid" in p:
        character_type = "robot"
        primary_color = (96, 165, 250)   # Blue metal
        secondary_color = (191, 219, 254)
        accent_color = (52, 211, 153)    # Glowing green
    elif "cat" in p or "kitten" in p:
        character_type = "cat"
        primary_color = (251, 146, 60)   # Calico ginger
        secondary_color = (254, 215, 170)
        accent_color = (239, 68, 68)     # Red collar
    elif "star" in p or "constellation" in p:
        character_type = "star"
        primary_color = (250, 204, 21)   # Bright star yellow
        secondary_color = (254, 240, 138)
        accent_color = (244, 114, 182)   # Rosy glow
    else:
        # Default cute creature
        character_type = "creature"
        primary_color = (244, 114, 182)  # Vibrant pink
        secondary_color = (251, 207, 232)
        accent_color = (250, 204, 21)

    # Detect setting
    if "pond" in p or "water" in p or "lake" in p or "ocean" in p or "river" in p:
        setting = "pond"
    elif "forest" in p or "woods" in p or "garden" in p:
        setting = "forest"
    elif "space" in p or "galaxy" in p or "stars" in p:
        setting = "space"
    else:
        setting = "magical"

    return {
        "character_type": character_type,
        "setting": setting,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "accent_color": accent_color,
    }


def create_character_sprite(entities: dict, size: int = 360) -> Image.Image:
    """
    Renders an expressive, high-detail character sprite on a transparent RGBA canvas.
    This sprite is reused across all scenes to ensure consistent character identity.
    """
    sprite = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)
    cx, cy = size // 2, size // 2

    char_type = entities["character_type"]
    c_primary = entities["primary_color"]
    c_sec = entities["secondary_color"]
    c_accent = entities["accent_color"]

    if char_type == "lotus":
        # Draw layered lotus petals
        # Outer darker petals
        for angle in (-55, -35, -15, 15, 35, 55):
            rad = math.radians(angle)
            px = cx + math.sin(rad) * (size * 0.28)
            py = cy - math.cos(rad) * (size * 0.28)
            petal_w = int(size * 0.16)
            petal_h = int(size * 0.32)
            draw.ellipse(
                [px - petal_w, py - petal_h, px + petal_w, py + petal_h],
                fill=(*c_primary, 230),
                outline=(*c_sec, 255),
                width=2,
            )

        # Inner vibrant petals
        for angle in (-40, -20, 0, 20, 40):
            rad = math.radians(angle)
            px = cx + math.sin(rad) * (size * 0.22)
            py = cy - math.cos(rad) * (size * 0.22) + 10
            petal_w = int(size * 0.14)
            petal_h = int(size * 0.28)
            draw.ellipse(
                [px - petal_w, py - petal_h, px + petal_w, py + petal_h],
                fill=(*c_sec, 245),
                outline=(255, 255, 255, 255),
                width=2,
            )

        # Core flower pod
        pod_r = int(size * 0.18)
        draw.ellipse([cx - pod_r, cy - pod_r + 15, cx + pod_r, cy + pod_r + 15], fill=(*c_accent, 255))
        # Golden stamens
        for a in range(0, 360, 36):
            rad = math.radians(a)
            sx = cx + math.cos(rad) * (pod_r * 0.65)
            sy = (cy + 15) + math.sin(rad) * (pod_r * 0.65)
            draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(234, 179, 8, 255))

    elif char_type == "robot":
        # Robotic head/body
        bw, bh = int(size * 0.44), int(size * 0.42)
        draw.rounded_rectangle([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2], radius=24, fill=(*c_primary, 255), outline=(255, 255, 255), width=3)
        # Antenna
        draw.line([(cx, cy - bh // 2), (cx, cy - bh // 2 - 35)], fill=(203, 213, 225), width=4)
        draw.ellipse([cx - 10, cy - bh // 2 - 45, cx + 10, cy - bh // 2 - 25], fill=(*c_accent, 255))
        # Visor
        draw.rounded_rectangle([cx - bw // 2 + 15, cy - 25, cx + bw // 2 - 15, cy + 25], radius=12, fill=(15, 23, 42, 255), outline=(*c_sec, 200), width=2)

    else:
        # Round cuddly fantasy creature
        cr = int(size * 0.32)
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(*c_primary, 255), outline=(*c_sec, 255), width=3)
        # Cute ears
        draw.polygon([(cx - cr + 10, cy - cr + 25), (cx - cr - 20, cy - cr - 40), (cx - cr + 55, cy - cr)], fill=(*c_primary, 255))
        draw.polygon([(cx + cr - 10, cy - cr + 25), (cx + cr + 20, cy - cr - 40), (cx + cr - 55, cy - cr)], fill=(*c_primary, 255))

    # Expressive Kawaii Eyes
    eye_offset_x = int(size * 0.08)
    eye_y = cy + (12 if char_type == "lotus" else -5)
    eye_w, eye_h = int(size * 0.04), int(size * 0.065)

    # Left eye
    draw.ellipse([cx - eye_offset_x - eye_w, eye_y - eye_h, cx - eye_offset_x + eye_w, eye_y + eye_h], fill=(20, 20, 35, 255))
    # Right eye
    draw.ellipse([cx + eye_offset_x - eye_w, eye_y - eye_h, cx + eye_offset_x + eye_w, eye_y + eye_h], fill=(20, 20, 35, 255))

    # Catchlights (Sparkles in eyes)
    draw.ellipse([cx - eye_offset_x - eye_w + 3, eye_y - eye_h + 3, cx - eye_offset_x, eye_y - eye_h + 9], fill=(255, 255, 255, 255))
    draw.ellipse([cx + eye_offset_x - eye_w + 3, eye_y - eye_h + 3, cx + eye_offset_x, eye_y - eye_h + 9], fill=(255, 255, 255, 255))

    # Rosy Cheeks
    cheek_offset_x = int(size * 0.16)
    cheek_y = eye_y + 16
    draw.ellipse([cx - cheek_offset_x - 12, cheek_y - 6, cx - cheek_offset_x + 12, cheek_y + 6], fill=(251, 113, 133, 180))
    draw.ellipse([cx + cheek_offset_x - 12, cheek_y - 6, cx + cheek_offset_x + 12, cheek_y + 6], fill=(251, 113, 133, 180))

    # Happy Mouth
    draw.arc([cx - 14, eye_y + 6, cx + 14, eye_y + 24], start=10, end=170, fill=(159, 18, 57, 255), width=3)

    return sprite


def render_environment_layer(width: int, height: int, setting: str, frame_time: float) -> Image.Image:
    """Render animated multi-depth environment with water waves, reflections, and glow."""
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(bg)

    # Sky / Upper ambience
    top_color = (8, 12, 32)
    horizon_color = (24, 38, 75)
    for y in range(int(height * 0.55)):
        factor = y / (height * 0.55)
        r = int(top_color[0] * (1 - factor) + horizon_color[0] * factor)
        g = int(top_color[1] * (1 - factor) + horizon_color[1] * factor)
        b = int(top_color[2] * (1 - factor) + horizon_color[2] * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Distant glowing twilight hills / mist
    for i in range(width):
        h1 = int(height * 0.48 + math.sin(i * 0.005 + 1.2) * 25)
        draw.line([(i, h1), (i, int(height * 0.55))], fill=(30, 45, 85, 255))

    # Water surface / Lake / Pond
    water_horizon = int(height * 0.55)
    for y in range(water_horizon, height):
        wave_factor = (y - water_horizon) / (height - water_horizon)
        # Sinusoidal water wave motion over time
        wave_motion = math.sin(y * 0.06 + frame_time * 3.5) * (4 * wave_factor)
        r = int(12 + wave_factor * 10)
        g = int(32 + wave_factor * 25 + wave_motion * 2)
        b = int(68 + wave_factor * 45 + wave_motion * 3)
        draw.line([(0, y), (width, y)], fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Floating water lily pads that bob up and down with water physics
    pad_y = int(height * 0.72)
    for px, scale in [(int(width * 0.2), 0.7), (int(width * 0.8), 0.85), (int(width * 0.5), 1.1)]:
        bob = math.sin(frame_time * 2.5 + px) * 5
        pad_w = int(130 * scale)
        pad_h = int(38 * scale)
        py = int(pad_y + bob)
        # Shadow of pad
        draw.ellipse([px - pad_w, py - pad_h // 2 + 6, px + pad_w, py + pad_h // 2 + 8], fill=(5, 18, 38, 160))
        # Lily pad green
        draw.ellipse([px - pad_w, py - pad_h // 2, px + pad_w, py + pad_h // 2], fill=(16, 120, 80, 240), outline=(52, 211, 153, 200), width=2)
        # Notch in pad
        draw.polygon([(px, py), (px + pad_w // 2, py - pad_h // 2), (px + pad_w // 3, py)], fill=(8, 28, 55, 255))

    return bg


def render_animated_frame(
    width: int,
    height: int,
    character_sprite: Image.Image,
    entities: dict,
    scene_number: int,
    total_scenes: int,
    scene_title: str,
    scene_description: str,
    motion_type: str,
    frame_idx: int,
    total_frames_in_scene: int,
    fps: int = 15,
) -> Image.Image:
    """
    Renders an animated frame incorporating true 2D character choreography:
    - Rhythmic hopping, squash & stretch
    - Dancing pendulum tilts and swaying
    - 360-degree pirouette rotation transforms
    - Dynamic water ripples & ground impact shadows
    - Rising animated magical particles/fireflies
    """
    frame_time = frame_idx / fps
    scene_progress = frame_idx / max(1, total_frames_in_scene)

    # 1. Base Environment
    frame = render_environment_layer(width, height, entities["setting"], frame_time)
    draw = ImageDraw.Draw(frame)

    # 2. Magical Floating Fireflies / Ambient Lights
    random.seed(42)  # Stable particle field
    for p_i in range(35):
        base_x = random.randint(0, width)
        base_y = random.randint(0, height)
        speed = random.uniform(25, 60)
        p_x = int((base_x + math.sin(frame_time * 1.5 + p_i) * 35) % width)
        p_y = int((base_y - frame_time * speed) % height)
        glow_r = int(3 + math.sin(frame_time * 3 + p_i) * 2)
        p_alpha = int(140 + math.sin(frame_time * 4 + p_i) * 90)
        draw.ellipse([p_x - glow_r * 2, p_y - glow_r * 2, p_x + glow_r * 2, p_y + glow_r * 2], fill=(*entities["accent_color"], p_alpha // 3))
        draw.ellipse([p_x - glow_r, p_y - glow_r, p_x + glow_r, p_y + glow_r], fill=(255, 255, 255, p_alpha))

    # 3. Compute Character Dance Choreography based on motion_type
    center_x = width // 2
    base_ground_y = int(height * 0.72)

    # Default parameters
    scale_x = 1.0
    scale_y = 1.0
    rotation_deg = 0.0
    pos_x = center_x
    pos_y = base_ground_y
    ripple_intensity = 0.0

    if motion_type == "sway_and_bob":
        # Scene 1: Waking up, swaying side to side, gentle floating bob
        bob = math.sin(frame_time * 3.0) * 14
        sway = math.sin(frame_time * 2.5) * 15
        pos_y = base_ground_y + bob
        rotation_deg = sway
        scale_x = 1.0 + math.sin(frame_time * 3.0) * 0.05
        scale_y = 1.0 - math.sin(frame_time * 3.0) * 0.05
        ripple_intensity = (1.0 + math.sin(frame_time * 3.0)) * 0.5

    elif motion_type == "bounce_and_hop":
        # Scene 2: High energetic rhythmic bouncing with squash & stretch
        hop_cycle = (frame_time * 3.8) % (math.pi * 2)
        jump_norm = math.sin(hop_cycle)

        if jump_norm > 0:
            # In the air
            jump_height = jump_norm * 90
            pos_y = base_ground_y - jump_height
            # Stretch vertically in flight
            scale_y = 1.0 + jump_norm * 0.28
            scale_x = 1.0 - jump_norm * 0.18
            rotation_deg = math.sin(frame_time * 3.8) * 18
            ripple_intensity = 0.2
        else:
            # Landing impact: squash!
            pos_y = base_ground_y
            squash = abs(jump_norm)
            scale_y = 1.0 - squash * 0.26
            scale_x = 1.0 + squash * 0.24
            rotation_deg = 0
            ripple_intensity = 1.0

        # Subtle horizontal groove drift
        pos_x = center_x + math.sin(frame_time * 1.9) * 45

    elif motion_type == "pirouette_spin":
        # Scene 3: Elegant 360-degree dance pirouette & float
        spin_phase = frame_time * 6.5
        # Perspective horizontal flip/spin
        scale_x = math.cos(spin_phase)
        scale_y = 1.05 + math.sin(frame_time * 3.0) * 0.15
        pos_y = base_ground_y - 45 + math.sin(frame_time * 3.0) * 25
        rotation_deg = math.sin(frame_time * 2.0) * 8
        ripple_intensity = 0.6

        # Centrifugal dance sparkles thrown outward
        for sp_i in range(8):
            sp_rad = spin_phase + sp_i * (math.pi / 4)
            sp_dist = 65 + math.sin(frame_time * 4 + sp_i) * 35
            sp_x = int(pos_x + math.cos(sp_rad) * sp_dist)
            sp_y = int(pos_y + math.sin(sp_rad) * (sp_dist * 0.5))
            draw.ellipse([sp_x - 4, sp_y - 4, sp_x + 4, sp_y + 4], fill=(255, 240, 140, 240))

    else:
        # Scene 4/5: Grand Finale Celebration
        shimmy = math.sin(frame_time * 12.0) * 12
        leap = abs(math.sin(frame_time * 4.5)) * 65
        pos_y = base_ground_y - leap
        pos_x = center_x + shimmy
        rotation_deg = math.sin(frame_time * 6.0) * 16
        scale_y = 1.0 + (leap / 65) * 0.22 - (1.0 - leap / 65) * 0.15
        scale_x = 1.0 - (leap / 65) * 0.15 + (1.0 - leap / 65) * 0.2
        ripple_intensity = 0.9 if leap < 15 else 0.3

    # 4. Animated Contact Shadow and Water Ripples beneath Character
    shadow_w = int(140 * max(0.4, scale_x) * (1.0 - (base_ground_y - pos_y) * 0.004))
    shadow_h = int(32 * (1.0 - (base_ground_y - pos_y) * 0.004))
    draw.ellipse(
        [center_x - shadow_w // 2, base_ground_y - shadow_h // 2, center_x + shadow_w // 2, base_ground_y + shadow_h // 2],
        fill=(5, 15, 30, 160),
    )

    # Expanding water ripple rings
    if ripple_intensity > 0.2:
        for ring in (1, 2):
            ring_r = int(((frame_time * 50 * ring) % 90) + 20)
            alpha = int(max(0, 180 - ring_r * 2))
            draw.ellipse(
                [center_x - ring_r, base_ground_y - int(ring_r * 0.28), center_x + ring_r, base_ground_y + int(ring_r * 0.28)],
                outline=(147, 197, 253, alpha),
                width=2,
            )

    # 5. Transform and Composite Character Sprite
    # Handle horizontal flip for pirouette
    curr_sprite = character_sprite.copy()
    flip_h = scale_x < 0
    eff_scale_x = max(0.12, abs(scale_x))
    eff_scale_y = max(0.2, abs(scale_y))

    target_w = int(curr_sprite.width * eff_scale_x)
    target_h = int(curr_sprite.height * eff_scale_y)
    curr_sprite = curr_sprite.resize((target_w, target_h), Image.Resampling.BILINEAR)

    if flip_h:
        curr_sprite = curr_sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    if abs(rotation_deg) > 0.5:
        curr_sprite = curr_sprite.rotate(rotation_deg, expand=True, resample=Image.Resampling.BILINEAR)

    # Paste sprite centered at (pos_x, pos_y - target_h // 2)
    paste_x = int(pos_x - curr_sprite.width // 2)
    paste_y = int(pos_y - curr_sprite.height // 2)
    frame.paste(curr_sprite, (paste_x, paste_y), curr_sprite)

    # 6. Cinematic Header & Choreography Badges
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    # Top title badge
    top_badge_h = 36
    ov_draw.rounded_rectangle([25, 20, width - 25, 20 + top_badge_h], radius=10, fill=(10, 15, 35, 190), outline=(99, 102, 241, 140), width=1)
    tag_font = get_font(12, bold=True)
    ov_draw.text((38, 30), f"FRAMEFLOW AI  •  SCENE {scene_number:02d}/{total_scenes:02d}  •  {scene_title.upper()}", font=tag_font, fill=(244, 114, 182, 255))

    # Bottom Motion Staging & Narration Bar
    bar_h = 75
    bar_y = height - bar_h - 20
    ov_draw.rounded_rectangle([25, bar_y, width - 25, bar_y + bar_h], radius=12, fill=(8, 12, 28, 215), outline=(147, 197, 253, 100), width=1)

    motion_font = get_font(11, bold=True)
    ov_draw.text((40, bar_y + 12), f"CHOREOGRAPHY: {motion_type.replace('_', ' ').upper()}", font=motion_font, fill=(251, 191, 36, 255))

    desc_font = get_font(13)
    ov_draw.text((40, bar_y + 32), scene_description[:110], font=desc_font, fill=(241, 245, 249, 255))

    # Bottom scene progress bar
    progress_bar_y = bar_y + bar_h - 6
    ov_draw.rectangle([25, progress_bar_y, width - 25, progress_bar_y + 4], fill=(30, 41, 59, 180))
    prog_w = int((width - 50) * scene_progress)
    ov_draw.rectangle([25, progress_bar_y, 25 + prog_w, progress_bar_y + 4], fill=(236, 72, 153, 255))

    return Image.alpha_composite(frame, overlay).convert("RGB")
