# Copyright (c) 2025 Shawon
# Licensed under the MIT License.
# This file is part of Shawon

import sqlite3
import aiosqlite
from random import randint
from time import time
from typing import List, Set, Union, Optional

from anony import config, logger, userbot


class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

        # Caches
        self.admin_list = {}
        self.active_calls = {}
        self.admin_play = []
        self.blacklisted = []
        self.cmd_delete = []
        self.loop = {}
        self.notified = []
        self.logger_status = False
        self.assistant = {}
        self.auth = {}
        self.chats = []
        self.users = []
        self.sudoers = []
        self.lang = {}


    async def connect(self) -> None:
        """Initialize the SQLite database and create tables."""
        try:
            start = time()
            self._conn = await aiosqlite.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            await self._create_tables()
            logger.info(f"Database connection successful. ({time() - start:.2f}s)")
            await self.load_cache()
        except Exception as e:
            logger.exception("Database connection failed")
            raise SystemExit(f"Database connection failed: {type(e).__name__}") from e

    async def _create_tables(self) -> None:
        """Create necessary tables if they don't exist."""
        queries = [
            "CREATE TABLE IF NOT EXISTS auth (chat_id INTEGER, user_id INTEGER, PRIMARY KEY (chat_id, user_id))",
            "CREATE TABLE IF NOT EXISTS assistant (chat_id INTEGER PRIMARY KEY, num INTEGER)",
            "CREATE TABLE IF NOT EXISTS blacklist_chats (chat_id INTEGER PRIMARY KEY)",
            "CREATE TABLE IF NOT EXISTS blacklist_users (user_id INTEGER PRIMARY KEY)",
            "CREATE TABLE IF NOT EXISTS chats (chat_id INTEGER PRIMARY KEY, cmd_delete BOOLEAN DEFAULT 0, admin_play BOOLEAN DEFAULT 1)",
            "CREATE TABLE IF NOT EXISTS lang (chat_id INTEGER PRIMARY KEY, lang TEXT)",
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)",
            "CREATE TABLE IF NOT EXISTS sudoers (user_id INTEGER PRIMARY KEY)",
            "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)",
            "CREATE TABLE IF NOT EXISTS gbans (user_id INTEGER PRIMARY KEY, reason TEXT)",
            "CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, user_id INTEGER, chat_id INTEGER, timestamp REAL)"
        ]


        for query in queries:
            await self._conn.execute(query)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            logger.info("Database connection closed.")

    async def execute(self, query: str, *args):
        async with self._conn.execute(query, args) as cursor:
            await self._conn.commit()
            return cursor

    async def fetchall(self, query: str, *args):
        async with self._conn.execute(query, args) as cursor:
            return await cursor.fetchall()

    async def fetchone(self, query: str, *args):
        async with self._conn.execute(query, args) as cursor:
            return await cursor.fetchone()

    # CACHE METHODS (Same as original)
    async def get_call(self, chat_id: int) -> bool:
        return chat_id in self.active_calls

    async def add_call(self, chat_id: int) -> None:
        self.active_calls[chat_id] = 1

    async def remove_call(self, chat_id: int) -> None:
        self.active_calls.pop(chat_id, None)

    async def playing(self, chat_id: int, paused: bool = None) -> Union[bool, None]:
        if paused is not None:
            self.active_calls[chat_id] = int(not paused)
        return bool(self.active_calls.get(chat_id, 0))

    async def get_admins(self, chat_id: int, reload: bool = False) -> List[int]:
        from anony.helpers._admins import reload_admins
        if chat_id not in self.admin_list or reload:
            self.admin_list[chat_id] = await reload_admins(chat_id)
        return self.admin_list[chat_id]

    async def get_loop(self, chat_id: int) -> int:
        return self.loop.get(chat_id, 0)

    async def set_loop(self, chat_id: int, count: int) -> None:
        self.loop[chat_id] = count

    # AUTH METHODS
    async def _get_auth(self, chat_id: int) -> Set[int]:
        if chat_id not in self.auth:
            rows = await self.fetchall("SELECT user_id FROM auth WHERE chat_id = ?", chat_id)
            self.auth[chat_id] = {row['user_id'] for row in rows}
        return self.auth[chat_id]

    async def is_auth(self, chat_id: int, user_id: int) -> bool:
        return user_id in await self._get_auth(chat_id)

    async def add_auth(self, chat_id: int, user_id: int) -> None:
        users = await self._get_auth(chat_id)
        if user_id not in users:
            users.add(user_id)
            await self.execute("INSERT OR IGNORE INTO auth (chat_id, user_id) VALUES (?, ?)", chat_id, user_id)

    async def rm_auth(self, chat_id: int, user_id: int) -> None:
        users = await self._get_auth(chat_id)
        if user_id in users:
            users.discard(user_id)
            await self.execute("DELETE FROM auth WHERE chat_id = ? AND user_id = ?", chat_id, user_id)

    # ASSISTANT METHODS
    async def set_assistant(self, chat_id: int) -> int:
        num = randint(1, len(userbot.clients))
        await self.execute("INSERT OR REPLACE INTO assistant (chat_id, num) VALUES (?, ?)", chat_id, num)
        self.assistant[chat_id] = num
        return num

    async def get_assistant(self, chat_id: int):
        from anony import anon
        if chat_id not in self.assistant:
            row = await self.fetchone("SELECT num FROM assistant WHERE chat_id = ?", chat_id)
            num = row['num'] if row else await self.set_assistant(chat_id)
            self.assistant[chat_id] = num
        return anon.clients[self.assistant[chat_id] - 1]

    async def get_client(self, chat_id: int):
        if chat_id not in self.assistant:
            await self.get_assistant(chat_id)
        client_map = {i+1: client for i, client in enumerate(userbot.clients)}
        return client_map.get(self.assistant[chat_id])

    # BLACKLIST METHODS
    async def add_blacklist(self, chat_id: int) -> None:
        if str(chat_id).startswith("-"):
            if chat_id not in self.blacklisted:
                self.blacklisted.append(chat_id)
                await self.execute("INSERT OR IGNORE INTO blacklist_chats (chat_id) VALUES (?)", chat_id)
        else:
            await self.execute("INSERT OR IGNORE INTO blacklist_users (user_id) VALUES (?)", chat_id)

    async def del_blacklist(self, chat_id: int) -> None:
        if str(chat_id).startswith("-"):
            if chat_id in self.blacklisted:
                self.blacklisted.remove(chat_id)
                await self.execute("DELETE FROM blacklist_chats WHERE chat_id = ?", chat_id)
        else:
            await self.execute("DELETE FROM blacklist_users WHERE user_id = ?", chat_id)

    async def get_blacklisted(self, chat: bool = False) -> List[int]:
        if chat:
            if not self.blacklisted:
                rows = await self.fetchall("SELECT chat_id FROM blacklist_chats")
                self.blacklisted = [row['chat_id'] for row in rows]
            return self.blacklisted
        rows = await self.fetchall("SELECT user_id FROM blacklist_users")
        return [row['user_id'] for row in rows]

    # CHAT METHODS
    async def is_chat(self, chat_id: int) -> bool:
        return chat_id in self.chats

    async def add_chat(self, chat_id: int) -> None:
        if not await self.is_chat(chat_id):
            self.chats.append(chat_id)
            await self.execute("INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", chat_id)

    async def rm_chat(self, chat_id: int) -> None:
        if await self.is_chat(chat_id):
            self.chats.remove(chat_id)
            await self.execute("DELETE FROM chats WHERE chat_id = ?", chat_id)

    async def get_chats(self) -> List[int]:
        if not self.chats:
            rows = await self.fetchall("SELECT chat_id FROM chats")
            self.chats = [row['chat_id'] for row in rows]
        return self.chats

    # COMMAND DELETE
    async def get_cmd_delete(self, chat_id: int) -> bool:
        if chat_id not in self.cmd_delete:
            row = await self.fetchone("SELECT cmd_delete FROM chats WHERE chat_id = ?", chat_id)
            if row and row['cmd_delete']:
                self.cmd_delete.append(chat_id)
        return chat_id in self.cmd_delete

    async def set_cmd_delete(self, chat_id: int, delete: bool = False) -> None:
        if delete:
            if chat_id not in self.cmd_delete:
                self.cmd_delete.append(chat_id)
        else:
            if chat_id in self.cmd_delete:
                self.cmd_delete.remove(chat_id)
        await self.execute("INSERT OR REPLACE INTO chats (chat_id, cmd_delete) VALUES (?, ?)", chat_id, int(delete))

    # LANGUAGE METHODS
    async def set_lang(self, chat_id: int, lang_code: str):
        await self.execute("INSERT OR REPLACE INTO lang (chat_id, lang) VALUES (?, ?)", chat_id, lang_code)
        self.lang[chat_id] = lang_code

    async def get_lang(self, chat_id: int) -> str:
        if chat_id not in self.lang:
            row = await self.fetchone("SELECT lang FROM lang WHERE chat_id = ?", chat_id)
            self.lang[chat_id] = row['lang'] if row else config.LANG_CODE
        return self.lang.get(chat_id, config.LANG_CODE)

    # LOGGER METHODS
    async def is_logger(self) -> bool:
        return self.logger_status

    async def get_logger(self) -> bool:
        row = await self.fetchone("SELECT value FROM metadata WHERE key = 'logger'")
        if row:
            self.logger_status = row['value'] == 'True'
        return self.logger_status

    async def set_logger(self, status: bool) -> None:
        self.logger_status = status
        await self.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('logger', ?)", str(status))

    # PLAY MODE METHODS
    async def get_play_mode(self, chat_id: int) -> bool:
        if chat_id not in self.admin_play:
            row = await self.fetchone("SELECT admin_play FROM chats WHERE chat_id = ?", chat_id)
            if row and row['admin_play']:
                self.admin_play.append(chat_id)
        return chat_id in self.admin_play

    async def set_play_mode(self, chat_id: int, remove: bool = False) -> None:
        if remove:
            if chat_id in self.admin_play:
                self.admin_play.remove(chat_id)
        else:
            if chat_id not in self.admin_play:
                self.admin_play.append(chat_id)
        await self.execute("INSERT OR REPLACE INTO chats (chat_id, admin_play) VALUES (?, ?)", chat_id, int(not remove))

    # SUDO METHODS
    async def add_sudo(self, user_id: int) -> None:
        if user_id not in self.sudoers:
            self.sudoers.append(user_id)
            await self.execute("INSERT OR IGNORE INTO sudoers (user_id) VALUES (?)", user_id)

    async def del_sudo(self, user_id: int) -> None:
        if user_id in self.sudoers:
            self.sudoers.remove(user_id)
            await self.execute("DELETE FROM sudoers WHERE user_id = ?", user_id)

    async def get_sudoers(self) -> List[int]:
        if not self.sudoers:
            rows = await self.fetchall("SELECT user_id FROM sudoers")
            self.sudoers = [row['user_id'] for row in rows]
        return self.sudoers

    # USER METHODS
    async def is_user(self, user_id: int) -> bool:
        return user_id in self.users

    async def add_user(self, user_id: int) -> None:
        if not await self.is_user(user_id):
            self.users.append(user_id)
            await self.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", user_id)

    async def rm_user(self, user_id: int) -> None:
        if await self.is_user(user_id):
            self.users.remove(user_id)
            await self.execute("DELETE FROM users WHERE user_id = ?", user_id)

    async def get_users(self) -> List[int]:
        if not self.users:
            rows = await self.fetchall("SELECT user_id FROM users")
            self.users = [row['user_id'] for row in rows]
        return self.users

    # GBAN METHODS
    async def add_gban(self, user_id: int, reason: str = None) -> None:
        await self.execute("INSERT OR REPLACE INTO gbans (user_id, reason) VALUES (?, ?)", user_id, reason)

    async def del_gban(self, user_id: int) -> None:
        await self.execute("DELETE FROM gbans WHERE user_id = ?", user_id)

        rows = await self.fetchall("SELECT user_id FROM gbans")
        return [row['user_id'] for row in rows]

    async def get_gbans(self) -> List[int]:
        rows = await self.fetchall("SELECT user_id FROM gbans")
        return [row['user_id'] for row in rows]


    # AUDIT LOG METHODS
    async def add_audit_log(self, action: str, user_id: int = 0, chat_id: int = 0) -> None:
        await self.execute(
            "INSERT INTO audit_log (action, user_id, chat_id, timestamp) VALUES (?, ?, ?, ?)",
            action, user_id, chat_id, time()
        )

    async def get_audit_logs(self, limit: int = 50) -> List[sqlite3.Row]:
        return await self.fetchall("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", limit)


    async def load_cache(self) -> None:

        from anony import app
        await self.get_chats()
        await self.get_users()
        app.bl_users.update(await self.get_blacklisted())
        await self.get_logger()
        await self.get_sudoers()



        logger.info("Database cache loaded.")
