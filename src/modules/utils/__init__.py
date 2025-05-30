#  Copyright (c) 2025 AshokShau
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the TgMusicBot project. All rights reserved where applicable.

__all__ = [
        "Filter",
        "sec_to_min",
        "get_audio_duration",
        "PlayButton",
        "PauseButton",
        "ResumeButton",
        "SupportButton",
        "send_logger"
]

import asyncio
import json

from pytdbot import Client, types

import config
from ._filters import Filter
from .buttons import PlayButton, PauseButton, ResumeButton, SupportButton
from ...logger import LOGGER
from ...platforms.dataclass import CachedTrack


def sec_to_min(seconds):
    """Convert seconds to minutes:seconds format."""
    try:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}:{remaining_seconds:02}"
    except Exception as e:
        LOGGER.warning(f"Failed to convert seconds to minutes:seconds format: {e}")
        return None


async def send_logger(client: Client, chat_id, song: CachedTrack):
    if not chat_id or not song or chat_id == config.LOGGER_ID or config.LOGGER_ID == 0:
        return

    text = (
        f"<b>Song Playing</b> in <code>{chat_id}</code>\n\n"
        f"▶️ <b>Now Playing:</b> <a href='{song.url}'>{song.name}</a>\n\n"
        f"• <b>Duration:</b> {sec_to_min(song.duration)}\n"
        f"• <b>Requested by:</b> {song.user}\n"
        f"• <b>Platform:</b> {song.platform}"
    )

    msg = await client.sendTextMessage(config.LOGGER_ID, text, disable_web_page_preview=True, disable_notification=True)
    if isinstance(msg, types.Error):
        LOGGER.error(f"Error sending message: {msg}")
    return

async def get_audio_duration(file_path):
    try:
        proc = await asyncio.create_subprocess_exec(
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        data = json.loads(stdout)
        duration = float(data['format']['duration'])
        return int(duration)
    except Exception as e:
        LOGGER.warning(f"Failed to get audio duration using ffprobe: {e}")
        return 0
