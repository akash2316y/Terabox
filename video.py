import os
import time
import random
import asyncio
import logging
import requests
import aiohttp
import aiofiles
import subprocess

from datetime import datetime
from dotenv import load_dotenv
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from moviepy.editor import VideoFileClip
import aria2p

# Load environment variables
load_dotenv("config.env")   # <<< Add it here

# Now read your variables
CHNL_BTN = os.getenv("CHNL_BTN", "False").lower() == "true"
AUTH_CHANNEL = os.getenv("AUTH_CHANNEL", "AkashServers")

def generate_thumbnail(video_path: str, output_path: str, time_position: int = 10) -> str:
    try:
        subprocess.run(
            [
                "ffmpeg", "-ss", str(time_position), "-i", video_path,
                "-vframes", "1", "-q:v", "2", "-vf", "scale=320:-1",
                output_path
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        logging.warning(f"Thumbnail generation failed: {e}")
        return None

def format_progress_bar(filename, percentage, done, total_size, status, eta, speed, elapsed, user_mention, user_id, aria2p_gid):
    bar_length = 10
    filled_length = int(bar_length * percentage / 100)
    bar = '★' * filled_length + '☆' * (bar_length - filled_length)

    def format_size(size):
        size = int(size)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 ** 3:
            return f"{size / 1024 ** 2:.2f} MB"
        else:
            return f"{size / 1024 ** 3:.2f} GB"

    def format_time(seconds):
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds} sec"
        elif seconds < 3600:
            return f"{seconds // 60} min"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} hr {minutes} min"

    return (
        f"┏ ғɪʟᴇɴᴀᴍᴇ: {filename}\n"
        f"┠ [{bar}] {percentage:.2f}%\n"
        f"┠ ᴘʀᴏᴄᴇssᴇᴅ: {format_size(done)} ᴏғ {format_size(total_size)}\n"
        f"┠ sᴛᴀᴛᴜs: {status}\n"
        f"┠ sᴘᴇᴇᴅ: {format_size(speed)}/s\n"
        f"┠ ᴇᴛᴀ: {format_time(eta)} | ᴇʟᴀᴘsᴇᴅ: {format_time(elapsed)}\n"
        f"┖ ᴜsᴇʀ: {user_mention} | ɪᴅ: {user_id}"
    )


# Terabox API Details
TERABOX_API_URL = "https://terabox.web.id"
TERABOX_API_TOKEN = "akash_8110231942"
THUMBNAIL = "https://envs.sh/JP6.jpg"
db_channel_id = -1002536904769

downloads_manager = {}

async def download_thumbnail(url: str) -> str:
    """Downloads the thumbnail from a URL and saves it locally."""
    filename = "thumbnail.jpg"
    file_path = os.path.join(os.getcwd(), filename)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to download thumbnail: HTTP {resp.status}")

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(await resp.read())

    return file_path  # Return local file path

async def fetch_json(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async def download(url: str, user_id: int, filename: str, reply_msg, user_mention, file_size: int) -> str:
    sanitized_filename = filename.replace("/", "_").replace("\\", "_")
    file_path = os.path.join(os.getcwd(), sanitized_filename)

    cookies = await fetch_json(f"{TERABOX_API_URL}/url?url={TERABOX_API_TOKEN}")

    download_key = f"{user_id}-{sanitized_filename}"  # Unique key per file
    downloads_manager[download_key] = {"downloaded": 0}

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=900),
        cookies=cookies
    ) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to fetch video: HTTP {resp.status}")

            total_size = int(resp.headers.get("Content-Length", 0)) or file_size  # Ensure file size is correct
            start_time = datetime.now()
            last_update_time = time.time()

            async def progress(current, total):
                nonlocal last_update_time
                percentage = (current / total) * 100 if total else 0
                elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
                speed = current / elapsed_time_seconds if elapsed_time_seconds > 0 else 0
                eta = (total - current) / speed if speed > 0 else 0

                if time.time() - last_update_time > 2:
                    progress_text = format_progress_bar(
                        filename=filename,
                        percentage=percentage,
                        done=current,
                        total_size=total,
                        status="Downloading",
                        eta=eta,
                        speed=speed,
                        elapsed=elapsed_time_seconds,
                        user_mention=user_mention,
                        user_id=user_id,
                        aria2p_gid=""
                    )
                    try:
                        await reply_msg.edit_text(progress_text)
                        last_update_time = time.time()
                    except Exception as e:
                        logging.warning(f"Error updating progress message: {e}")

            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    chunk = await resp.content.read(10 * 1024 * 1024)  # 10MB chunks
                    if not chunk:
                        break
                    if downloads_manager[download_key]["downloaded"] + len(chunk) > total_size:
                        logging.warning(f"Download exceeded expected size for {filename}. Stopping...")
                        break
                    await f.write(chunk)
                    downloads_manager[download_key]['downloaded'] += len(chunk)
                    await progress(downloads_manager[download_key]['downloaded'], total_size)

    downloads_manager.pop(download_key, None)  # Cleanup after completion
    return file_path

async def download_video(url, reply_msg, user_mention, user_id, max_retries=3):
    try:
        logging.info(f"Fetching video info: {url}")

        # Fetch video details
        api_response = await fetch_json(f"{TERABOX_API_URL}/url?url={url}&token={TERABOX_API_TOKEN}")

        if not api_response or not isinstance(api_response, list) or "filename" not in api_response[0]:
            raise Exception("Invalid API response format.")

        # Extract details from response
        data = api_response[0]
        download_link = data["link"] + f"&random={random.randint(1, 10)}"
        video_title = data["filename"]
        file_size = int(data.get("size", 0))  # Convert to int to ensure proper type
        thumb_url = THUMBNAIL  # Use default if missing

        logging.info(f"Downloading: {video_title} | Size: {file_size} bytes")

        if file_size == 0:
            raise Exception("Failed to get file size, download aborted.")

        # Retry logic for robustness
        for attempt in range(1, max_retries + 1):
            try:
                file_path = await asyncio.create_task(download(download_link, user_id, video_title, reply_msg, user_mention, file_size))
                break  # Exit loop if successful
            except Exception as e:
                logging.warning(f"Download failed (Attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise e  # Raise error if all retries fail
                await asyncio.sleep(3)

        # Send completion message
        await reply_msg.edit_text(f"✅ Download Complete!\n📂 {video_title}")
        return file_path, thumb_url, video_title, None  # No duration in response

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        return None, None, None, None

async def upload_video(client, file_path, thumbnail_url, video_title, reply_msg, user_mention, user_id, message):
    try:
        file_size = os.path.getsize(file_path)
        uploaded = 0
        start_time = datetime.now()
        last_update_time = time.time()

        # Step 1: Try downloading the thumbnail from URL
        thumbnail_path = None
        if thumbnail_url:
            try:
                thumbnail_path = await download_thumbnail(thumbnail_url)
            except Exception as e:
                logging.warning(f"Failed to download thumbnail: {e}")
                thumbnail_path = None

        # Step 2: Fallback to generate thumbnail from the video
        if not thumbnail_path:
            thumbnail_path = f"{os.path.splitext(file_path)[0]}_thumb.jpg"
            generated = generate_thumbnail(file_path, thumbnail_path)
            if not generated:
                thumbnail_path = None


        # Step 3: Get video duration (optional - to use in caption)
        video_duration = get_video_duration(file_path)

        async def progress(current, total):
            nonlocal uploaded, last_update_time
            uploaded = current
            percentage = (current / total) * 100
            elapsed_time_seconds = (datetime.now() - start_time).total_seconds()

            if time.time() - last_update_time > 2:
                progress_text = format_progress_bar(
                    filename=video_title,
                    percentage=percentage,
                    done=current,
                    total_size=total,
                    status="Uploading",
                    eta=(total - current) / (current / elapsed_time_seconds) if current > 0 else 0,
                    speed=current / elapsed_time_seconds if current > 0 else 0,
                    elapsed=elapsed_time_seconds,
                    user_mention=user_mention,
                    user_id=user_id,
                    aria2p_gid=""
                )
                try:
                    await reply_msg.edit_text(progress_text)
                    last_update_time = time.time()
                except Exception as e:
                    logging.warning(f"Error updating progress message: {e}")

        # Step 4: Upload video to DB channel
        with open(file_path, 'rb') as file:
            collection_message = await client.send_video(
                chat_id=db_channel_id,
                video=file,
                caption=f"✨ {video_title}\n⏱ Duration: {video_duration} sec\n👤 ʟᴇᴇᴄʜᴇᴅ ʙʏ : {user_mention}\n📥 <b>ʙʏ @Javpostr </b>",
                thumb=thumbnail_path if thumbnail_path else None,
                progress=progress
            )

        # Step 5: Forward to user (copy without forward header)
        copied_msg = await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=db_channel_id,
            message_id=collection_message.id
        )

        # Step 6: Edit with caption and buttons
        caption = f"✨ {video_title}\n⏱ Duration: {video_duration} sec\n👤 ʟᴇᴇᴄʜᴇᴅ ʙʏ : {user_mention}\n📥 <b>ʙʏ @Javpostr </b>"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/{AUTH_CHANNEL}")]]) if CHNL_BTN else None

        await copied_msg.edit_caption(
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
        # Step 5: Cleanup
        try:
            os.remove(file_path)
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        except Exception as e:
            logging.warning(f"Error during file cleanup: {e}")

        try:
            await message.delete()
        except Exception as e:
            logging.warning(f"Failed to delete user message: {e}")

        await asyncio.sleep(5)

        return collection_message.id

    except Exception as e:
        logging.error(f"Error during upload: {e}", exc_info=True)
        return None

def get_video_duration(file_path):
    try:
        clip = VideoFileClip(file_path)
        duration = int(clip.duration)  # seconds mein
        clip.close()
        return duration
    except Exception as e:
        logging.warning(f"Error getting video duration: {e}")
        return 0
