"""CIPHER PROTOCOL // Cybersecurity puzzle game
A green-terminal, keyboard/mouse-driven cybersecurity puzzle game.
Requires Python 3 and pygame (pygame-ce also works).
Run: py cipher_protocol_silent_payload.py
"""

import base64
import json
import math
import os
import queue
import random
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from array import array

import pygame

# ------------------------------- Setup ---------------------------------------
pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()
WIDTH, HEIGHT = 1180, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CIPHER QUEST | Cybersecurity + Cloud")
SONG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "silent_payload.wav")
clock = pygame.time.Clock()

BLACK = (2, 7, 4)
DARK = (3, 15, 8)
PANEL = (4, 20, 10)
PANEL_HI = (6, 29, 14)
GREEN = (80, 255, 120)
GREEN_BRIGHT = (160, 255, 170)
GREEN_DIM = (31, 132, 57)
GREEN_DARK = (12, 55, 25)
WHITE_GREEN = (206, 255, 213)
AMBER = (255, 197, 74)
RED = (255, 74, 74)
CYAN = (85, 238, 225)
MUTED = (101, 160, 112)

font_tiny = pygame.font.SysFont("segoeui", 16)
font_small = pygame.font.SysFont("segoeui", 19)
font = pygame.font.SysFont("segoeui", 21)
font_bold = pygame.font.SysFont("segoeui", 23, bold=True)
font_medium = pygame.font.SysFont("segoeui", 27, bold=True)
font_title = pygame.font.SysFont("segoeui", 43, bold=True)
font_huge = pygame.font.SysFont("segoeui", 54, bold=True)

# ------------------------------- Audio ---------------------------------------
audio_ok = False
sound_on = True  # interface effects
song_on = True   # original melancholic vocal song: SILENT PAYLOAD
sounds = {}
ambient_channel = None
vocal_song_loaded = False
try:
    pygame.mixer.init(22050, -16, 1, 512)
    audio_ok = True
    ambient_channel = pygame.mixer.Channel(0)
    if os.path.isfile(SONG_PATH):
        try:
            pygame.mixer.music.load(SONG_PATH)
            pygame.mixer.music.set_volume(0.55)
            vocal_song_loaded = True
        except pygame.error:
            vocal_song_loaded = False
except pygame.error:
    audio_ok = False


def synth_music(duration=8.0):
    """Generate an original, looping cyberpunk melody in code (no borrowed song/audio)."""
    if not audio_ok:
        return None
    sample_rate = 22050
    count = int(sample_rate * duration)
    data = array("h")
    # Four-chord progression: Em, C, G, D. A short 120-BPM loop.
    chords = [
        (82.41, 123.47, 164.81, 41.20),
        (65.41, 98.00, 130.81, 32.70),
        (98.00, 146.83, 196.00, 49.00),
        (73.42, 110.00, 146.83, 36.71),
    ]
    melody = [659, 784, 988, 784, 587, 659, 880, 659,
              523, 659, 784, 1046, 880, 784, 659, 587,
              659, 784, 988, 1175, 1046, 988, 784, 659,
              587, 659, 784, 659, 523, 587, 659, 523]
    beat_len = 0.5
    for i in range(count):
        t = i / sample_rate
        beat_number = int(t / beat_len)
        half_beat = int(t / (beat_len / 2))
        chord_index = int(t / 2.0) % 4
        c1, c2, c3, bass_f = chords[chord_index]
        # Soft chord pad makes it musical rather than a single ominous drone.
        pad_breath = 0.74 + 0.20 * math.sin(2 * math.pi * 0.25 * t)
        pad = (math.sin(2 * math.pi * c1 * t) * 0.055
               + math.sin(2 * math.pi * c2 * t) * 0.045
               + math.sin(2 * math.pi * c3 * t) * 0.035) * pad_breath
        # Plucked bass on each beat.
        beat_t = t % beat_len
        bass_env = math.exp(-beat_t * 4.0)
        bass = math.sin(2 * math.pi * bass_f * t) * bass_env * 0.16
        # Bright eight-note arpeggio/melody.
        note_freq = melody[half_beat % len(melody)]
        note_t = t % (beat_len / 2)
        note_env = math.exp(-note_t * 5.6)
        lead = (math.sin(2 * math.pi * note_freq * t)
                + 0.24 * math.sin(2 * math.pi * note_freq * 2 * t)) * note_env * 0.10
        # Electronic kick every beat.
        kick_env = math.exp(-beat_t * 20.0)
        kick_freq = 72 - 30 * min(1.0, beat_t / beat_len)
        kick = math.sin(2 * math.pi * kick_freq * beat_t) * kick_env * 0.20
        # Gentle digital snare on beats 2 and 4; soft hats on offbeats.
        beat_in_bar = beat_number % 4
        snare = 0.0
        if beat_in_bar in (1, 3) and beat_t < 0.11:
            snare_env = math.exp(-beat_t * 34.0)
            snare = (math.sin(2 * math.pi * 185 * beat_t)
                     + math.sin(2 * math.pi * 345 * beat_t)) * snare_env * 0.055
        hat = 0.0
        if half_beat % 2 == 1:
            hat_t = t % (beat_len / 2)
            if hat_t < 0.025:
                # Deterministic light high-frequency tick; avoids noisy randomness.
                hat = math.sin(2 * math.pi * 3600 * t) * math.exp(-hat_t * 90.0) * 0.025
        wave = (pad + bass + lead + kick + snare + hat) * 0.78
        # Tiny edge fade keeps the loop smooth at start/end.
        edge = min(1.0, t / 0.035, (duration - t) / 0.035)
        sample = int(max(-1.0, min(1.0, wave * max(0.0, edge))) * 32767)
        data.append(sample)
    try:
        return pygame.mixer.Sound(buffer=data.tobytes())
    except pygame.error:
        return None


def synth_sound(kind, duration):
    """Create small original interface effects in code; no external files required."""
    if not audio_ok:
        return None
    sample_rate = 22050
    count = max(1, int(sample_rate * duration))
    data = array("h")
    phase = 0.0
    for i in range(count):
        t = i / sample_rate
        p = i / count
        if kind == "ambient":
            wobble = math.sin(2 * math.pi * 0.21 * t)
            wave = (math.sin(2 * math.pi * (48 + 5 * wobble) * t) * 0.50
                    + math.sin(2 * math.pi * 72 * t) * 0.19
                    + math.sin(2 * math.pi * (93 + 3 * math.sin(t * 1.7)) * t) * 0.12)
            wave *= 0.20 + 0.10 * math.sin(2 * math.pi * 0.7 * t) ** 2
        elif kind == "type":
            wave = math.sin(2 * math.pi * 1250 * t) * math.exp(-p * 16) * 0.16
            wave += math.sin(2 * math.pi * 780 * t) * math.exp(-p * 25) * 0.08
        elif kind == "success":
            freq = 420 + 760 * p
            wave = (math.sin(2 * math.pi * freq * t) * 0.30
                    + math.sin(2 * math.pi * freq * 1.5 * t) * 0.08) * (1 - p) ** 0.45
        elif kind == "error":
            freq = 190 - 65 * p + 9 * math.sin(2 * math.pi * 9 * t)
            wave = math.sin(2 * math.pi * freq * t) * (1 - p) * 0.32
        elif kind == "alarm":
            freq = 330 + 190 * math.sin(2 * math.pi * 3.5 * t)
            wave = math.sin(2 * math.pi * freq * t) * 0.20 * (1 - p * 0.65)
            wave += math.sin(2 * math.pi * (freq * 0.5) * t) * 0.08
        else:  # soft menu ping
            freq = 330 + 180 * math.sin(p * math.pi)
            wave = math.sin(2 * math.pi * freq * t) * (1 - p) * 0.18
        fade_in = min(1.0, i / 180)
        fade_out = min(1.0, (count - i) / max(1, int(sample_rate * 0.035)))
        sample = int(max(-1, min(1, wave * fade_in * fade_out)) * 32767)
        data.append(sample)
    try:
        return pygame.mixer.Sound(buffer=data.tobytes())
    except pygame.error:
        return None


if audio_ok:
    sounds = {
        "ambient": synth_music(8.0),
        "type": synth_sound("type", 0.055),
        "success": synth_sound("success", 0.55),
        "error": synth_sound("error", 0.35),
        "alarm": synth_sound("alarm", 0.8),
        "click": synth_sound("click", 0.12),
    }
    for name, vol in {"ambient": 0.27, "type": 0.10, "success": 0.42,
                      "error": 0.28, "alarm": 0.18, "click": 0.22}.items():
        if sounds.get(name):
            sounds[name].set_volume(vol)


def play_sound(name):
    if not audio_ok:
        return
    try:
        if name == "ambient":
            if not song_on:
                return
            # Prefer the bundled original SILENT PAYLOAD vocal track; use the generated synth loop only as fallback.
            if vocal_song_loaded:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            elif sounds.get("ambient") and ambient_channel and not ambient_channel.get_busy():
                ambient_channel.play(sounds["ambient"], loops=-1)
        elif sound_on and sounds.get(name):
            sounds[name].play()
    except pygame.error:
        pass


def toggle_sound():
    """Toggle interface effects only."""
    global sound_on
    sound_on = not sound_on


def toggle_song():
    """Toggle the background vocal theme independently from button effects."""
    global song_on
    song_on = not song_on
    if not song_on:
        if ambient_channel:
            ambient_channel.stop()
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
    else:
        play_sound("ambient")

# --------------------------- Cryptography tools -----------------------------
def letters_only(text):
    return "".join(ch for ch in text.upper() if "A" <= ch <= "Z")


def normalize_answer(text):
    return "".join(ch for ch in text.upper() if ch.isalnum())


def caesar_decrypt(text, key=3):
    out = []
    for ch in text.upper():
        if "A" <= ch <= "Z":
            out.append(chr((ord(ch) - ord("A") - key) % 26 + ord("A")))
        else:
            out.append(ch)
    return "".join(out)


def playfair_square(key):
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    result = []
    for ch in (letters_only(key).replace("J", "I") + alphabet):
        if ch in alphabet and ch not in result:
            result.append(ch)
    return [result[i:i + 5] for i in range(0, 25, 5)]


def playfair_encrypt(text, key):
    raw = letters_only(text).replace("J", "I")
    pairs = []
    i = 0
    while i < len(raw):
        a = raw[i]
        if i + 1 >= len(raw):
            b = "X"
            i += 1
        elif raw[i + 1] == a:
            b = "X"
            i += 1
        else:
            b = raw[i + 1]
            i += 2
        pairs.append((a, b))
    grid = playfair_square(key)
    pos = {ch: (r, c) for r, row in enumerate(grid) for c, ch in enumerate(row)}
    out = []
    for a, b in pairs:
        ra, ca = pos[a]
        rb, cb = pos[b]
        if ra == rb:
            out.extend((grid[ra][(ca + 1) % 5], grid[rb][(cb + 1) % 5]))
        elif ca == cb:
            out.extend((grid[(ra + 1) % 5][ca], grid[(rb + 1) % 5][cb]))
        else:
            out.extend((grid[ra][cb], grid[rb][ca]))
    return "".join(out)


def vigenere_encrypt(text, key):
    key = letters_only(key)
    out, j = [], 0
    for ch in text.upper():
        if "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + ord(key[j % len(key)]) - 65) % 26 + 65))
            j += 1
        else:
            out.append(ch)
    return "".join(out)


def encode_lsb(surface, message):
    payload = message.encode("ascii", errors="ignore") + b"\0"
    bits = "".join(f"{byte:08b}" for byte in payload)
    w, h = surface.get_size()
    for i, bit in enumerate(bits[:w * h]):
        x, y = i % w, i // w
        r, g, b, a = surface.get_at((x, y))
        surface.set_at((x, y), ((r & 254) | int(bit), g, b, a))
    return surface


def decode_lsb(surface):
    w, h = surface.get_size()
    byte_bits, output = "", []
    for i in range(w * h):
        x, y = i % w, i // w
        byte_bits += str(surface.get_at((x, y))[0] & 1)
        if len(byte_bits) == 8:
            value = int(byte_bits, 2)
            if value == 0:
                break
            output.append(value)
            byte_bits = ""
    return bytes(output).decode("ascii", errors="ignore")


def make_cat_art():
    art = pygame.Surface((300, 220)).convert()
    art.fill((2, 12, 7))
    for x in range(4, 300, 18):
        pygame.draw.line(art, (5, 35, 15), (x, 0), (x, 220), 1)
        for y in range((x * 3) % 31, 220, 32):
            pygame.draw.rect(art, (9, 60, 24), (x + 3, y, 5, 11))
    # Digital cat silhouette and neon eyes.
    pygame.draw.ellipse(art, (8, 40, 19), (51, 64, 198, 172))
    pygame.draw.polygon(art, (18, 91, 36), [(71, 94), (78, 24), (129, 73)])
    pygame.draw.polygon(art, (18, 91, 36), [(171, 73), (224, 24), (231, 95)])
    pygame.draw.polygon(art, (3, 16, 8), [(83, 79), (85, 43), (112, 73)])
    pygame.draw.polygon(art, (3, 16, 8), [(188, 73), (216, 43), (219, 80)])
    pygame.draw.ellipse(art, (18, 73, 30), (66, 69, 168, 145))
    pygame.draw.ellipse(art, (2, 8, 4), (92, 103, 43, 53))
    pygame.draw.ellipse(art, (2, 8, 4), (165, 103, 43, 53))
    pygame.draw.ellipse(art, (80, 255, 120), (99, 113, 29, 30))
    pygame.draw.ellipse(art, (80, 255, 120), (172, 113, 29, 30))
    pygame.draw.ellipse(art, BLACK, (111, 113, 7, 29))
    pygame.draw.ellipse(art, BLACK, (184, 113, 7, 29))
    pygame.draw.circle(art, WHITE_GREEN, (107, 119), 4)
    pygame.draw.circle(art, WHITE_GREEN, (180, 119), 4)
    pygame.draw.polygon(art, (16, 99, 49), [(142, 151), (157, 151), (150, 161)])
    pygame.draw.line(art, (72, 190, 96), (150, 160), (139, 168), 2)
    pygame.draw.line(art, (72, 190, 96), (150, 160), (161, 168), 2)
    for y in range(0, 220, 4):
        pygame.draw.line(art, (0, 20, 6), (0, y), (300, y), 1)
    for i in range(80):
        x = random.randrange(300)
        y = random.randrange(220)
        pygame.draw.rect(art, random.choice([(10, 72, 25), (8, 40, 18), (21, 110, 40)]), (x, y, random.randint(1, 3), 1))
    pygame.draw.rect(art, GREEN_DIM, (1, 1, 298, 218), 2)
    return art


cat_art = encode_lsb(make_cat_art(), "CAT")

# -------------------------- Mission definitions -----------------------------
playfair_cipher = playfair_encrypt("MEETME", "MONARCH")
vigenere_cipher = vigenere_encrypt("ACCESS GRANTED", "ORBIT")

STAGES = [
    {
        "title": "CAESAR CIPHER", "difficulty": "LEVEL 01 // BEGINNER", "type": "cipher",
        "brief": "A captured message was shifted through the alphabet. Reverse the shift and recover the phrase.",
        "label": "ENCRYPTED PAYLOAD", "display": "KHOOR ZRUOG", "expected": "HELLO WORLD",
        "meta": "METHOD: CAESAR     KEY / SHIFT: 3", "hint": "Move every letter BACK by 3 places. Example: D becomes A.",
        "points": 100,
    },
    {
        "title": "PLAYFAIR CIPHER", "difficulty": "LEVEL 02 // INTERMEDIATE", "type": "cipher",
        "brief": "This message was encrypted in letter pairs using a 5x5 Playfair grid. Recover the original text.",
        "label": "PAIR ENCRYPTION", "display": playfair_cipher, "expected": "MEETME",
        "meta": "KEYWORD: MONARCH     I / J SHARE ONE CELL", "hint": "Build the 5x5 grid using MONARCH, then decrypt each pair with Playfair rules.",
        "points": 150,
    },
    {
        "title": "ACROSTIC TRACE", "difficulty": "LEVEL 03 // PUZZLE", "type": "text",
        "brief": "An operator hid a keyword in plain sight. Read the FIRST letter of every word, in order.",
        "label": "RECOVER THE HIDDEN WORD", "display": "Silent Hackers Investigate\nEncrypted Logs Daily", "expected": "SHIELD",
        "meta": "TECHNIQUE: FIRST-LETTER EXTRACTION", "hint": "Take the first character of each word, including words on the second line.",
        "points": 150,
    },
    {
        "title": "CAT // STEGANOGRAPHY", "difficulty": "LEVEL 04 // FORENSICS", "type": "stego",
        "brief": "The image is not just artwork. Run a pixel scan, then read each 8-bit group as an ASCII character.",
        "label": "HIDDEN PIXEL STREAM", "display": "IMAGE DATA NOT ANALYZED", "expected": "CAT",
        "meta": "ARTIFACT: cat_payload.img     CHANNEL: RED / LSB", "hint": "After scanning, split the binary into 8-bit bytes and convert each byte from ASCII.",
        "points": 200,
    },
    {
        "title": "VIGENERE CIPHER", "difficulty": "LEVEL 05 // ADVANCED", "type": "cipher",
        "brief": "A repeating-key cipher protects the next access phrase. Subtract each key letter from the matching ciphertext letter.",
        "label": "ENCRYPTED ACCESS PHRASE", "display": vigenere_cipher, "expected": "ACCESS GRANTED",
        "meta": "METHOD: VIGENERE     KEYWORD: ORBIT", "hint": "Use A=0 through Z=25. Repeat ORBIT across the letters and subtract the key values.",
        "points": 250,
    },
    {
        "title": "BASE64 RECOVERY", "difficulty": "LEVEL 06 // ADVANCED", "type": "cipher",
        "brief": "This payload is encoded, not encrypted. Identify the encoding and decode the text.",
        "label": "ENCODED PAYLOAD", "display": "Q1lCRVJTRUNSRVQ=", "expected": "CYBERSECRET",
        "meta": "FORMAT: BASE64     PADDING: =", "hint": "Base64 uses letters, digits, +, / and optional = padding. Decode it to text.",
        "points": 250,
    },
    {
        "title": "BINARY FORENSICS", "difficulty": "LEVEL 07 // EXPERT", "type": "cipher",
        "brief": "A packet dump contains ASCII bytes. Convert each 8-bit binary group to its character, then combine them.",
        "label": "RAW BYTE STREAM", "display": "01010100 01010010 01000001\n01000011 01000101", "expected": "TRACE",
        "meta": "FORMAT: 8-BIT BINARY     ENCODING: ASCII", "hint": "Convert each 8-bit group from binary to decimal, then find the matching ASCII character.",
        "points": 300,
    },
    {
        "title": "INCIDENT RESPONSE", "difficulty": "LEVEL 08 // EXPERT", "type": "logs",
        "brief": "Inspect the authentication logs. Which source IP is repeatedly failing logins and likely performing a brute-force attempt?",
        "label": "AUTHENTICATION LOG // LAST 30 SECONDS",
        "display": "22:14:01  10.0.0.8       LOGIN OK    user=maya\n22:14:03  172.16.4.20  AUTH FAIL   user=admin\n22:14:04  172.16.4.20  AUTH FAIL   user=root\n22:14:05  172.16.4.20  AUTH FAIL   user=guest\n22:14:06  172.16.4.20  AUTH FAIL   user=admin\n22:14:07  10.0.0.12      LOGIN OK    user=alex",
        "expected": "172.16.4.20", "meta": "TASK: IDENTIFY THE REPEATED FAILURE SOURCE", "hint": "Look for the same source address appearing repeatedly beside AUTH FAIL.",
        "points": 350,
    },
    {
        "title": "WEB ATTACK ANALYSIS", "difficulty": "LEVEL 09 // FINAL", "type": "text",
        "brief": "A web login request contains an input crafted to change how a database query behaves. Identify the vulnerability category.",
        "label": "SUSPICIOUS REQUEST", "display": "GET /login?user=' OR '1'='1' --", "expected": "SQL INJECTION",
        "meta": "MISSION: CLASSIFY THE ATTACK     MODE: DEFENSIVE ANALYSIS", "hint": "The clue is about manipulating a database query through user input. Name the vulnerability.",
        "points": 400,
    },
]

# ----------------------------- Matrix effect ---------------------------------
RAIN_CHARS = "0123456789ABCDEF#$%&<>/\\[]{}"
rain = []
for x in range(0, WIDTH, 17):
    rain.append({"x": x, "y": random.randrange(-HEIGHT, HEIGHT),
                 "speed": random.uniform(1.2, 4.2), "length": random.randint(5, 12)})
frame_count = 0
# Lightweight particles used only on the main menu's neon animation.
menu_particles = [
    {"x": random.randrange(0, WIDTH), "y": random.randrange(65, HEIGHT),
     "speed": random.uniform(0.45, 1.8), "size": random.choice((1, 1, 2)),
     "hue": random.randrange(0, 3)}
    for _ in range(78)
]


def draw_matrix_background():
    global frame_count
    screen.fill(BLACK)
    # Very subtle terminal grid.
    for x in range(0, WIDTH, 80):
        pygame.draw.line(screen, (3, 20, 8), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 70):
        pygame.draw.line(screen, (3, 18, 7), (0, y), (WIDTH, y), 1)
    for col in rain:
        col["y"] += col["speed"]
        if col["y"] - col["length"] * 15 > HEIGHT:
            col["y"] = random.randrange(-260, -20)
            col["speed"] = random.uniform(1.2, 4.2)
            col["length"] = random.randint(5, 12)
        for j in range(col["length"]):
            yy = int(col["y"] - j * 15)
            if -15 <= yy < HEIGHT:
                ch = random.choice(RAIN_CHARS) if random.random() < 0.28 else random.choice("01ABCDEF")
                if j == 0:
                    color = (115, 255, 148)
                else:
                    brightness = max(18, 102 - j * 7)
                    color = (10, brightness, 24)
                screen.blit(font_tiny.render(ch, True, color), (col["x"], yy))
    # Moving scan line.
    scan_y = (frame_count * 3) % HEIGHT
    pygame.draw.line(screen, (6, 34, 14), (0, scan_y), (WIDTH, scan_y), 2)
    frame_count += 1


def draw_scanlines():
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(screen, (0, 9, 2), (0, y), (WIDTH, y), 1)
    # Small restrained glitch streaks, not enough to obscure gameplay.
    if frame_count % 71 < 2:
        y = random.randint(80, HEIGHT - 60)
        pygame.draw.rect(screen, (33, 8, 11), (0, y, WIDTH, random.randint(1, 3)))

# ------------------------------ UI helpers -----------------------------------
clickables = []
answer_box = pygame.Rect(54, 448, 480, 45)


def draw_text(text, font_obj, color, x, y, center=False, shadow=False):
    rendered = font_obj.render(str(text), True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    if shadow:
        shadow_surface = font_obj.render(str(text), True, (0, 65, 19))
        sr = shadow_surface.get_rect()
        sr.topleft = (rect.x + 2, rect.y + 2)
        screen.blit(shadow_surface, sr)
    screen.blit(rendered, rect)
    return rect


def wrap_text(text, font_obj, color, rect, line_gap=4, max_lines=None):
    words = str(text).split()
    line = ""
    y = rect.y
    lines_drawn = 0
    for word in words:
        candidate = word if not line else line + " " + word
        if font_obj.size(candidate)[0] <= rect.width:
            line = candidate
        else:
            if line:
                draw_text(line, font_obj, color, rect.x, y)
                y += font_obj.get_linesize() + line_gap
                lines_drawn += 1
                if max_lines and lines_drawn >= max_lines:
                    return y
            line = word
    if line and (not max_lines or lines_drawn < max_lines):
        draw_text(line, font_obj, color, rect.x, y)
        y += font_obj.get_linesize() + line_gap
    return y


def panel(rect, fill=PANEL, outline=GREEN_DIM, radius=8, glow=False):
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    if glow:
        pygame.draw.rect(screen, (9, 67, 25), rect.inflate(4, 4), 1, border_radius=radius + 2)
    pygame.draw.rect(screen, outline, rect, 1, border_radius=radius)


def button(label, rect, action, accent=GREEN, enabled=True, sublabel=None):
    mouse = pygame.mouse.get_pos()
    hover = enabled and rect.collidepoint(mouse)
    fill = (8, 42, 18) if hover else (3, 21, 9)
    edge = accent if enabled else (32, 65, 39)
    if hover:
        pygame.draw.rect(screen, (7, 48, 18), rect.inflate(4, 4), 1, border_radius=5)
    pygame.draw.rect(screen, fill, rect, border_radius=5)
    pygame.draw.rect(screen, edge, rect, 2 if hover else 1, border_radius=5)
    draw_text(label, font_bold if len(label) < 22 else font_small, accent if enabled else MUTED,
              rect.centerx, rect.centery - (5 if sublabel else 0), center=True)
    if sublabel:
        draw_text(sublabel, font_tiny, MUTED, rect.centerx, rect.centery + 12, center=True)
    if enabled:
        clickables.append((rect.copy(), action))


def draw_top_bar(tag="TRAINING TERMINAL"):
    panel(pygame.Rect(24, 15, WIDTH - 48, 44), fill=(2, 13, 6), outline=GREEN_DIM, radius=5)
    draw_text("[ CIPHER QUEST ]", font_bold, GREEN, 40, 28)
    draw_text("CYBERSECURITY + CLOUD GAME", font_small, MUTED, 310, 28)
    # Blinking status dot.
    color = GREEN if frame_count % 50 < 35 else GREEN_DIM
    pygame.draw.circle(screen, color, (WIDTH - 226, 37), 5)
    draw_text("SYSTEM ONLINE", font_small, GREEN_BRIGHT, WIDTH - 212, 27)
    draw_text(tag, font_tiny, AMBER, WIDTH - 205, 44)


def draw_status_strip(text, color=GREEN):
    rect = pygame.Rect(30, HEIGHT - 30, WIDTH - 60, 18)
    pygame.draw.rect(screen, (1, 12, 5), rect)
    draw_text(text, font_tiny, color, rect.x + 8, rect.y + 2)

# ------------------------------- Screens -------------------------------------
phase = "menu"
current_stage = 0
unlocked = 0
completed = set()
score = 0
answer_text = ""
feedback = ""
feedback_color = GREEN
hint_used = False
scan_done = False
input_active = False
attempts_this_stage = 0
activity_log = ["[SYS] CYBER RANGE INITIALIZED", "[OK] LOCAL SANDBOX ACTIVE", "[SYS] AWAITING OPERATOR INPUT"]

# Optional real cloud integration using Firebase Authentication + Realtime Database.
# Fill cloud_config.json with your Firebase Web API key and database URL to enable it.
CLOUD_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloud_config.json")
try:
    with open(CLOUD_CONFIG_PATH, "r", encoding="utf-8") as _cloud_file:
        cloud_config = json.load(_cloud_file)
except (OSError, json.JSONDecodeError):
    cloud_config = {}

cloud_api_key = str(cloud_config.get("api_key", "")).strip()
cloud_database_url = str(cloud_config.get("database_url", "")).strip().rstrip("/")
cloud_configured = bool(
    cloud_api_key and "PASTE_" not in cloud_api_key and
    cloud_database_url.startswith("https://") and "YOUR-PROJECT" not in cloud_database_url
)
cloud_token = None
cloud_uid = None
cloud_user_email = ""
cloud_email_input = ""
cloud_password_input = ""
cloud_active_field = "email"
cloud_status = "NOT CONFIGURED // see cloud_config.json"
cloud_busy = False
cloud_messages = queue.Queue()
cloud_leaderboard = []
cloud_score_saved = False
CLOUD_EMAIL_RECT = pygame.Rect(80, 269, 454, 43)
CLOUD_PASSWORD_RECT = pygame.Rect(80, 340, 454, 43)


def _firebase_request(url, data=None, method=None):
    payload = None if data is None else json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message", detail)
        except Exception:
            message = str(exc)
        raise RuntimeError(str(message)) from exc


def _cloud_worker(action, email, password, score_value, missions_value, token, uid):
    """Network work runs away from the game loop so the UI does not freeze."""
    try:
        if not cloud_configured:
            raise RuntimeError("Cloud not configured: edit cloud_config.json first.")
        if action in ("login", "register"):
            endpoint_action = "signInWithPassword" if action == "login" else "signUp"
            url = ("https://identitytoolkit.googleapis.com/v1/accounts:" + endpoint_action
                   + "?key=" + urllib.parse.quote(cloud_api_key, safe=""))
            result = _firebase_request(url, {
                "email": email, "password": password, "returnSecureToken": True
            }, "POST")
            cloud_messages.put(("auth_ok", {
                "token": result["idToken"], "uid": result["localId"], "email": result.get("email", email),
                "message": "ACCOUNT READY // CLOUD CONNECTED"
            }))
        elif action == "sync":
            if not token or not uid:
                raise RuntimeError("Sign in to Firebase before syncing a score.")
            url = f"{cloud_database_url}/leaderboard/{urllib.parse.quote(uid, safe='')}.json?auth={urllib.parse.quote(token, safe='')}"
            data = {
                "name": email.split("@", 1)[0][:24] or "operator",
                "score": int(score_value),
                "missions_completed": int(missions_value),
                "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")
            }
            _firebase_request(url, data, "PUT")
            cloud_messages.put(("sync_ok", data))
        elif action == "load":
            if not token:
                raise RuntimeError("Sign in to load the cloud leaderboard.")
            url = f"{cloud_database_url}/leaderboard.json?auth={urllib.parse.quote(token, safe='')}"
            result = _firebase_request(url, None, "GET") or {}
            rows = []
            if isinstance(result, dict):
                for item in result.values():
                    if isinstance(item, dict):
                        rows.append({
                            "name": str(item.get("name", "operator"))[:24],
                            "score": int(item.get("score", 0)),
                            "missions_completed": int(item.get("missions_completed", 0))
                        })
            rows.sort(key=lambda item: (item["score"], item["missions_completed"]), reverse=True)
            cloud_messages.put(("load_ok", rows[:8]))
    except Exception as exc:
        msg = str(exc)
        translations = {
            "EMAIL_EXISTS": "This email already exists. Choose LOGIN.",
            "EMAIL_NOT_FOUND": "Email not found. Choose CREATE ACCOUNT first.",
            "INVALID_PASSWORD": "Password is incorrect.",
            "INVALID_LOGIN_CREDENTIALS": "Email or password is incorrect.",
            "WEAK_PASSWORD": "Password needs at least 6 characters.",
            "OPERATION_NOT_ALLOWED": "Enable Email/Password in Firebase Authentication.",
            "API_KEY_INVALID": "Check api_key in cloud_config.json.",
            "Permission denied": "Firebase database rules denied this request.",
        }
        for code, friendly in translations.items():
            if code in msg:
                msg = friendly
                break
        cloud_messages.put(("error", msg[:150]))


def start_cloud_task(action):
    global cloud_busy, cloud_status
    if cloud_busy:
        cloud_status = "PLEASE WAIT // CLOUD REQUEST IN PROGRESS"
        return
    if not cloud_configured:
        cloud_status = "NOT CONFIGURED // edit cloud_config.json"
        return
    if action in ("login", "register"):
        email = cloud_email_input.strip()
        password = cloud_password_input
        if "@" not in email or len(password) < 6:
            cloud_status = "ENTER A VALID EMAIL AND 6+ CHARACTER PASSWORD"
            return
    else:
        email = cloud_user_email
        password = ""
    cloud_busy = True
    cloud_status = "CONTACTING FIREBASE CLOUD..."
    thread = threading.Thread(
        target=_cloud_worker,
        args=(action, email, password, score, len(completed), cloud_token, cloud_uid),
        daemon=True,
    )
    thread.start()


def process_cloud_messages():
    global cloud_busy, cloud_token, cloud_uid, cloud_user_email, cloud_email_input, cloud_status, cloud_leaderboard, cloud_score_saved
    while True:
        try:
            kind, value = cloud_messages.get_nowait()
        except queue.Empty:
            break
        cloud_busy = False
        if kind == "auth_ok":
            cloud_token = value["token"]
            cloud_uid = value["uid"]
            cloud_user_email = value["email"]
            cloud_email_input = value["email"]
            cloud_status = value["message"]
            cloud_score_saved = False
            log_event("[CLOUD] AUTHENTICATED WITH FIREBASE")
        elif kind == "sync_ok":
            cloud_score_saved = True
            cloud_status = f"CLOUD SYNC COMPLETE // SCORE {value['score']} SAVED"
            log_event("[CLOUD] SCORE SAVED TO FIREBASE LEADERBOARD")
        elif kind == "load_ok":
            cloud_leaderboard = value
            cloud_status = f"CLOUD LEADERBOARD LOADED // {len(value)} RECORD(S)"
        elif kind == "error":
            cloud_status = "CLOUD ERROR // " + value
            log_event("[CLOUD WARN] " + value[:48])


def log_event(message):
    activity_log.append(message)
    del activity_log[:-6]


def open_stage(index):
    global phase, current_stage, answer_text, feedback, hint_used, scan_done, input_active, attempts_this_stage
    if index > unlocked and index not in completed:
        return
    current_stage = index
    answer_text = ""
    feedback = ""
    hint_used = False
    scan_done = False
    input_active = True
    attempts_this_stage = 0
    phase = "mission"
    log_event(f"[LOAD] MISSION {index + 1:02d} // {STAGES[index]['title']}")
    play_sound("click")


def check_answer():
    global phase, feedback, feedback_color, score, unlocked, hint_used, attempts_this_stage
    stage = STAGES[current_stage]
    if stage["type"] == "stego" and not scan_done:
        feedback = "PIXEL SCAN REQUIRED // ANALYZE THE IMAGE FIRST"
        feedback_color = AMBER
        play_sound("alarm")
        log_event("[WARN] PIXEL DATA HAS NOT BEEN ANALYZED")
        return
    expected = stage["expected"]
    if stage.get("validator") == "ip":
        okay = answer_text.strip() == expected
    else:
        okay = normalize_answer(answer_text) == normalize_answer(expected)
    attempts_this_stage += 1
    if okay:
        first_completion = current_stage not in completed
        completed.add(current_stage)
        if first_completion:
            earned = stage["points"] if not hint_used else int(stage["points"] * 0.7)
            score += earned
        unlocked = max(unlocked, min(current_stage + 1, len(STAGES) - 1))
        feedback = "ACCESS GRANTED // PAYLOAD VERIFIED"
        feedback_color = GREEN_BRIGHT
        phase = "success"
        log_event(f"[PASS] MISSION {current_stage + 1:02d} CLEARED")
        play_sound("success")
    else:
        feedback = "ACCESS DENIED // CHECK THE CLUES AND TRY AGAIN"
        feedback_color = RED
        log_event(f"[BLOCK] INVALID RESPONSE // ATTEMPT {attempts_this_stage}")
        play_sound("error")


def reveal_hint():
    global hint_used, feedback, feedback_color
    hint_used = True
    feedback = "HINT // " + STAGES[current_stage]["hint"]
    feedback_color = AMBER
    log_event("[HINT] ANALYST NOTE REQUESTED")
    play_sound("click")


def scan_image():
    global scan_done, feedback, feedback_color
    stage = STAGES[current_stage]
    if stage["type"] != "stego":
        return
    hidden = decode_lsb(cat_art)
    binary = " ".join(f"{ord(ch):08b}" for ch in hidden)
    scan_done = True
    feedback = "PIXEL SCAN COMPLETE // BINARY BYTES EXTRACTED"
    feedback_color = CYAN
    log_event("[FORENSICS] RED-CHANNEL LSB SCAN COMPLETE")
    log_event("[DATA] " + binary)
    # Showing the extracted bitstream is the actual puzzle clue.
    play_sound("alarm")


def next_after_success():
    global phase
    if current_stage >= len(STAGES) - 1:
        phase = "win"
        log_event("[MISSION] ALL INCIDENTS RESOLVED")
        play_sound("success")
    else:
        phase = "select"


def draw_menu_neon_background():
    """Draw animated neon atmosphere behind the title and main menu."""
    # Darken the Matrix rain slightly so the buttons and title remain readable.
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 3, 7, 132))
    screen.blit(shade, (0, 0))

    t = frame_count / 50.0
    pulse = 0.5 + 0.5 * math.sin(t * 1.7)
    cyan = (18, int(145 + pulse * 70), 255)
    violet = (int(145 + pulse * 80), 45, 255)
    pink = (255, int(35 + pulse * 45), int(130 + pulse * 60))

    # Animated perspective grid: a neon data floor receding into the screen.
    horizon = 438
    scroll = (frame_count * 2) % 26
    for i in range(1, 13):
        base = i * 22 + scroll
        y = horizon + int(base * (base / 110.0))
        if y < HEIGHT:
            alpha_color = (5, min(100, 25 + i * 5), min(120, 40 + i * 5))
            pygame.draw.line(screen, alpha_color, (0, y), (WIDTH, y), 1)
    vanishing_x = WIDTH // 2
    for x in range(-900, WIDTH + 1000, 92):
        end_x = vanishing_x + int((x - vanishing_x) * 1.48)
        pygame.draw.line(screen, (4, 49, 65), (vanishing_x, horizon), (end_x, HEIGHT), 1)

    # Floating neon particles move gently across the screen.
    palette = [(50, 255, 170), (30, 210, 255), (207, 70, 255)]
    for particle in menu_particles:
        particle["y"] += particle["speed"]
        particle["x"] += math.sin(t + particle["y"] * 0.014) * 0.32
        if particle["y"] > HEIGHT - 8:
            particle["y"] = random.randint(66, 115)
            particle["x"] = random.randrange(0, WIDTH)
        color = palette[particle["hue"]]
        x, y = int(particle["x"]), int(particle["y"])
        pygame.draw.circle(screen, color, (x, y), particle["size"])
        if particle["size"] == 2 and frame_count % 3 == 0:
            pygame.draw.line(screen, (12, 80, 105), (x - 4, y), (x + 4, y), 1)

    # Side rails pulse between cyan and violet, with small circuit segments.
    rail_left = (42, 91, 112)
    rail_right = (83, 44, 120)
    pygame.draw.line(screen, rail_left, (24, 82), (24, 625), 2)
    pygame.draw.line(screen, rail_right, (WIDTH - 25, 82), (WIDTH - 25, 625), 2)
    for i in range(7):
        y = 100 + i * 78 + int((frame_count * 1.4) % 30)
        if y < 640:
            pygame.draw.line(screen, cyan, (24, y), (35, y), 2)
            pygame.draw.line(screen, violet, (WIDTH - 36, y + 25), (WIDTH - 25, y + 25), 2)

    # Thin neon frame around the play area.
    frame_color = (14, int(68 + pulse * 38), int(90 + pulse * 55))
    pygame.draw.rect(screen, frame_color, pygame.Rect(35, 75, WIDTH - 70, 565), 1, border_radius=10)


def draw_menu():
    draw_menu_neon_background()
    draw_top_bar("MAIN MENU")

    # Keep the first screen simple: one clear title, one clear action, and readable labels.
    title_y = 101
    title_text = "CIPHER QUEST"
    if frame_count % 93 < 3:
        draw_text(title_text, font_huge, (255, 55, 155), WIDTH // 2 + 3, title_y - 1, center=True)
        draw_text(title_text, font_huge, (40, 225, 255), WIDTH // 2 - 3, title_y + 1, center=True)
    draw_text(title_text, font_huge, GREEN_BRIGHT, WIDTH // 2, title_y, center=True, shadow=True)
    draw_text("A cyber game about secret codes and cloud security", font_small, WHITE_GREEN,
              WIDTH // 2, 157, center=True)

    # Left card: simple summary rather than dense technical text.
    left = pygame.Rect(48, 218, 220, 302)
    panel(left, fill=(1, 12, 17), outline=(24, 111, 132), radius=8, glow=True)
    draw_text("YOUR MISSION", font_bold, CYAN, left.x + 16, left.y + 17)
    pygame.draw.line(screen, (19, 96, 115), (left.x + 16, left.y + 53), (left.right - 16, left.y + 53), 1)
    mission_lines = ["Solve the puzzles", "Find hidden messages", "Unlock every stage"]
    for i, line in enumerate(mission_lines):
        yy = left.y + 76 + i * 50
        pygame.draw.circle(screen, GREEN, (left.x + 24, yy + 10), 4)
        wrap_text(line, font_small, WHITE_GREEN, pygame.Rect(left.x + 39, yy, 160, 34), line_gap=0, max_lines=2)
    draw_text("9 CHALLENGES", font_bold, GREEN_BRIGHT, left.x + 16, left.y + 250)

    # Right card: the Cloud part is visible, without claiming that Firebase is configured.
    right = pygame.Rect(WIDTH - 268, 218, 220, 302)
    panel(right, fill=(1, 12, 17), outline=(93, 57, 145), radius=8, glow=True)
    draw_text("CLOUD FEATURES", font_bold, (202, 145, 255), right.x + 14, right.y + 17)
    pygame.draw.line(screen, (93, 57, 145), (right.x + 14, right.y + 53), (right.right - 14, right.y + 53), 1)
    cloud_lines = ["Save your score online", "Create an account", "Compare scores"]
    for i, line in enumerate(cloud_lines):
        yy = right.y + 76 + i * 51
        pygame.draw.circle(screen, (202, 145, 255), (right.x + 21, yy + 10), 4)
        wrap_text(line, font_small, WHITE_GREEN, pygame.Rect(right.x + 35, yy, 165, 36), line_gap=0, max_lines=2)
    draw_text("OPTIONAL SETUP", font_small, AMBER, right.x + 14, right.y + 250)

    # Main menu card and clear buttons.
    center = pygame.Rect(292, 207, 596, 390)
    panel(center, fill=(1, 9, 15), outline=(18, 115, 136), radius=10, glow=True)
    draw_text("WELCOME, PLAYER", font_medium, CYAN, WIDTH // 2, 231, center=True)
    draw_text("Ready to crack the code?", font_small, WHITE_GREEN, WIDTH // 2, 263, center=True)

    play_rect = pygame.Rect(WIDTH // 2 - 210, 292, 420, 68)
    button("▶  PLAY GAME", play_rect, "start", CYAN)
    button("HOW TO PLAY", pygame.Rect(326, 382, 242, 48), "brief", (202, 145, 255))
    button("CLOUD SCORES", pygame.Rect(580, 382, 274, 48), "cloud", CYAN)
    button("SETTINGS", pygame.Rect(WIDTH // 2 - 148, 443, 296, 44), "settings", (255, 110, 178))
    song_text = "SILENT PAYLOAD: ON" if song_on else "SILENT PAYLOAD: OFF"
    button(song_text, pygame.Rect(WIDTH // 2 - 148, 498, 296, 42), "song",
           GREEN if sound_on else AMBER)
    draw_text("Press PLAY to begin. Press M to turn the song on or off.", font_small, MUTED,
              WIDTH // 2, 563, center=True)
    draw_status_strip("CIPHER PUZZLES  |  CLOUD SCORES  |  USE YOUR KEYBOARD AND MOUSE", MUTED)

def draw_select():
    draw_top_bar("MISSION SELECT")
    draw_text("SELECT AN OPERATION", font_title, GREEN_BRIGHT, 34, 76, shadow=True)
    draw_text("Complete missions in order to unlock advanced investigations.", font_small, MUTED, 38, 121)
    card_w, card_h = 354, 143
    start_x, start_y, gap_x, gap_y = 34, 157, 28, 14
    for i, stage in enumerate(STAGES):
        row, col = divmod(i, 3)
        rect = pygame.Rect(start_x + col * (card_w + gap_x), start_y + row * (card_h + gap_y), card_w, card_h)
        is_unlocked = i <= unlocked or i in completed
        is_done = i in completed
        edge = GREEN if is_unlocked else (32, 61, 38)
        fill = (4, 25, 11) if is_unlocked else (3, 12, 6)
        panel(rect, fill=fill, outline=edge, radius=6, glow=(is_unlocked and not is_done))
        num_color = GREEN_BRIGHT if is_unlocked else MUTED
        draw_text(f"{i + 1:02d}", font_medium, num_color, rect.x + 14, rect.y + 13)
        title_color = WHITE_GREEN if is_unlocked else MUTED
        draw_text(stage["title"], font_bold, title_color, rect.x + 63, rect.y + 15)
        draw_text(stage["difficulty"], font_tiny, AMBER if i >= 4 else GREEN_DIM, rect.x + 64, rect.y + 43)
        brief = stage["brief"]
        wrap_text(brief, font_tiny, MUTED if is_unlocked else (68, 90, 71),
                  pygame.Rect(rect.x + 15, rect.y + 70, card_w - 30, 35), line_gap=0, max_lines=2)
        if is_done:
            status = "[ MISSION CLEARED ]"
            status_color = GREEN_BRIGHT
        elif is_unlocked:
            status = "[ AVAILABLE // ENTER ]"
            status_color = CYAN
        else:
            status = "[ LOCKED ]"
            status_color = MUTED
        draw_text(status, font_tiny, status_color, rect.x + 15, rect.y + 119)
        if is_unlocked:
            clickables.append((rect.copy(), f"stage:{i}"))
    button("[ BACK TO MAIN MENU ]", pygame.Rect(34, 640, 240, 34), "menu", CYAN)
    draw_text(f"MISSIONS CLEARED: {len(completed)}/{len(STAGES)}     SCORE: {score:04d}", font_small, GREEN, 700, 649)


def draw_cat_image(rect):
    scaled = pygame.transform.smoothscale(cat_art, (rect.width, rect.height))
    screen.blit(scaled, rect.topleft)
    pygame.draw.rect(screen, GREEN_DIM, rect, 1)


def draw_mission():
    stage = STAGES[current_stage]
    draw_top_bar(f"MISSION {current_stage + 1:02d} / {len(STAGES):02d}")
    # Progress bar.
    progress_rect = pygame.Rect(32, 73, WIDTH - 64, 12)
    pygame.draw.rect(screen, (3, 20, 8), progress_rect, border_radius=4)
    fill_w = int(progress_rect.width * (len(completed) / len(STAGES)))
    if fill_w:
        pygame.draw.rect(screen, GREEN, (progress_rect.x, progress_rect.y, fill_w, progress_rect.height), border_radius=4)
    draw_text(f"SCORE {score:04d}", font_tiny, GREEN_BRIGHT, WIDTH - 138, 91)

    left = pygame.Rect(30, 113, 720, 505)
    right = pygame.Rect(770, 113, 380, 505)
    panel(left, fill=(2, 14, 6), outline=GREEN_DIM, glow=True)
    panel(right, fill=(2, 13, 6), outline=GREEN_DIM)

    draw_text(f"// {stage['title']}", font_medium, GREEN_BRIGHT, 52, 132)
    draw_text(stage["difficulty"], font_tiny, AMBER, 54, 164)
    wrap_text(stage["brief"], font_small, WHITE_GREEN, pygame.Rect(54, 188, 670, 48), line_gap=2, max_lines=2)

    data_rect = pygame.Rect(52, 244, 676, 157)
    panel(data_rect, fill=(0, 8, 3), outline=(20, 94, 36), radius=5)
    draw_text(stage["label"], font_tiny, CYAN, 67, 256)
    draw_text(stage["meta"], font_tiny, AMBER, 67, 376)

    if stage["type"] == "logs":
        lines = stage["display"].splitlines()
        for i, line in enumerate(lines):
            col = RED if "AUTH FAIL" in line else GREEN
            draw_text(line, font_tiny, col, 68, 281 + i * 16)
    elif stage["type"] == "stego":
        content = "PIXEL STREAM NOT EXTRACTED"
        if scan_done:
            content = "01000011 01000001 01010100"
        draw_text(content, font_bold if not scan_done else font, GREEN_BRIGHT, 68, 306)
        draw_text("Each 8-bit byte represents one ASCII character.", font_tiny, MUTED, 68, 338)
    else:
        lines = stage["display"].splitlines()
        start_y = 301 if len(lines) > 1 else 315
        line_font = font_small if len(lines) > 1 else font_medium
        for i, line in enumerate(lines):
            color = GREEN_BRIGHT if i == 0 else GREEN
            draw_text(line, line_font, color, 68, start_y + i * 29)

    draw_text("ENTER YOUR DECODED ANSWER", font_tiny, GREEN, 54, 416)
    pygame.draw.rect(screen, (0, 8, 3), answer_box, border_radius=4)
    pygame.draw.rect(screen, GREEN if input_active else GREEN_DIM, answer_box, 2 if input_active else 1, border_radius=4)
    value = answer_text
    if not value:
        draw_text("type response here...", font, (53, 91, 61), answer_box.x + 12, answer_box.y + 13)
    else:
        draw_text(value, font_bold, GREEN_BRIGHT, answer_box.x + 12, answer_box.y + 12)
    if input_active and frame_count % 60 < 30:
        caret_x = answer_box.x + 12 + font_bold.size(value)[0] + 2
        pygame.draw.line(screen, GREEN_BRIGHT, (min(caret_x, answer_box.right - 8), answer_box.y + 9),
                         (min(caret_x, answer_box.right - 8), answer_box.bottom - 9), 2)
    button("[ SUBMIT ]", pygame.Rect(548, 448, 162, 45), "submit", GREEN)
    button("[ REQUEST HINT ]", pygame.Rect(53, 512, 183, 37), "hint", AMBER)
    button("[ MISSION GRID ]", pygame.Rect(248, 512, 183, 37), "select", CYAN)
    if feedback:
        wrap_text(feedback, font_tiny, feedback_color, pygame.Rect(54, 557, 655, 41), line_gap=1, max_lines=2)

    # Right dashboard, no robot maze: the game is a terminal and investigation console.
    draw_text("SECURITY OPERATIONS", font_bold, GREEN, 793, 133)
    draw_text("LIVE ANALYST FEED", font_tiny, MUTED, 794, 159)
    if stage["type"] == "stego":
        image_rect = pygame.Rect(808, 186, 304, 222)
        draw_cat_image(image_rect)
        button("[ ANALYZE IMAGE / PIXELS ]", pygame.Rect(808, 418, 304, 38), "scan", CYAN)
        draw_text("ARTIFACT: CAT_IMAGE.BIN", font_tiny, GREEN, 811, 469)
        draw_text("CHANNEL: RED LEAST-SIGNIFICANT BIT", font_tiny, MUTED, 811, 489)
        draw_text("STATUS: " + ("ANALYZED" if scan_done else "WAITING FOR SCAN"), font_tiny,
                  GREEN_BRIGHT if scan_done else AMBER, 811, 509)
        panel(pygame.Rect(808, 536, 304, 55), fill=(0, 9, 3), outline=(18, 70, 29), radius=4)
        draw_text("FORENSIC RULE:", font_tiny, CYAN, 819, 544)
        draw_text("Pixel bits can carry hidden text.", font_tiny, WHITE_GREEN, 819, 564)
    else:
        panel(pygame.Rect(792, 185, 335, 112), fill=(0, 8, 3), outline=(17, 69, 28), radius=4)
        telemetry = [
            ("CRYPTO ENGINE", "READY", GREEN),
            ("SANDBOX NETWORK", "OFFLINE", AMBER),
            ("THREAT LEVEL", "TRAINING ONLY", CYAN),
            ("ANSWER CHECK", "LOCAL", GREEN),
        ]
        for i, (a, b, c) in enumerate(telemetry):
            draw_text(a, font_tiny, MUTED, 808, 198 + i * 22)
            draw_text(b, font_tiny, c, 1000, 198 + i * 22)
        draw_text("EVENT LOG", font_tiny, GREEN, 794, 315)
        panel(pygame.Rect(792, 337, 335, 254), fill=(0, 8, 3), outline=(17, 69, 28), radius=4)
        last = activity_log[-9:]
        for i, item in enumerate(last):
            color = GREEN if "[PASS]" in item or "[OK]" in item else (AMBER if "[WARN]" in item or "[HINT]" in item else MUTED)
            draw_text(item[:42], font_tiny, color, 805, 350 + i * 24)
    draw_status_strip("ENTER = SUBMIT   |   ESC = MISSION GRID   |   M = MUSIC ON/OFF", MUTED)


def draw_success():
    draw_top_bar("MISSION CLEARED")
    # Matrix background becomes brighter behind the success window.
    rect = pygame.Rect(170, 126, 840, 485)
    panel(rect, fill=(1, 17, 7), outline=GREEN, radius=12, glow=True)
    draw_text("[ ACCESS GRANTED ]", font_huge, GREEN_BRIGHT, WIDTH // 2, 183, center=True, shadow=True)
    draw_text("PAYLOAD VERIFIED  //  MISSION COMPLETE", font_bold, GREEN, WIDTH // 2, 235, center=True)
    draw_text(f"MISSION {current_stage + 1:02d}: {STAGES[current_stage]['title']}", font, WHITE_GREEN, WIDTH // 2, 292, center=True)
    draw_text(f"TOTAL SCORE: {score:04d}", font_medium, AMBER, WIDTH // 2, 336, center=True)
    draw_text(f"MISSIONS CLEARED: {len(completed):02d} / {len(STAGES):02d}", font, GREEN, WIDTH // 2, 378, center=True)
    draw_text("The next operation is ready in the mission grid.", font_small, MUTED, WIDTH // 2, 416, center=True)
    button("[ CONTINUE ]", pygame.Rect(320, 483, 250, 46), "continue", GREEN)
    button("[ MISSION GRID ]", pygame.Rect(600, 483, 250, 46), "select", CYAN)
    draw_status_strip("GOOD WORK, OPERATOR // KEEP INVESTIGATING", GREEN)


def draw_win():
    draw_top_bar("ALL OPERATIONS COMPLETE")
    rect = pygame.Rect(150, 105, 880, 525)
    panel(rect, fill=(1, 17, 7), outline=GREEN_BRIGHT, radius=12, glow=True)
    draw_text("SYSTEM SECURED", font_huge, GREEN_BRIGHT, WIDTH // 2, 171, center=True, shadow=True)
    draw_text("YOU CLEARED THE CIPHER PROTOCOL", font_medium, GREEN, WIDTH // 2, 223, center=True)
    draw_text(f"FINAL SCORE: {score:04d}", font_title, AMBER, WIDTH // 2, 292, center=True)
    draw_text(f"MISSIONS COMPLETED: {len(completed)} / {len(STAGES)}", font, WHITE_GREEN, WIDTH // 2, 341, center=True)
    rank = "ELITE ANALYST" if score >= 2100 else "CYBER INVESTIGATOR"
    draw_text(f"RANK AWARDED: {rank}", font_bold, CYAN, WIDTH // 2, 385, center=True)
    draw_text("Remember: investigate responsibly and protect systems.", font_small, MUTED, WIDTH // 2, 425, center=True)
    button("[ RUN AGAIN ]", pygame.Rect(310, 500, 240, 46), "restart", GREEN)
    button("[ MAIN MENU ]", pygame.Rect(580, 500, 240, 46), "menu", CYAN)
    draw_status_strip("SIMULATION FINISHED // NO REAL SYSTEMS WERE ACCESSED", GREEN)


def draw_brief():
    draw_top_bar("MISSION BRIEF")
    rect = pygame.Rect(90, 105, 1000, 520)
    panel(rect, fill=(2, 15, 6), outline=GREEN, radius=8, glow=True)
    draw_text("OPERATOR BRIEFING", font_title, GREEN_BRIGHT, 126, 134)
    items = [
        "01  Caesar Cipher / reverse a letter shift.",
        "02  Playfair Cipher / decrypt pairs using a 5x5 keyword grid.",
        "03  Acrostic / recover a message from the first letter of each word.",
        "04  Steganography / scan a cat image for hidden pixel data.",
        "05  Vigenere / decrypt a repeating-key cipher.",
        "06  Base64 / decode an encoded payload.",
        "07  Binary Forensics / convert binary bytes into ASCII.",
        "08  Incident Response / find a brute-force pattern in fictional logs.",
        "09  Web Attack Analysis / classify a suspicious login input.",
        "CLOUD FEATURE / Firebase account, online scores, shared leaderboard.",
    ]
    for i, line in enumerate(items):
        draw_text(line, font_small, GREEN if i < 4 else (CYAN if i == 9 else WHITE_GREEN), 132, 190 + i * 30)
    draw_text("The cloud leaderboard is optional; core gameplay works offline.", font_small, AMBER, 132, 515)
    button("[ BACK ]", pygame.Rect(132, 565, 180, 38), "menu", CYAN)
    button("[ START OPERATIONS ]", pygame.Rect(795, 565, 260, 38), "start", GREEN)


def draw_cloud_portal():
    draw_top_bar("CLOUD OPERATIONS")
    draw_text("CLOUD SCOREBOARD", font_title, GREEN_BRIGHT, 42, 78, shadow=True)
    draw_text("REAL CLOUD STORAGE // FIREBASE REALTIME DATABASE", font_small, CYAN, 46, 125)
    left = pygame.Rect(38, 160, 545, 455)
    right = pygame.Rect(603, 160, 539, 455)
    panel(left, fill=(2, 14, 6), outline=GREEN_DIM, glow=True)
    panel(right, fill=(2, 14, 6), outline=GREEN_DIM)
    draw_text("ACCOUNT / CONNECTION", font_bold, GREEN, 62, 181)
    status_color = AMBER if (not cloud_configured or cloud_busy or "ERROR" in cloud_status) else GREEN_BRIGHT
    wrap_text(cloud_status, font_small, status_color, pygame.Rect(62, 211, 493, 32), line_gap=1, max_lines=2)
    draw_text("EMAIL ADDRESS", font_small, WHITE_GREEN, 80, 248)
    pygame.draw.rect(screen, (0, 8, 3), CLOUD_EMAIL_RECT, border_radius=4)
    pygame.draw.rect(screen, CYAN if cloud_active_field == "email" else GREEN_DIM, CLOUD_EMAIL_RECT, 2 if cloud_active_field == "email" else 1, border_radius=4)
    draw_text(cloud_email_input or "operator@example.com", font, GREEN_BRIGHT if cloud_email_input else MUTED,
              CLOUD_EMAIL_RECT.x + 12, CLOUD_EMAIL_RECT.y + 11)
    draw_text("PASSWORD (6+ CHARACTERS)", font_small, WHITE_GREEN, 80, 319)
    pygame.draw.rect(screen, (0, 8, 3), CLOUD_PASSWORD_RECT, border_radius=4)
    pygame.draw.rect(screen, CYAN if cloud_active_field == "password" else GREEN_DIM, CLOUD_PASSWORD_RECT, 2 if cloud_active_field == "password" else 1, border_radius=4)
    masked = "*" * len(cloud_password_input) if cloud_password_input else "enter password"
    draw_text(masked, font, GREEN_BRIGHT if cloud_password_input else MUTED,
              CLOUD_PASSWORD_RECT.x + 12, CLOUD_PASSWORD_RECT.y + 11)
    button("[ LOGIN ]", pygame.Rect(80, 397, 218, 42), "cloud_login", GREEN)
    button("[ CREATE ACCOUNT ]", pygame.Rect(315, 397, 219, 42), "cloud_register", CYAN)
    if cloud_token:
        draw_text("SIGNED IN AS: " + cloud_user_email[:34], font_tiny, GREEN_BRIGHT, 80, 452)
        button("[ SYNC MY SCORE ]", pygame.Rect(80, 477, 218, 42), "cloud_sync", AMBER)
        button("[ REFRESH BOARD ]", pygame.Rect(315, 477, 219, 42), "cloud_load", CYAN)
    else:
        wrap_text("Sign in or create an account after Firebase is configured. Scores stay local until you choose SYNC.",
                  font_small, MUTED, pygame.Rect(80, 462, 450, 64), line_gap=2, max_lines=3)
    if not cloud_configured:
        wrap_text("SETUP NEEDED: add the Firebase Web API key and Realtime Database URL to cloud_config.json.",
                  font_small, AMBER, pygame.Rect(62, 531, 490, 40), line_gap=1, max_lines=2)
    button("[ BACK TO MAIN MENU ]", pygame.Rect(62, 578, 250, 30), "menu", GREEN)

    draw_text("GLOBAL TRAINING LEADERBOARD", font_bold, GREEN, 628, 181)
    draw_text("Scores are saved online to your Firebase project.", font_small, MUTED, 628, 214)
    panel(pygame.Rect(626, 250, 491, 290), fill=(0, 8, 3), outline=(20, 94, 36), radius=5)
    draw_text("RANK", font_small, CYAN, 647, 268)
    draw_text("OPERATOR", font_small, CYAN, 715, 268)
    draw_text("MISSIONS", font_small, CYAN, 900, 268)
    draw_text("SCORE", font_small, CYAN, 1016, 268)
    pygame.draw.line(screen, GREEN_DIM, (644, 296), (1099, 296), 1)
    if not cloud_leaderboard:
        draw_text("No cloud records loaded yet.", font, MUTED, 653, 320)
        draw_text("1. Configure Firebase", font_small, WHITE_GREEN, 653, 360)
        draw_text("2. Login / create account", font_small, WHITE_GREEN, 653, 390)
        draw_text("3. Finish missions and sync score", font_small, WHITE_GREEN, 653, 420)
    else:
        for i, row in enumerate(cloud_leaderboard[:8]):
            y = 310 + i * 26
            color = GREEN_BRIGHT if i == 0 else WHITE_GREEN
            draw_text(f"{i + 1:02d}", font_small, CYAN, 650, y)
            draw_text(row.get("name", "operator")[:22], font_small, color, 715, y)
            draw_text(str(row.get("missions_completed", 0)), font_small, GREEN, 932, y)
            draw_text(str(row.get("score", 0)), font_small, AMBER, 1023, y)
    wrap_text("CLOUD CONCEPT: authentication + remote database + shared leaderboard + cross-device score access.",
              font_small, GREEN_DIM, pygame.Rect(628, 557, 480, 43), line_gap=2, max_lines=2)
    draw_status_strip("CLOUD SYNC IS OPTIONAL // OFFLINE GAMEPLAY STILL WORKS", MUTED)


def draw_settings():
    draw_top_bar("SETTINGS")
    rect = pygame.Rect(300, 155, 580, 390)
    panel(rect, fill=(2, 15, 6), outline=GREEN, radius=8, glow=True)
    draw_text("SETTINGS", font_title, GREEN_BRIGHT, WIDTH // 2, 205, center=True)
    draw_text("SILENT PAYLOAD — original mellow vocal song + button sounds", font_small, MUTED, WIDTH // 2, 273, center=True)
    button("SONG: " + ("ON" if song_on else "OFF"), pygame.Rect(425, 330, 330, 45), "song", GREEN if song_on else AMBER)
    draw_text("Press M anytime to turn the song on or off.", font_small, MUTED, WIDTH // 2, 395, center=True)
    button("[ BACK TO MENU ]", pygame.Rect(440, 445, 300, 42), "menu", CYAN)

# ------------------------------- Actions -------------------------------------
def handle_action(action):
    global phase, unlocked, completed, score, current_stage, answer_text, feedback, hint_used, scan_done
    play_sound("click")
    if action == "start":
        phase = "select"
    elif action == "brief":
        phase = "brief"
    elif action == "settings":
        phase = "settings"
    elif action == "cloud":
        phase = "cloud"
    elif action == "cloud_login":
        start_cloud_task("login")
    elif action == "cloud_register":
        start_cloud_task("register")
    elif action == "cloud_sync":
        start_cloud_task("sync")
    elif action == "cloud_load":
        start_cloud_task("load")
    elif action == "menu":
        phase = "menu"
    elif action == "select":
        phase = "select"
    elif action == "sound":
        toggle_sound()
    elif action == "song":
        toggle_song()
    elif action == "submit":
        check_answer()
    elif action == "hint":
        reveal_hint()
    elif action == "scan":
        scan_image()
    elif action == "continue":
        next_after_success()
    elif action == "restart":
        unlocked = 0
        completed = set()
        score = 0
        open_stage(0)
    elif action.startswith("stage:"):
        try:
            open_stage(int(action.split(":", 1)[1]))
        except ValueError:
            pass
    elif action == "quit":
        pygame.event.post(pygame.event.Event(pygame.QUIT))


def click_test(pos):
    for rect, action in reversed(clickables):
        if rect.collidepoint(pos):
            handle_action(action)
            return True
    return False

# -------------------------------- Main loop ----------------------------------
running = True
while running:
    clock.tick(50)
    if song_on and audio_ok:
        play_sound("ambient")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if phase == "mission" and answer_box.collidepoint(event.pos):
                input_active = True
            else:
                input_active = False
            if phase == "cloud" and CLOUD_EMAIL_RECT.collidepoint(event.pos):
                cloud_active_field = "email"
            elif phase == "cloud" and CLOUD_PASSWORD_RECT.collidepoint(event.pos):
                cloud_active_field = "password"
            else:
                click_test(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                toggle_song()
            elif event.key == pygame.K_ESCAPE:
                if phase == "menu":
                    running = False
                elif phase == "mission":
                    phase = "select"
                elif phase in ("select", "brief", "settings", "success"):
                    phase = "menu" if phase in ("brief", "settings") else "select"
                elif phase == "cloud":
                    phase = "menu"
                elif phase == "win":
                    phase = "menu"
            elif phase == "menu" and event.key == pygame.K_RETURN:
                phase = "select"
                play_sound("click")
            elif phase == "select" and pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                if idx <= unlocked or idx in completed:
                    open_stage(idx)
            elif phase == "mission":
                if event.key == pygame.K_RETURN:
                    check_answer()
                elif event.key == pygame.K_BACKSPACE:
                    answer_text = answer_text[:-1]
                    play_sound("type")
                elif input_active and event.unicode and event.unicode.isprintable() and len(answer_text) < 64:
                    answer_text += event.unicode.upper()
                    play_sound("type")
            elif phase == "cloud":
                if event.key == pygame.K_TAB:
                    cloud_active_field = "password" if cloud_active_field == "email" else "email"
                elif event.key == pygame.K_BACKSPACE:
                    if cloud_active_field == "email":
                        cloud_email_input = cloud_email_input[:-1]
                    else:
                        cloud_password_input = cloud_password_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if cloud_active_field == "email":
                        cloud_active_field = "password"
                    elif cloud_email_input and cloud_password_input:
                        start_cloud_task("login")
                elif event.unicode and event.unicode.isprintable():
                    if cloud_active_field == "email" and len(cloud_email_input) < 100:
                        cloud_email_input += event.unicode
                    elif cloud_active_field == "password" and len(cloud_password_input) < 128:
                        cloud_password_input += event.unicode
                    play_sound("type")
            elif phase == "success" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                next_after_success()
            elif phase in ("brief", "settings", "cloud") and event.key == pygame.K_RETURN:
                if phase in ("brief", "settings"):
                    phase = "menu"

    process_cloud_messages()
    clickables = []
    draw_matrix_background()
    if phase == "menu":
        draw_menu()
    elif phase == "select":
        draw_select()
    elif phase == "mission":
        draw_mission()
    elif phase == "success":
        draw_success()
    elif phase == "win":
        draw_win()
    elif phase == "brief":
        draw_brief()
    elif phase == "settings":
        draw_settings()
    elif phase == "cloud":
        draw_cloud_portal()
    draw_scanlines()
    pygame.display.flip()

pygame.quit()
sys.exit()
