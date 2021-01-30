import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import os
import time
import asyncio
import pyrogram

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import script

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from plugins.helpers import progress_for_pyrogram

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from PIL import Image
from database.database import *


async def force_name(bot, message):

    await bot.send_message(
        message.reply_to_message.from_user.id,
        "Enter new name for media\n\nNote : Extension not required",
        reply_to_message_id=message.reply_to_message.message_id,
        reply_markup=ForceReply(True)
    )


@Client.on_message(filters.private & filters.reply & filters.text)
async def cus_name(bot, message):
    
    if (message.reply_to_message.reply_markup) and isinstance(message.reply_to_message.reply_markup, ForceReply):
        asyncio.create_task(rename_video(bot, message))     
    else:
        print('No media present')

    
async def rename_video(bot, message):
    
    mssg = await bot.get_messages(
        message.chat.id,
        message.reply_to_message.message_id
    )    
    
    media = mssg.reply_to_message

    
    if media.empty:
        await message.reply_text('Why did you delete that 😕', True)
        return
        
    filetype = media.document or media.video or media.audio or media.voice or media.video_note
    try:
        actualname = filetype.file_name
        splitit = actualname.split(".")
        extension = (splitit[-1])
    except:
        extension = "mp4"

    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=message.reply_to_message.message_id,
        revoke=True
    )

    if message.from_user.id not in Config.BANNED_USERS:
        file_name = message.text
        description = script.CUSTOM_CAPTION_UL_FILE.format(newname=file_name)
        download_location = Config.DOWNLOAD_LOCATION + "/"
