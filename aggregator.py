from telethon import TelegramClient, events
from telethon.utils import get_extension
from python_json_config import ConfigBuilder
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)

config = ConfigBuilder().parse_config('config.json')

client = TelegramClient('anon', config.telegramApiId, config.telegramApiHash)

bot = TelegramClient('bot', config.telegramApiId, config.telegramApiHash).start(bot_token=config.botToken)

# Channels to listen to
target_channels = config.channels.to_dict().keys()


@client.on(events.NewMessage(chats=[int(ch) for ch in target_channels]))
async def message_listener(event):
    logging.info(event.message.to_dict())

    media_data = None
    message = event.message
    message_id = message.id
    message_text = message.message
    channel_id = int(f"-100{message.peer_id.channel_id}")
    destination_channel = config.channels.get(str(channel_id)) or config.defaultDestinationChannel

    channel_data = await client.get_entity(channel_id)

    channel_name = channel_data.title
    url = 'https://t.me/c/' + str(channel_id) + '/' + str(message_id)
    formatted_link = f"**[{channel_name}]({url})**"
    headline = message_text + '\n\n' + formatted_link

    if message.media:
        media_data = await client.download_media(message.media, f'./media/file{get_extension(message.media)}')

    await bot.send_message(int(destination_channel), headline, link_preview=False, file=media_data)

with client:
    client.run_until_disconnected()

with bot:
    bot.run_until_disconnected()
