"""Configuración cargada desde variables de entorno / archivo .env."""

import os

import discord
from dotenv import load_dotenv

load_dotenv()

# Decora automáticamente los mensajes que contienen solo un enlace.
AUTOLINK_ENABLED = os.getenv("AUTOLINK_ENABLED", "true").strip().lower() in (
    "1",
    "true",
    "yes",
    "si",
)

NOMBRE_BOT = "Xiter 47' $ Bot"
DESCRIPCION_BOT = (
    "Server Security — Protege y gestiona tu servidor de Discord con "
    "moderación, utilidades y entretenimiento. Usa `/ayuda` para empezar."
)

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!").strip() or "!"
TEST_GUILD_ID = os.getenv("TEST_GUILD_ID", "").strip()
OWNER_ID = os.getenv("OWNER_ID", "").strip()

# Anti-raid: expulsar al superar el umbral de creación en la ventana de tiempo.
ANTIRAID_ENABLED = os.getenv("ANTIRAID_ENABLED", "true").strip().lower() in (
    "1",
    "true",
    "yes",
    "si",
)


def _entero_env(nombre: str, por_defecto: int) -> int:
    try:
        return int(os.getenv(nombre, str(por_defecto)).strip())
    except ValueError:
        return por_defecto


ANTIRAID_LIMIT = _entero_env("ANTIRAID_LIMIT", 5)
ANTIRAID_WINDOW = _entero_env("ANTIRAID_WINDOW", 10)
ANTIRAID_EXEMPT_IDS = {
    int(parte)
    for parte in os.getenv("ANTIRAID_EXEMPT_IDS", "").replace(" ", "").split(",")
    if parte.isdigit()
}

# ============================
# Embed tipo Panel (edita aquí los textos y links)
# ============================
PANEL_COLOR = discord.Color.blue()  # barra lateral azul
PANEL_TITULO = "│🛠️┃ʀᴇǫᴜɪʀᴇᴍᴇɴᴛs"
# Formato: (Nombre del campo, URL del link)
PANEL_ITEMS = [
    ("📦 Requirements", "https://www.mediafire.com/file/8gn74l43931vv43/Requerimientos+Xiter+47'$.rar/file"),
    ("🛡️ Defender Disabled", "https://www.mediafire.com/file/gqdnge6mbxgw4b3/Antivirus.rar/file"),
    ("🔥 FREE FIRE", "https://www.mediafire.com/file/liiuldko7og1qwd/Free.Fire-Normal.New.xapk/file"),
    ("💻 Bluestacks", "https://www.mediafire.com/file/ewsi640v5aui13y/Bluestacks+Xiter+47'$.exe/file"),
    ("🎮 MSI", "https://www.mediafire.com/file/f9a72yi0caakk4z/Msi+Xiter+47'$.exe/file"),
    ("⚠️ BORRAR EMULADORES", "https://www.mediafire.com/file/uqsl7x37t6n6iam/BSTCleaner+New+Versions.exe/file"),
]

# Envío automático al iniciar (deja en true para que salga solo sin /panel)
PANEL_AUTO_SEND = os.getenv("PANEL_AUTO_SEND", "true").strip().lower() in (
    "1",
    "true",
    "yes",
    "si",
)
# ID del canal donde se enviará automáticamente (ponlo en .env)
PANEL_CHANNEL_ID = os.getenv("PANEL_CHANNEL_ID", "").strip()

# Canales de bienvenida y despedida (pon los IDs en .env)
CANAL_BIENVENIDA_ID = os.getenv("CANAL_BIENVENIDA_ID", "").strip()
CANAL_DESPEDIDA_ID = os.getenv("CANAL_DESPEDIDA_ID", "").strip()

# ============================
# Sistema de Tickets
# ============================
TICKET_PANEL_CHANNEL_ID = os.getenv("TICKET_PANEL_CHANNEL_ID", "").strip()  # Canal donde está el botón de abrir ticket
TICKET_CATEGORY_ID = os.getenv("TICKET_CATEGORY_ID", "").strip()              # Categoría donde se crean los tickets
TICKET_STAFF_ROLE_ID = os.getenv("TICKET_STAFF_ROLE_ID", "").strip()          # Rol de staff que ve los tickets
