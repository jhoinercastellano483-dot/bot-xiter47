"""Decora automáticamente los enlaces que se pegan en el chat."""

import re

import discord
from discord.ext import commands

from config import AUTOLINK_ENABLED, NOMBRE_BOT
from utils.embeds import crear

URL_RE = re.compile(r"https?://[^\s<>\"'`]+", re.IGNORECASE)

PLATAFORMAS = {
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "twitch.tv": "Twitch",
    "github.com": "GitHub",
    "discord.com": "Discord",
    "discord.gg": "Discord",
    "spotify.com": "Spotify",
    "instagram.com": "Instagram",
    "tiktok.com": "TikTok",
    "x.com": "X / Twitter",
    "twitter.com": "X / Twitter",
    "reddit.com": "Reddit",
}


def _plataforma(dominio: str) -> str:
    dominio = dominio.lower().removeprefix("www.")
    for clave, nombre in PLATAFORMAS.items():
        if dominio == clave or dominio.endswith("." + clave):
            return nombre
    return "Sitio web"


class AutoLink(commands.Cog, name="Auto-Link"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not AUTOLINK_ENABLED:
            return
        if message.author.bot or message.guild is None:
            return
        if not message.content:
            return

        coincides = URL_RE.findall(message.content)
        if not coincides:
            return

        # Solo decoramos si el mensaje es únicamente el/los link(s), para no
        # interferir con conversaciones normales que mencionen una URL.
        texto_limpio = URL_RE.sub("", message.content).strip()
        if texto_limpio:
            return

        url = coincides[0].rstrip(".,;:!?)")
        dominio = url.split("/")[2] if "//" in url else url

        embed = crear(f"🔗 {_plataforma(dominio)}", url, discord.Color.blurple())
        embed.add_field(name="Dominio", value=f"`{dominio}`", inline=True)
        embed.set_footer(
            text=f"Publicado por {message.author.display_name} · {NOMBRE_BOT}"
        )
        if message.author.display_avatar:
            embed.set_thumbnail(url=message.author.display_avatar.url)

        vista = discord.ui.View(timeout=None)
        vista.add_item(
            discord.ui.Button(
                label="Abrir enlace",
                style=discord.ButtonStyle.link,
                url=url,
                emoji="🔗",
            )
        )

        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        await message.channel.send(embed=embed, view=vista)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoLink(bot))
