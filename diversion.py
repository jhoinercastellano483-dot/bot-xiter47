"""Comandos de diversión."""

import random

from discord.ext import commands

from utils.embeds import crear

RESPUESTAS_BOLA8 = [
    "Sí, definitivamente.",
    "Es cierto.",
    "Sin duda alguna.",
    "Pregunta de nuevo más tarde.",
    "No cuentes con ello.",
    "Mi respuesta es no.",
    "No estoy seguro, inténtalo otra vez.",
    "Las probabilidades no son buenas.",
]


class Diversion(commands.Cog, name="Diversión"):
    @commands.hybrid_command(name="dado", description="Lanza un dado (6 caras por defecto)")
    async def dado(self, ctx: commands.Context, caras: int = 6) -> None:
        if caras < 2:
            await ctx.send("El dado necesita al menos **2 caras**.")
            return
        await ctx.send(embed=crear("🎲 Dado", f"Sacaste **{random.randint(1, caras)}** (1–{caras})"))

    @commands.hybrid_command(name="moneda", description="Lanza una moneda al aire")
    async def moneda(self, ctx: commands.Context) -> None:
        await ctx.send(embed=crear("🪙 Moneda", f"Salió **{random.choice(['Cara', 'Cruz'])}**"))

    @commands.hybrid_command(name="bola8", description="La bola 8 responde tu pregunta")
    async def bola8(self, ctx: commands.Context, *, pregunta: str) -> None:
        await ctx.send(
            embed=crear(
                "🎱 Bola 8",
                f"**Pregunta:** {pregunta}\n**Respuesta:** {random.choice(RESPUESTAS_BOLA8)}",
            )
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Diversion(bot))
