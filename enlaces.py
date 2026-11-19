"""Comandos para publicar enlaces decorados con embeds y botones."""

from urllib.parse import urlparse

import discord
from discord.ext import commands

from config import NOMBRE_BOT
from utils.embeds import crear, fallo

COLORES = {
    "azul": discord.Color.blurple(),
    "verde": discord.Color.green(),
    "rojo": discord.Color.red(),
    "morado": discord.Color.purple(),
    "naranja": discord.Color.orange(),
    "dorado": discord.Color.gold(),
    "rosa": discord.Color.pink(),
    "gris": discord.Color.default(),
    "blanco": discord.Color.default(),
}


def _plataforma(dominio: str) -> str:
    dominio = dominio.lower().removeprefix("www.")
    plataformas = {
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
    for clave, nombre in plataformas.items():
        if dominio == clave or dominio.endswith("." + clave):
            return nombre
    return "Sitio web"


class Enlaces(commands.Cog, name="Enlaces"):
    @commands.hybrid_command(
        name="link",
        aliases=["enlace"],
        description="Publica un enlace decorado con embed y botón",
    )
    async def link(
        self,
        ctx: commands.Context,
        url: str,
        titulo: str = "Enlace",
        descripcion: str = "",
        color: str = "azul",
        imagen: str = "",
    ) -> None:
        url = url.strip()
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            await ctx.send(
                embed=fallo(
                    "Enlace inválido",
                    "La URL debe empezar con `http://` o `https://`.",
                )
            )
            return

        dominio = parsed.netloc.removeprefix("www.")
        color_elegido = COLORES.get(color.strip().lower(), COLORES["azul"])

        embed = crear(
            titulo,
            descripcion or f"Haz clic en el botón para abrir el enlace.",
            color_elegido,
        )
        embed.add_field(name="Plataforma", value=_plataforma(dominio), inline=True)
        embed.add_field(name="Dominio", value=f"`{dominio}`", inline=True)

        imagen_parsed = urlparse(imagen.strip()) if imagen else None
        if (
            imagen_parsed
            and imagen_parsed.scheme in ("http", "https")
            and imagen_parsed.netloc
        ):
            embed.set_image(url=imagen.strip())

        embed.set_footer(
            text=f"Publicado por {ctx.author.display_name} · {NOMBRE_BOT}"
        )

        vista = discord.ui.View(timeout=None)
        vista.add_item(
            discord.ui.Button(
                label="Abrir enlace",
                style=discord.ButtonStyle.link,
                url=url,
                emoji="🔗",
            )
        )

        if ctx.message is not None and ctx.interaction is None:
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

        await ctx.send(embed=embed, view=vista)

    @commands.hybrid_command(
        name="embed",
        aliases=["encrustar", "crearembed"],
        description="Crea un embed decorado con título, campos, imagen y botón",
    )
    async def embed(
        self,
        ctx: commands.Context,
        titulo: str,
        descripcion: str = "",
        color: str = "azul",
        imagen: str = "",
        campo1: str = "",
        campo2: str = "",
        campo3: str = "",
        url_boton: str = "",
        texto_boton: str = "Abrir enlace",
    ) -> None:
        """campo1, campo2, campo3 van en formato: Nombre|Valor"""

        color_elegido = COLORES.get(color.strip().lower(), COLORES["azul"])
        embed = crear(titulo, descripcion, color_elegido)

        for campo in (campo1, campo2, campo3):
            if not campo.strip():
                continue
            if "|" in campo:
                nombre, valor = campo.split("|", 1)
            else:
                nombre, valor = campo, "—"
            embed.add_field(
                name=nombre.strip(),
                value=valor.strip(),
                inline=False,
            )

        imagen_parsed = urlparse(imagen.strip()) if imagen else None
        if (
            imagen_parsed
            and imagen_parsed.scheme in ("http", "https")
            and imagen_parsed.netloc
        ):
            embed.set_image(url=imagen.strip())

        embed.set_footer(
            text=f"Publicado por {ctx.author.display_name} · {NOMBRE_BOT}"
        )

        vista = None
        if url_boton:
            parsed = urlparse(url_boton.strip())
            if parsed.scheme in ("http", "https") and parsed.netloc:
                vista = discord.ui.View(timeout=None)
                vista.add_item(
                    discord.ui.Button(
                        label=texto_boton.strip() or "Abrir enlace",
                        style=discord.ButtonStyle.link,
                        url=url_boton.strip(),
                        emoji="🔗",
                    )
                )

        if ctx.message is not None and ctx.interaction is None:
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

        await ctx.send(embed=embed, view=vista)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Enlaces(bot))
