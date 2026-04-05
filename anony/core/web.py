# Copyright (c) 2025 Shawon
# Licensed under the MIT License.
# This file is part of Shawon

import os
import time
import psutil
import uvicorn
import asyncio
from typing import Union
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pyrogram.types import ChatPrivileges

from anony import db, config, logger, app, boot

web_app = FastAPI()
templates = Jinja2Templates(directory="anony/core/templates")

# Simple session management
web_app.add_middleware(SessionMiddleware, secret_key=config.API_HASH or "secret")

def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated", False)

@web_app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if not is_authenticated(request):
        return templates.TemplateResponse("login.html", {"request": request})
    
    # Gathering Stats
    users_count = len(await db.get_users())
    chats_count = len(await db.get_chats())
    sudoers_count = len(await db.get_sudoers())
    gbans_count = len(await db.get_gbans())
    calls_count = len(db.active_calls)
    
    # System Info
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent
    uptime_seconds = int(time.time() - boot)
    uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"

    stats = {
        "users": users_count,
        "chats": chats_count,
        "sudoers": sudoers_count,
        "gbans": gbans_count,
        "calls": calls_count
    }
    
    system = {
        "cpu": cpu_usage,
        "ram": ram_usage,
        "disk": disk_usage,
        "uptime": uptime_str,
        "auto_leave": config.AUTO_LEAVE,
        "auto_end": config.AUTO_END
    }

    
    sudo_users = await db.get_sudoers()
    all_users = await db.get_users()
    all_chats = await db.get_chats()
    active_vcs = []

    from anony import anon
    for chat_id, status in db.active_calls.items():
        try:
            chat = await app.get_chat(chat_id)
            active_vcs.append({
                "id": chat_id, 
                "title": chat.title or "Unknown",
                "playing": bool(status)
            })
        except Exception:
            active_vcs.append({
                "id": chat_id, 
                "title": "Encrypted Chat",
                "playing": bool(status)
            })

    formatted_logs = []
    for log in await db.get_audit_logs(40):
        action = log["action"]
        u_id = log["user_id"]
        c_id = log["chat_id"]
        
        target = f"Chat: {c_id}" if c_id else "SYSTEM"
        performer = f"User: {u_id}" if u_id else "DASHBOARD"
        
        # Optimization: We could cache these, but for now we just show IDs or common names
        if u_id == config.OWNER_ID: performer = "OWNER"
        
        formatted_logs.append({
            "id": log["id"],
            "timestamp": datetime.fromtimestamp(log["timestamp"]).strftime("%d/%m %H:%M"),
            "action": action,
            "performer": performer,
            "target": target
        })
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "system": system,
        "sudo_users": sudo_users,
        "all_users": all_users,
        "all_chats": all_chats,
        "audit_logs": formatted_logs,
        "active_vcs": active_vcs
    })


@web_app.post("/gban")
async def gban(request: Request, user_id: int = Form(...)):
    if not is_authenticated(request): return RedirectResponse(url="/", status_code=303)
    await db.add_gban(user_id, "Banned From Web Panel")
    app.bl_users.add(user_id)
    await db.add_audit_log(f"GBANNED: {user_id}")
    return RedirectResponse(url="/?success=gban", status_code=303)


@web_app.post("/ungban")
async def ungban(request: Request, user_id: int = Form(...)):
    if not is_authenticated(request): return RedirectResponse(url="/", status_code=303)
    await db.del_gban(user_id)
    app.bl_users.discard(user_id)
    return RedirectResponse(url="/?success=ungban", status_code=303)


@web_app.post("/stop-stream")
async def stop_stream(request: Request, chat_id: int = Form(...)):
    if not is_authenticated(request): return RedirectResponse(url="/", status_code=303)
    from anony import anon
    await anon.stop(chat_id)
    await db.add_audit_log(f"MANUALLY STOPPED STREAM", chat_id=chat_id)
    return RedirectResponse(url="/", status_code=303)


@web_app.post("/skip-stream")
async def skip_stream(request: Request, chat_id: int = Form(...)):
    if not is_authenticated(request): return RedirectResponse(url="/", status_code=303)
    from anony import anon
    await anon.play_next(chat_id)
    await db.add_audit_log(f"MANUALLY SKIPPED STREAM", chat_id=chat_id)
    return RedirectResponse(url="/", status_code=303)


@web_app.post("/pause-stream")
async def pause_stream(request: Request, chat_id: int = Form(...)):
    if not is_authenticated(request): return RedirectResponse(url="/", status_code=303)
    from anony import anon
    await anon.pause(chat_id)
    await db.add_audit_log(f"MANUALLY PAUSED STREAM", chat_id=chat_id)
    return RedirectResponse(url="/", status_code=303)


@web_app.post("/resume-stream")
async def resume_stream(request: Request, chat_id: int = Form(...)):
    if not is_authenticated(request): return RedirectResponse(url="/", status_code=303)
    from anony import anon
    await anon.resume(chat_id)
    await db.add_audit_log(f"MANUALLY RESUMED STREAM", chat_id=chat_id)
    return RedirectResponse(url="/", status_code=303)



@web_app.get("/logs", response_class=PlainTextResponse)

async def get_logs(request: Request):
    if not is_authenticated(request):
        return "Unauthorized"
    
    if os.path.exists("log.txt"):
        with open("log.txt", "r") as f:
            lines = f.readlines()
            return "".join(lines[-100:]) # Return last 100 lines
    return "Log file not found."

@web_app.get("/download-db")
async def download_db(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    
    db_path = "database.db"
    if os.path.exists(db_path):
        return FileResponse(db_path, media_type="application/x-sqlite3", filename="backup.db")
    return {"error": "Database file not found."}

@web_app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == config.WEB_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/?error=1", status_code=303)

@web_app.post("/remote-admin")
async def remote_admin(
    request: Request, 
    user_id: str = Form(...), 
    chat_id: int = Form(...), 
    action: str = Form(...)
):
    if not is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    
    try:
        # Resolve user_id (it could be username or ID)
        try:
            target_user = int(user_id)
        except ValueError:
            user = await app.get_users(user_id)
            target_user = user.id

        if action == "ban":
            await app.ban_chat_member(chat_id, target_user)
            logger.info(f"Remote BAN: {target_user} in {chat_id}")
            await db.add_audit_log(f"Remote Banned User: {target_user}", chat_id=chat_id)
        elif action == "kick":
            await app.ban_chat_member(chat_id, target_user)
            await app.unban_chat_member(chat_id, target_user)
            logger.info(f"Remote KICK: {target_user} in {chat_id}")
            await db.add_audit_log(f"Remote Kicked User: {target_user}", chat_id=chat_id)
        elif action == "mute":
            from pyrogram.types import ChatPermissions
            await app.restrict_chat_member(chat_id, target_user, ChatPermissions())
            logger.info(f"Remote MUTE: {target_user} in {chat_id}")
            await db.add_audit_log(f"Remote Muted User: {target_user}", chat_id=chat_id)

        elif action == "unban":
            await app.unban_chat_member(chat_id, target_user)
            logger.info(f"Remote UNBAN: {target_user} in {chat_id}")
        elif action == "unmute":
            from pyrogram.types import ChatPermissions
            await app.restrict_chat_member(chat_id, target_user, ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            ))
            logger.info(f"Remote UNMUTE: {target_user} in {chat_id}")
        elif action == "promote":
            await app.promote_chat_member(
                chat_id, target_user,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=False,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                )
            )
            logger.info(f"Remote PROMOTE: {target_user} in {chat_id}")
            await db.add_audit_log(f"Remote Promoted {target_user}", chat_id=chat_id)
            
    except Exception as e:

        logger.error(f"Remote Admin Error: {e}")
        return RedirectResponse(url=f"/?error={e}", status_code=303)
        
    return RedirectResponse(url="/?success=1", status_code=303)

@web_app.post("/add-sudo")
async def add_sudo(request: Request, user_id: int = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    await db.add_sudo(user_id)
    app.sudoers_set.add(user_id)
    await db.add_audit_log(f"Added Sudo User: {user_id}")
    return RedirectResponse(url="/", status_code=303)



@web_app.post("/del-sudo")
async def del_sudo(request: Request, user_id: int = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    await db.del_sudo(user_id)
    app.sudoers_set.discard(user_id)
    return RedirectResponse(url="/", status_code=303)


@web_app.post("/broadcast")
async def broadcast(request: Request, message: str = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    
    logger.info("Broadcast requested from web panel: %s...", message[:50])
    await db.add_audit_log("Initiated Web Broadcast")
    asyncio.create_task(send_broadcast(message))
    return RedirectResponse(url="/", status_code=303)


async def send_broadcast(message: str):
    chats = await db.get_chats()
    sent = 0
    for chat in chats:
        try:
            await app.send_message(chat, message)
            sent += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.debug("Failed to send broadcast to %s: %s", chat, e)
    logger.info("Web broadcast finished: %d messages sent.", sent)

@web_app.post("/restart")
async def restart(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    logger.info("Restart requested from web panel.")
    os._exit(0)

@web_app.post("/toggle")
async def toggle_conf(request: Request, key: str = Form(...)):
    if not is_authenticated(request): return RedirectResponse(url="/", status_code=303)
    if key == "auto_leave":
        config.AUTO_LEAVE = not config.AUTO_LEAVE
    elif key == "auto_end":
        config.AUTO_END = not config.AUTO_END
    return RedirectResponse(url="/", status_code=303)


@web_app.post("/clean")
async def clean_cache(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    # Clean logic (e.g. removing downloads)
    files = ["downloads", "cache"]
    for folder in files:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
            os.makedirs(folder)
    logger.info("Cache cleaned from web panel.")
    return RedirectResponse(url="/", status_code=303)


async def start_web():
    logger.info("Starting Web Dashboard on port %d", config.PORT)
    cfg = uvicorn.Config(web_app, host="0.0.0.0", port=config.PORT, log_level="error")
    server = uvicorn.Server(cfg)
    await server.serve()
