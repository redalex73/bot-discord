import requests
from bs4 import BeautifulSoup
import discord
import asyncio

# Configuración
DISCORD_TOKEN = "MTMxMzExODIxODA0NjU0MTg5NQ.Gn1Nvc.IDMyD_UoLxn_H2vBdWM3qGp1OsVuupf-W5d8x8"
DISCORD_GUILD_ID = 1310524831728533584  # Reemplaza con el ID de tu servidor
TWITTER_CHANNEL_ID = 1312107008459145337  # ID del canal de notificaciones de Twitter
INSTAGRAM_CHANNEL_ID = 1312107039660703878  # ID del canal de notificaciones de Instagram
TWITTER_USERNAME = "Crim_Shot"  # Nombre de usuario de Twitter
INSTAGRAM_USERNAME = "crim_shot"  # Nombre de usuario de Instagram

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_tweet = None  # Almacena el último tweet para evitar duplicados
last_instagram_post = None  # Almacena la última publicación de Instagram


# Función para buscar el último tweet
async def fetch_latest_tweet():
    global last_tweet
    while True:
        try:
            url = f"https://twitter.com/{TWITTER_USERNAME}"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            tweets = soup.find_all("div", {"data-testid": "tweet"})

            if tweets:
                latest_tweet = tweets[0].text.strip()
                if latest_tweet != last_tweet:
                    last_tweet = latest_tweet

                    # Envía el tweet al canal de Twitter
                    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
                    if guild:
                        channel = discord.utils.get(guild.channels, id=TWITTER_CHANNEL_ID)
                        if channel:
                            await channel.send(f"Nuevo tweet de @{TWITTER_USERNAME}: {latest_tweet}")
        except Exception as e:
            print(f"Error al buscar tweets: {e}")
        await asyncio.sleep(300)  # Comprobar cada 60 segundos


# Función para buscar la última publicación de Instagram
async def fetch_latest_instagram_post():
    global last_instagram_post
    while True:
        try:
            url = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar publicaciones
            posts = soup.find_all("div", {"class": "v1Nh3 kIKUG _bz0w"})  # Clase contenedora de publicaciones
            if posts:
                latest_post = posts[0].find("a")["href"]  # Extraer enlace de la publicación
                if latest_post != last_instagram_post:
                    last_instagram_post = latest_post

                    # Envía la publicación al canal de Instagram
                    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
                    if guild:
                        channel = discord.utils.get(guild.channels, id=INSTAGRAM_CHANNEL_ID)
                        if channel:
                            post_url = f"https://www.instagram.com{latest_post}"
                            await channel.send(f"Nuevo post de @{INSTAGRAM_USERNAME}: {post_url}")
        except Exception as e:
            print(f"Error al buscar publicaciones de Instagram: {e}")
        await asyncio.sleep(300)  # Comprobar cada 60 segundos


@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
    if guild:
        print(f"Bot activo en el servidor: {guild.name}")
        # Crear tareas para ambas funciones
        client.loop.create_task(fetch_latest_tweet())
        client.loop.create_task(fetch_latest_instagram_post())
    else:
        print("El bot no está en el servidor especificado. Verifica el ID.")

client.run(DISCORD_TOKEN)