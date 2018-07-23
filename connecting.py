from telethon import TelegramClient, sync
from config import API_HASH, API_ID, PHONE

def connect_client():
    # Connect the client
    client = TelegramClient('testing', API_ID, API_HASH)
    # authorize
    client.start(PHONE)
    return client
