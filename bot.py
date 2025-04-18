import requests
import discord
import asyncio
import os
from flask import Flask
from threading import Thread

# Configuración
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
DISCORD_GUILD_ID = int(os.environ['DISCORD_GUILD_ID'])  # Reemplaza con el ID de tu servidor
TWITTER_CHANNEL_ID = int(os.environ['TWITTER_CHANNEL_ID'])  # ID del canal de notificaciones de Twitter
TWITTER_USERNAME = os.environ['TWITTER_USERNAME']  # Nombre de usuario de Twitter

# Clave de Bearer Token de Twitter API y RapidAPI para Instagram
BEARER_TOKEN = os.environ['TWITTER_BEARER_TOKEN']

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_tweet = ""  # Almacena el último tweet para evitar duplicados

# Configuración del servidor HTTP
app = Flask('')

@app.route('/')
def home():
    return "El bot está activo."

def run():
    app.run(host='0.0.0.0', port=8080)  # Puerto 8080

def keep_awake():
    thread = Thread(target=run)
    thread.start()

# Función para enviar mensajes al canal adecuado
async def send_message_to_channel(channel, message):
    if isinstance(channel, discord.TextChannel):
        await channel.send(message)
    else:
        print(f"El canal {channel.name} no es un canal de texto, no se puede enviar el mensaje.")

# Función para buscar el último tweet usando Twitter API
async def fetch_latest_tweet():
    global last_tweet
    while True:
        try:
            # Obtener el user_id de la cuenta objetivo
            user_url = f"https://api.twitter.com/2/users/by/username/{TWITTER_USERNAME}"
            headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
            user_response = requests.get(user_url, headers=headers)
            user_data = user_response.json()

            if 'data' in user_data:
                user_id = user_data['data']['id']

                # Obtener los tweets más recientes de la cuenta
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5"
                tweets_response = requests.get(tweets_url, headers=headers)
                tweets_data = tweets_response.json()

                if 'data' in tweets_data:
                    latest_tweet_data = tweets_data['data'][0]
                    latest_tweet = latest_tweet_data['text'].strip()  # Obtener el texto del tweet
                    tweet_url = f"https://twitter.com/{TWITTER_USERNAME}/status/{latest_tweet_data['id']}"

                    # Verificar si es un retweet
                    if 'referenced_tweets' in latest_tweet_data:
                        tweet_type = "retweet"
                    else:
                        tweet_type = "tweet"

                    if latest_tweet != last_tweet:
                        last_tweet = latest_tweet
                        print(f"Último tweet: {latest_tweet}")  # Depuración

                        # Enviar el tweet al canal de Discord
                        guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
                        if guild:
                            channel = discord.utils.get(guild.channels, id=TWITTER_CHANNEL_ID)
                            if channel:
                                if tweet_type == "retweet":
                                    await send_message_to_channel(channel, f"¡Nuevo retweet de @{TWITTER_USERNAME}!\n{tweet_url}")
                                else:
                                    await send_message_to_channel(channel, f"Nuevo tweet de @{TWITTER_USERNAME}:\n{tweet_url}")
        except Exception as e:
            print(f"Error al buscar tweets: {e}")

        # Esperar 1 minuto antes de comprobar de nuevo
        await asyncio.sleep(120)

# Función para mantener el bot despierto
async def keep_alive():
    while True:
        print("El bot está activo...")  # Imprime en consola cada 60 segundos
        await asyncio.sleep(120)  # Espera 120 segundos

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
    if guild:
        print(f"Bot activo en el servidor: {guild.name}")
        # Crear tareas para las funciones
        client.loop.create_task(fetch_latest_tweet())  # Asegúrate de que esta línea esté correctamente indentada
        client.loop.create_task(fetch_latest_instagram_post())
        client.loop.create_task(keep_alive())  # Llama a la función que mantiene el bot activo
        keep_awake()  # Inicia el servidor HTTP
    else:
        print("El bot no está en el servidor especificado. Verifica el ID.")

client.run(DISCORD_TOKEN)
