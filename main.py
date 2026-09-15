import asyncio

import discord
from discord.ext import commands
import pyttsx3
import requests
from bs4 import BeautifulSoup


TOKEN = "AGREGA TU TOKEN AQUÍ"

URL_HABITOS = "https://joaquin31707.github.io/"

URL_OMS = "https://www.who.int/es/news-room/fact-sheets/detail/climate-change-and-health"


intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


servidores_saludados = set()


def speak(texto, volumen, genero):
    engine = pyttsx3.init()

    engine.setProperty("rate", 125)
    engine.setProperty("volume", volumen / 100)

    voices = engine.getProperty("voices")

    if genero == 0 and len(voices) > 0:
        engine.setProperty("voice", voices[0].id)

    elif genero == 2 and len(voices) > 2:
        engine.setProperty("voice", voices[2].id)

    engine.say(texto)

    engine.runAndWait()


def texto_bienvenida():
    return (
        "Hola. Soy EcoGuía. "
        "Escribe !start para comenzar."
    )


def texto_inicio():
    return (
        "Bienvenido. Ahora escribe !funciones "
        "para conocer lo que puedo hacer."
    )


def texto_funciones():
    return (
        "Funciones disponibles: "
        "Le recomendamos que empieze con !porqueexisto, después use !fact, "
        "luego !soluciones y finalmente !habitos para una mejor experiencia."
    )


async def enviar_bienvenida(guild):
    canal = guild.system_channel

    if canal is not None:
        permisos = canal.permissions_for(guild.me)

        if not permisos.send_messages:
            canal = None

    if canal is None:
        for posible_canal in guild.text_channels:
            permisos = posible_canal.permissions_for(guild.me)

            if permisos.send_messages:
                canal = posible_canal
                break

    if canal is not None:
        await canal.send(
            texto_bienvenida()
        )


@bot.event
async def on_ready():
    print(
        "Bot conectado como "
        + str(bot.user)
    )

    for guild in bot.guilds:
        if guild.id not in servidores_saludados:
            await enviar_bienvenida(guild)
            servidores_saludados.add(guild.id)


@bot.event
async def on_guild_join(guild):
    await enviar_bienvenida(guild)
    servidores_saludados.add(guild.id)


@bot.command()
async def start(ctx):
    await ctx.send(
        texto_inicio()
    )


@bot.command()
async def funciones(ctx):
    await ctx.send(
        texto_funciones()
    )


@bot.command()
async def porqueexisto(ctx):
    await ctx.send(
        "EcoGuía existe para ayudar a las personas a conocer el cambio climático "
        "y aprender acciones sencillas para cuidar la Tierra."
    )


@bot.command()
async def soluciones(ctx):
    await ctx.send(
        "Soluciones: Usa menos plástico, recicla, ahorra agua y energía, "
        "Camina o usa bicicleta, evita desperdiciar comida y cuida los árboles. "
        "Pero también puedes encontrar más soluciones en la página de hábitos "
        "sostenibles con !habitos."
    )


@bot.command()
async def habitos(ctx):
    await ctx.send(
        "Completa tu chequeo diario de hábitos aquí: "
        + URL_HABITOS
    )


@bot.command()
async def fact(ctx):

    def es_el_usuario(mensaje):
        return (
            mensaje.author == ctx.author
            and mensaje.channel == ctx.channel
        )


    await ctx.send(
        "¿Qué volumen deseas? Escribe un número entre 0 y 100."
    )


    try:
        respuesta = await bot.wait_for(
            "message",
            check=es_el_usuario,
            timeout=30
        )

        volumen = int(
            respuesta.content.strip()
        )

    except ValueError:
        await ctx.send(
            "Debes escribir solamente un número entre 0 y 100."
        )
        return

    except asyncio.TimeoutError:
        await ctx.send(
            "Se acabó el tiempo. Usa !fact otra vez."
        )
        return


    if volumen < 0 or volumen > 100:
        await ctx.send(
            "El volumen debe estar entre 0 y 100."
        )
        return


    await ctx.send(
        "¿Qué voz deseas? Escribe 0 para voz femenina o 2 para voz masculina."
    )


    try:
        respuesta = await bot.wait_for(
            "message",
            check=es_el_usuario,
            timeout=30
        )

        genero = int(
            respuesta.content.strip()
        )

    except ValueError:
        await ctx.send(
            "Debes escribir 0 para voz femenina o 2 para voz masculina."
        )
        return

    except asyncio.TimeoutError:
        await ctx.send(
            "Se acabó el tiempo. Usa !fact otra vez."
        )
        return


    if genero not in [0, 2]:
        await ctx.send(
            "Debes escribir 0 para voz femenina o 2 para voz masculina."
        )
        return


    try:
        response = requests.get(
            URL_OMS,
            timeout=10
        )


        if response.status_code != 200:
            await ctx.send(
                "No pude obtener la información de la OMS."
            )
            return


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        parrafos = soup.find_all("p")

        textos = []


        for parrafo in parrafos:

            texto = parrafo.get_text(
                " ",
                strip=True
            )


            if len(texto) > 80:
                textos.append(texto)


        if len(textos) == 0:
            await ctx.send(
                "No pude encontrar información en la página de la OMS."
            )
            return


        hecho_espanol = textos[0]


        if len(hecho_espanol) > 300:
            hecho_espanol = hecho_espanol[:300] + "..."


        await ctx.send(
            "Dato interesante de la OMS: "
            + hecho_espanol
        )


        await asyncio.to_thread(
            speak,
            hecho_espanol,
            volumen,
            genero
        )


        await ctx.send(
            "Si quieres conocer más, entra a este sitio web: "
            + URL_OMS
        )


    except requests.RequestException:
        await ctx.send(
            "No pude conectarme a la página de la OMS. "
            "Inténtalo más tarde."
        )


bot.run(TOKEN)
