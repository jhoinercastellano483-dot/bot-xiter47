# 🤖 Bot de Discord (Python + discord.py)

Bot multiusos y **modular**: trae comandos básicos, moderación, utilidades y diversión, y está listo para seguir creciendo. Los comandos funcionan tanto con `/comando` (slash) como con `!comando`.

---

## 1. Requisitos

- **Python 3.10 o superior** → https://www.python.org/downloads/
  - ⚠️ Durante la instalación en Windows, marca **"Add Python to PATH"**.

Comprueba que esté bien instalado abriendo una terminal en esta carpeta:

```powershell
python --version
```

## 2. Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

## 3. Configurar el token

1. Abre el archivo `.env` que ya está creado.
2. Reemplaza `PEGAR_TOKEN_AQUI` por tu token real:

```env
DISCORD_TOKEN=TU_TOKEN_REAL_AQUI
COMMAND_PREFIX=!
```

> El token es como tu contraseña: no lo compartas ni lo subas a GitHub. `.env` ya está ignorado por git.

### Si aún no configuraste el bot en el Portal de Desarrolladores

1. Entra a https://discord.com/developers/applications → **New Application**.
2. En la pestaña **Bot** → **Add Bot** y copia el **Token** (resetea si se te perdió).
3. En **Privileged Gateway Intents**, activa:
   - ✅ **Message Content Intent**
   - ✅ **Server Members Intent**
4. En **OAuth2 → URL Generator**:
   - Scopes: `bot` + `applications.commands`
   - Permisos recomendados: *Send Messages, Embed Links, Read Message History, Manage Messages, Kick Members, Ban Members, Moderate Members, Add Reactions, Use External Emojis*
5. Copia la URL generada, ábrela e invita al bot a tu servidor.

## 4. Iniciar el bot

```powershell
python bot.py
```

Si todo sale bien verás algo como:

```
Cog cargado: diversion
Cog cargado: eventos
...
Conectado como TuBot#1234 (ID: 123456789...)
```

Detén el bot con `Ctrl + C`.

---

## 5. Comandos incluidos

| Categoría | Comandos |
|---|---|
| **General** | `/ayuda`, `/acerca`, `/ping`, `/hola`, `/decir`, `/invitar` |
| **Moderación** | `/limpiar`, `/expulsar`, `/banear`, `/desbanear`, `/silenciar`, `/desilenciar`, `/advertir`, `/advertencias` |
| **Utilidades** | `/usuario`, `/servidor`, `/avatar`, `/elegir`, `/encuesta` |
| **Enlaces** | `/link` (publica un enlace decorado con botón) |
| **Anti-Raid** | `/antiraid` (solo administradores) |
| **Diversión** | `/dado`, `/moneda`, `/bola8` |

Ejemplos con prefijo:

```
!ping
!limpiar 20
!silenciar @usuario 30 motivo: spam
!elegir pizza, sushi, hamburguesa
!encuesta "¿Qué hacemos hoy?" opciones: Cine, Juegos, Pasear
```

Las advertencias se guardan en `data/warnings.json` para que no se pierdan al reiniciar.

---

## 6. Agregar tus propios comandos (para "más cosas")

La carga es automática: cualquier `.py` que pongas dentro de `cogs/` se carga solo al iniciar.

Ejemplo, crea `cogs/micomando.py`:

```python
from discord.ext import commands
from utils.embeds import ok


class MiComando(commands.Cog, name="Mi Comando"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="saludo", description="Un saludo personalizado")
    async def saludo(self, ctx):
        await ctx.send(embed=ok("¡Funciona!", "Acabas de crear tu primer comando."))


async def setup(bot):
    await bot.add_cog(MiComando(bot))
```

Reinicia el bot y ya estará disponible como `/saludo` y `!saludo`.

---

## 6.3 Embed tipo Panel

`/panel` envía un embed con el estilo de la imagen: título con icono, campos con emojis, subtítulos y enlaces azules tipo "Descargar".

```
/panel
```

Con prefijo: `!panel` (el bot borra tu mensaje y deja solo el embed).

### Cómo cambiar textos y links

Edita el archivo `config.py`, busca la sección **Embed tipo Panel** y modifica `PANEL_ITEMS`. Cada ítem tiene este formato:

```python
("📦 Requirements", "Descargar", "https://tu-link.com"),
```

- **Primer texto:** nombre del campo (puedes poner emojis al frente).
- **Segundo texto:** subtítulo (ej. "Descargar" o la versión del archivo).
- **Tercer texto:** el enlace URL (se muestra en azul, como en la foto).

Puedes agregar, quitar o reordenar ítems libremente. El color del embed está en `PANEL_COLOR` (por defecto amarillo/dorado).

## 6.4 Enlaces decorados

### Decoración automática

Si alguien pega **solo un enlace** en el chat, el bot borra el mensaje y lo vuelve a publicar como embed con botón. Se controla con:

```env
AUTOLINK_ENABLED=true
```

Ponlo en `false` para desactivarlo. El bot necesita permiso **Gestionar mensajes** para borrar el original; si no lo tiene, igual publica el embed decorado.

`/link` publica cualquier URL como un embed con color, dominio, plataforma detectada y un botón **Abrir enlace**.

```
/link url:https://youtube.com/watch?v=xxx titulo:Mi video descripcion:Míralo aquí color:rojo
/link url:https://github.com/ejemplo titulo:Repositorio color:verde imagen:https://ejemplo.com/img.png
```

Colores disponibles: `azul`, `verde`, `rojo`, `morado`, `naranja`, `dorado`, `rosa`.

Con prefijo: `!link https://ejemplo.com "Mi título" "Descripción" azul`

### `/embed` — embeds decorados como en la foto

Crea un embed personalizado con título, descripción, campos con iconos, imagen y botón. Los campos van en formato `Nombre|Valor`.

```
/embed titulo:⚡ DESCARGAS — ARCHIVOS OFICIALES descripcion:Descarga el panel y emuladores oficiales abajo 👇 color:azul imagen:https://ejemplo.com/imagen.png campo1:🖥️ Emuladores|BlueStacks 5.22.85 campo2:🔥 Juego|Free Fire Normal campo3:🛡️ Sistema & Fixes|Problemas y Soluciones url_boton:https://ejemplo.com texto_boton:Descargar
```

Con prefijo:

```
!embed "⚡ DESCARGAS — ARCHIVOS OFICIALES" "Descarga el panel 👇" azul "https://img.png" "🖥️ Emuladores|BlueStacks" "🔥 Juego|Free Fire" "🛡️ Sistema|Fixes" "https://ejemplo.com" "Descargar"
```

Esto reproduce el estilo de la imagen: título con icono, descripción, campos con emojis, imagen grande y botón.

## 6.5 Protección anti-raid

El bot expulsa automáticamente a quien cree **5 canales, roles o invitaciones en menos de 10 segundos** (valores ajustables en `.env`).

```env
ANTIRAID_ENABLED=true
ANTIRAID_LIMIT=5
ANTIRAID_WINDOW=10
ANTIRAID_EXEMPT_IDS=
```

- **No se aplica** al dueño del servidor, administradores, gestores de servidor, bots ni a los IDs puestos en `ANTIRAID_EXEMPT_IDS` (separados por comas).
- Necesita el permiso **Expulsar miembros** y que el rol del bot esté por encima del rol del miembro.
- Para detectar creación de roles con precisión, conviene darle al bot el permiso **Ver registro de auditoría**.
- Cada expulsión se anuncia en el canal del sistema del servidor.
- Consulta el estado con `/antiraid`.

## 6.6 Descripción en el Portal de Desarrolladores

El texto que se muestra en la página del bot en Discord **no** se configura por código. Cópialo desde aquí:

> https://discord.com/developers/applications → tu aplicación → pestaña **Bot** → campo **Description**:

```text
Server Security — Protege y gestiona tu servidor de Discord con moderación, utilidades y entretenimiento. Usa `/ayuda` para ver la lista completa de comandos.
```

También puedes pegar una versión corta en **Información general → Descripción** de la aplicación:

```text
Server Security — Protege y gestiona tu servidor de Discord con moderación, utilidades y entretenimiento. Usa `/ayuda` para más detalles.
```

Para cambiar el texto que aparece **dentro** de Discord, edita `DESCRIPCION_BOT` y `NOMBRE_BOT` en `config.py` y reinicia el bot.

## Estructura del proyecto

```
Bot Discord/
├── bot.py              # Entrada principal, intents y carga de cogs
├── config.py           # Lee .env
├── .env                # Tu token (no compartir)
├── requirements.txt
├── cogs/               # Comandos y eventos (agrega aquí tus módulos)
│   ├── general.py
│   ├── moderacion.py
│   ├── utilidades.py
│   ├── diversion.py
│   └── eventos.py
└── utils/
    ├── embeds.py       # Colores/estilos de embeds
    └── storage.py      # Guardado en JSON
```

## Solución de problemas

- **"Configura DISCORD_TOKEN..."** → revisa que `.env` exista y tenga el token sin comillas ni espacios de más.
- **Los comandos slash no aparecen** → asegúrate de haber invitado al bot con el scope `applications.commands` (usa este enlace: https://discord.com/oauth2/authorize?client_id=1572365154883207258&scope=bot+applications.commands&permissions=1099511982150). Para que aparezcan **al instante**, pon el ID de tu servidor en `TEST_GUILD_ID` dentro de `.env` y reinicia. Para obtener el ID: Discord → Configuración de usuario → Avanzado → activa *Modo desarrollador*, luego clic derecho en el servidor → *Copiar ID de servidor*.
- **"No pasó nada" al iniciar** → la ventana de la terminal debe permanecer abierta mientras quieras que el bot esté en línea. Confirma que veas la línea `Conectado como ...`. Luego comprueba en Discord que el bot aparece **en línea** dentro de tu servidor (no solo en la lista de amigos).
- **El bot no responde mensajes con prefijo** → activa **Message Content Intent** en el Portal de Desarrolladores.
- **Error de permisos al moderar** → el rol del bot debe estar **arriba** del rol del miembro al que quieres sancionar, y tener los permisos correspondientes.
