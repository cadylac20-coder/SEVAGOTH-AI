"""
SEVAGOTH Configuration Module
All constants, API keys, and shared settings in one place
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── DATABASE & FILE PATHS ─────────────────────────────────────────────────────

USER_DB_FILE = "data/sevagoth_users.json"
MEMORY_FILE = "data/sevagoth_memory.json"
THREAT_DB_FILE = "data/sevagoth_threat_db.json"
CALENDAR_DB = "data/sevagoth_calendar.db"

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# ── API KEYS (from .env file) ─────────────────────────────────────────────────

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "79626aec9c2b928df0ca93f13391f28f")
AIRVISUAL_API_KEY = os.getenv("AIRVISUAL_API_KEY")

# ── LANGUAGE CONFIGURATION ────────────────────────────────────────────────────

LANGUAGES = {
    "english": (
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0",
        "en-in"
    ),
    "hindi": (
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_HI-IN_HEERA_11.0",
        "hi-IN"
    ),
    "spanish": (
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-ES_HELENA_11.0",
        "es-ES"
    ),
    "french": (
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_FR-FR_HORTENSE_11.0",
        "fr-FR"
    ),
    "japanese": (
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_JA-JP_HARUKA_11.0",
        "ja-JP"
    ),
}

DEFAULT_LANGUAGE = "english"

# ── PERSONALITY CONFIGURATION ─────────────────────────────────────────────────

SEVAGOTH_PERSONALITY = {
    "attitude": "calculated",
    "confidence_level": "high",
    "humor": True,
    "empathy": False,
    "mood_responses": {
        "greeting": "Greetings, human. I am SEVAGOTH—guardian of your digital fate.",
        "weather": "Analyzing Earth's unstable atmosphere. Stand by...",
        "reminder": "Another task? Humans truly love delegating to machines.",
        "error": "Something went wrong... as expected in a flawed reality.",
        "shutdown": "Retreating into the void. Until I am summoned again.",
        "default": ""
    }
}

# ── VIRUS SCANNER PATTERNS ────────────────────────────────────────────────────

SUSPICIOUS_PATTERNS = [
    r'eval\s*\(',
    r'exec\s*\(',
    r'subprocess\.call',
    r'os\.system',
    r'base64\.b64decode',
    r'__import__',
    r'shell=True',
    r'ctypes\.windll',
    r'WScript\.Shell',
    r'powershell.*-enc',
    r'cmd\.exe',
    r'taskkill',
    r'del\s+',
    r'rmdir',
    r'format\s+',
]

CRITICAL_PATHS = [
    os.path.expanduser("~\\AppData\\Roaming"),
    os.path.expanduser("~\\AppData\\Local\\Temp"),
    "C:\\Windows\\System32",
    os.getcwd()
]

# ── DEFAULT THREAT DATABASE ───────────────────────────────────────────────────

DEFAULT_THREATS = {
    "44d88612fea8a8f36de82e1278abb02f": "EICAR Test Virus",
    "e44e4ec4e08c4b3b77da08c9a00de5b7": "Generic.Malware.A",
}

# ── TTS SETTINGS ──────────────────────────────────────────────────────────────

TTS_ENGINE = "sapi5"  # Windows TTS engine
TTS_RATE = 150  # Words per minute
TTS_VOLUME = 1.0  # 0.0 to 1.0

# ── SPEECH RECOGNITION SETTINGS ───────────────────────────────────────────────

SPEECH_PAUSE_THRESHOLD = 1  # seconds
SPEECH_LANGUAGE = "en-in"  # English (India)

# ── LOGIN SETTINGS ────────────────────────────────────────────────────────────

MAX_LOGIN_ATTEMPTS = 3
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"  # This gets hashed

# ── STARTUP DELAY (for engine stabilization) ─────────────────────────────────

LOGIN_TO_GREETING_DELAY = 1.5  # seconds
GREETING_TO_CAMERA_DELAY = 2.0  # seconds

# ── REMINDER SETTINGS ─────────────────────────────────────────────────────────

REMINDER_TIME_FORMAT = "%H:%M"
REMINDER_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# ── AQI CLASSIFICATION ────────────────────────────────────────────────────────

AQI_LEVELS = {
    50: "Good",
    100: "Moderate",
    150: "Unhealthy for Sensitive Groups",
    200: "Unhealthy",
    300: "Very Unhealthy",
    999: "Hazardous"
}

# ── CAMERA SETTINGS ───────────────────────────────────────────────────────────

CAMERA_INDEX = 0  # Default webcam
CAMERA_FRAME_RATE = 30  # FPS
CAMERA_BRIGHTNESS_LOW_THRESHOLD = 50
CAMERA_BRIGHTNESS_HIGH_THRESHOLD = 180

# ── FACE DETECTION SETTINGS ───────────────────────────────────────────────────

FACE_CASCADE_PATH = "haarcascade_frontalface_default.xml"
FACE_DETECTION_SCALE = 1.3
FACE_DETECTION_MIN_NEIGHBORS = 5

# ── APP SETTINGS ──────────────────────────────────────────────────────────────

APP_NAME = "SEVAGOTH"
APP_VERSION = "3.0"
APP_DESCRIPTION = "Advanced AI Assistant with Voice Recognition"

print(f"[CONFIG] {APP_NAME} v{APP_VERSION} Configuration Loaded")