# Copyright (c) 2025 Shawon
# Licensed under the MIT License.
# This file is part of Shawon


import asyncio
import signal
import importlib
from contextlib import suppress

from anony import (anon, app, config, db, logger,
                   stop, thumb, userbot, yt, boot)
from anony.core.web import start_web
from anony.plugins import all_modules


async def idle():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGABRT):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop_event.set)
    await stop_event.wait()

async def main():
    # Start the Web Dashboard FIRST to pass Railway healthchecks immediately
    asyncio.create_task(start_web())

    await db.connect()


    await app.boot()
    try:
        await userbot.boot()
        await anon.boot()
    except Exception as e:
        logger.error(f"Failed to start Assistants/Calls: {e}")
        logger.warning("Bot will run without Voice Chat support.")

    await thumb.start()


    for module in all_modules:
        importlib.import_module(f"anony.plugins.{module}")
    logger.info(f"Loaded {len(all_modules)} modules.")

    if config.COOKIES_URL:
        await yt.save_cookies(config.COOKIES_URL)

    sudoers_list = await db.get_sudoers()
    app.sudoers.update(sudoers_list)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"Loaded {len(app.sudoers)} sudo users.")



    await idle()
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
