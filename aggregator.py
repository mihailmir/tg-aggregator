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
    reply_to = None
    message = event.message
    channel_id = int(f"-100{message.peer_id.channel_id}")
    destination_channel = int(config.channels.get(str(channel_id)) or config.defaultDestinationChannel)
    if message.media:
        media_data = await client.download_media(message.media, f'./media/file{get_extension(message.media)}')
    if message.reply_to and message.reply_to.reply_to_msg_id:
        original_parent_message = await client.get_messages(channel_id, ids=message.reply_to.reply_to_msg_id)
        parent_messages = await client.get_messages(destination_channel, search=original_parent_message.message, limit=1)
        if parent_messages:
            reply_to = parent_messages[0].id

    await bot.send_message(destination_channel, message, link_preview=False, file=media_data, reply_to=reply_to, )

with client:
    client.run_until_disconnected()

with bot:
    bot.run_until_disconnected()
