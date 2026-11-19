"""Comandos de utilidad e información."""

import random
from typing import Optional

import discord
from discord.ext import commands

from utils.embeds import crear

EMOJIS_NUMERO = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]


class Utilidades(commands.Cog, name="Utilidades"):
    @commands.hybrid_command(name="usuario", description="Muestra información de un usuario")
    async def usuario(
        self,
        ctx: commands.Context,
        miembro: Optional[discord.Member] = None,
    ) -> None:
        miembro = miembro or ctx.author
        embed = crear(f"👤 {miembro}", miembro.mention)
        embed.set_thumbnail(url=miembro.display_avatar.url)
        embed.add_field(name="ID", value=str(miembro.id), inline=True)
        embed.add_field(name="Cuenta creada", value=miembro.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(
            name="Se unió al servidor",
            value=miembro.joined_at.strftime("%d/%m/%Y") if miembro.joined_at else "—",
            inline=True,
        )
        roles = [rol.mention for rol in miembro.roles[1:]]
        embed.add_field(name="Roles", value=", ".join(roles) or "Ninguno", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="servidor", description="Muestra información del servidor")
    async def servidor(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        embed = crear(f"🏠 {guild.name}", guild.description or "Sin descripción")
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Miembros", value=str(guild.member_count), inline=True)
        embed.add_field(name="Canales", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Creado", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="ID", value=str(guild.id), inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="avatar", description="Muestra el avatar de un usuario")
    async def avatar(
        self,
        ctx: commands.Context,
        miembro: Optional[discord.Member] = None,
    ) -> None:
        miembro = miembro or ctx.author
        embed = crear(f"🖼️ Avatar de {miembro}", "")
        embed.set_image(url=miembro.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="elegir", description="Elige una opción al azar")
    async def elegir(self, ctx: commands.Context, *, opciones: str) -> None:
        items = [opcion.strip() for opcion in opciones.split(",") if opcion.strip()]
        if len(items) < 2:
            await ctx.send("Escribe al menos **2 opciones** separadas por comas.")
            return
        await ctx.send(embed=crear("🎲 Elección aleatoria", f"Elegí: **{random.choice(items)}**"))

    @commands.hybrid_command(name="encuesta", description="Crea una encuesta con reacciones")
    async def encuesta(
        self,
        ctx: commands.Context,
        pregunta: str,
        *,
        opciones: str,
    ) -> None:
        items = [opcion.strip() for opcion in opciones.split(",") if opcion.strip()]
        if len(items) < 2:
            await ctx.send("Necesitas al menos **2 opciones** separadas por comas.")
            return
        if len(items) > len(EMOJIS_NUMERO):
            await ctx.send(f"Máximo **{len(EMOJIS_NUMERO)} opciones** por encuesta.")
            return

        descripcion = "\n".join(
            f"{EMOJIS_NUMERO[i]} {opcion}" for i, opcion in enumerate(items)
        )
        embed = crear(f"📊 {pregunta}", descripcion)
        embed.set_footer(text=f"Encuesta creada por {ctx.author.display_name}")
        mensaje = await ctx.send(embed=embed)
        for emoji in EMOJIS_NUMERO[: len(items)]:
            await mensaje.add_reaction(emoji)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utilidades(bot))
