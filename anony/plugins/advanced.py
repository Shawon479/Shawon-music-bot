# Copyright (c) 2025 Shawon
# Licensed under the MIT License.
# This file is part of Shawon

import asyncio
from pyrogram import filters, types, errors
from anony import app, db, lang

@app.on_message(filters.command(["gban", "globalban"]) & app.sudoers)
@lang.language()
async def gban_user(_, message: types.Message):
    if not message.reply_to_message:
        if len(message.command) < 2:
            return await message.reply_text("Please reply to a user or provide a User ID to GBan.")
        user_id = message.command[1]
    else:
        user_id = message.reply_to_message.from_user.id

    try:
        user_id = int(user_id)
        user = await app.get_users(user_id)
    except Exception:
        return await message.reply_text("Invalid User ID.")

    if user.id == app.owner:
        return await message.reply_text("I cannot GBan the owner.")
    if user.id in app.sudoers:
        return await message.reply_text("I cannot GBan a sudo user.")

    reason = message.text.split(None, 2)[2] if len(message.command) > 2 else "No reason provided."
    
    await db.add_gban(user.id, reason)
    app.bl_users.add(user.id)
    
    chats = await db.get_chats()
    sent = await message.reply_text(f"GBanning {user.mention} in {len(chats)} groups...")
    
    banned = 0
    for chat_id in chats:
        try:
            await app.ban_chat_member(chat_id, user.id)
            banned += 1
            await asyncio.sleep(0.1)
        except errors.FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            continue
            
    await sent.edit_text(f"Successfully GBanned {user.mention} in {banned} groups with reason: {reason}")


@app.on_message(filters.command(["ungban"]) & app.sudoers)
@lang.language()
async def ungban_user(_, message: types.Message):
    if not message.reply_to_message:
        if len(message.command) < 2:
            return await message.reply_text("Please reply to a user or provide a User ID to un-GBan.")
        user_id = message.command[1]
    else:
        user_id = message.reply_to_message.from_user.id

    try:
        user_id = int(user_id)
    except ValueError:
        return await message.reply_text("Invalid User ID.")

    await db.del_gban(user_id)
    app.bl_users.discard(user_id)
    
    chats = await db.get_chats()
    sent = await message.reply_text(f"Un-GBanning user in {len(chats)} groups...")
    
    unbanned = 0
    for chat_id in chats:
        try:
            await app.unban_chat_member(chat_id, user_id)
            unbanned += 1
            await asyncio.sleep(0.1)
        except Exception:
            continue
            
    await sent.edit_text(f"Successfully un-GBanned user in {unbanned} groups.")

@app.on_message(filters.command(["stats"]) & app.sudoers)
async def stats_command(_, message: types.Message):
    users = len(await db.get_users())
    chats = len(await db.get_chats())
    sudoers = len(await db.get_sudoers())
    gbans = len(await db.get_gbans())
    
    text = (
        f"📊 **{app.name} System Stats**\n\n"
        f"👤 **Total Users:** {users}\n"
        f"📢 **Total Chats:** {chats}\n"
        f"🛡️ **Sudo Users:** {sudoers}\n"
        f"🚫 **GBanned Users:** {gbans}\n\n"
        f"🎙️ **Active Calls:** {len(db.active_calls)}"
    )
    await message.reply_text(text)


@app.on_message(filters.command(["users"]) & filters.user(app.owner))
async def list_users(_, message: types.Message):
    users = await db.get_users()
    if not users:
        return await message.reply_text("No users found.")
    
    msg = "**List of Users:**\n\n"
    for user_id in users[:50]: # Limit msg length
        msg += f"- `{user_id}`\n"
    
    if len(users) > 50:
        msg += f"\nAnd {len(users) - 50} more..."
        
    await message.reply_text(msg)


@app.on_message(filters.command(["chats"]) & filters.user(app.owner))
async def list_chats(_, message: types.Message):
    chats = await db.get_chats()
    if not chats:
        return await message.reply_text("No chats found.")
    
    msg = "**List of Chats:**\n\n"
    for chat_id in chats[:50]:
        msg += f"- `{chat_id}`\n"
        
    if len(chats) > 50:
        msg += f"\nAnd {len(chats) - 50} more..."
        
    await message.reply_text(msg)

