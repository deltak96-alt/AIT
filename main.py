
Render-ready single-file FastAPI +

Alogram Telegram bot

Webhook endpoint (uses

WEBHOOK_SECRET)

Auto create DB tables on startup

Handles Render's postgres:// -> postgresql+asyncpg:// driver fix

Uses RENDER EXTERNAL HOSTNAME or WEBHOOK BASE environment var to build webhook URL

How to run locally:

RENDER EXTERNAL HOSTNAME is not set locally set WEBHOOK BASE to your public domain (https://...) or test with ngrok, uvicorn main:apphost 0.0.0.0

--port 8000

Requirements (put in requirements.txt): fastapi uvicorn standard] aiogram>=3.3 SQLAlchemy>=2.0 asyncpg

Deploy notes (Render):

Add environment variables: BOT TOKEN, OWNER ID, DATABASE_URL, WEBHOOK SECRET

Render provides RENDER EXTERNAL HOSTNAME automatically-code will use it

import os import logging from datetime import datetime, timedelta, timezoane fram typing import Optional

from fastapi import FastAPI, Request, HTTPException from aiogram import Bot, Dispatcher from aiogram.types import InlineKeyboard Markup,

InlineKeyboard Button, Update from sqlalchemy.ext.asyncio import create async_engine, async sessionmaker,

AsyncEngine from sqlalchemy.orm import

DeclarativeBase, Mapped, mapped_column from sqlalchemy import BigInteger, String, Integer, DateTime, Boolean, Text, Foreignkey, select, Index

CONFIG

MYANMAR TZ =

timezone(timedelta(hours-6, 30)) BOT TOKEN = os.getenv("BOT_TOKEN") OWNER ID= int(os.getenv("OWNER ID", "0")) DATABASE_URL

os.getenv("DATABASE_URL")

WEBHOOK SECRET =

os.getenv("WEBHOOK SECRET", "change this_secret") WEBHOOK BASE os.getenv("WEBHOOK_BASE") # optional

manual override

small sanity checks

if not BOT TOKEN or not DATABASE URL or OWNER ID 0: raise RuntimeError("Missing BOT_TOKEN,

OWNER ID, or DATABASE_URL")

SQLAlchemy driver fix (Render/Postgres

often gives postgres://)

if DATABASE_URL.startswith("postgres://"): DATABASE URL = DATABASE URL..replace("postgres://",

"postgresql+asyncpg://", 1)

logging.basicConfig(level-logging.INFO)

logger

logging.getLogger("super-bot-final")

DATABASE

class Base(DeclarativeBase): pass

class User(Base): tablename="users" id:

Mapped[int] =

mapped_column(primary_key=True) tg_id: Mapped[int] = mapped column (BigInteger, unique=True, index=True) lang:

Mapped[str] = mapped_column(String(5),

default="MM") stars: Mapped[int] =

mapped column(Integer, default=0)

wallet balance: Mapped[int] =

mapped_column(Integer, default=0)

last_active: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True) ) created_at: Mapped[datetime] =

mapped column(DateTime(timezone=True)

default-lambda:

datetime.now(MYANMAR_TZ)) table_args =

(Index("idx user last active",

"last_active"),)

class Wallet Transaction(Base): tablename= "wallet_transactions" id: Mapped[int] = mapped column(primary_key=True)

user id: Mapped[int]

mapped_column(ForeignKey("users.id"))

amount: Mapped[int] =

mapped_column(Integer) type: Mapped[str] = mapped_column(String(16)) #deposit/withdraw/spend method:

Mapped [Optional[str]] =

mapped_column(String(32)) # KBZPay/

WavePay/Cash created at:

Mapped datetime] =

mapped_column(DateTime(timezone=True)

default-lambda:

datetime.now(MYANMAR_TZ))

class Marketplaceltem(Base): tablename=

"marketplace_items" id: Mapped[int] =

mapped_column(primary_key=True)

seller_id: Mapped[int] =

mapped_column(ForeignKey("users.id"))

title: Mapped[str] =

mapped_column(String(128)) description:

Mapped[str] = mapped column(Text) price: Mapped[int] = mapped_column(Integer)

status: Mapped[str]=

mapped_column(String(12),

default="active") created_at:

Mapped datetime] =

mapped column(DateTime(timezone=True)

default-lambda:

datetime.now(MYANMAR TZ))

class Job(Base): tablename = "jobs" id:

Mapped[int] =

mapped_column(primary_key=True) title: Mapped[str] =

mapped column(String(128)) description:

Mapped[str] = mapped column(Text) type: Mapped(str) mapped_column(String(12))

salary: Mapped Optional[int]]=

mapped_column(Integer) employer_id:

Mapped[Optional[int]] =

mapped column(ForeignKey("users.id")) status: Mapped[str] =

mapped_column(String(12),

default="active") created at:

Mapped[datetime] =>

mapped_column(DateTime(timezone=True)

default-lambda:

datetime.now(MYANMAR TZ))

class Housing (Base): tablename =

"housing" id: Mapped[int] =

mapped_column(primary_key=True)

owner_id: Mapped[int]

mapped_column(ForeignKey("users.id"))

title: Mapped[str] =

mapped_column(String(128)) description:

Mapped[str] = mapped_column(Text) type: Mapped[str] = mapped_column(String(16))

price: Mapped[int] =

mapped_column(Integer) digital contract: Mapped[bool] mapped_column(Boolean, default-False) status: Mapped[str] =

mapped_column(String (12),

default="available") created_at:

Mapped(datetime] =

mapped_column(DateTime(timezone=True)

default-lambda:

datetime.now(MYANMAR TZ))

class ShortVideo(Base): tablename

"short videos" id: Mapped[int] =

mapped_column(primary_key=True) title:

Mapped[str] =

mapped_column(String(128)) url:

Mapped[str] =

mapped_column(String(256)) created at:

Mapped[datetime] =

mapped_column(DateTime(timezone=True)

default-lambda:

datetime.now(MYANMAR_TZ))

class VideoHistory(Base): tablename=

"video_history" id: Mapped[int]

mapped_column(primary key=True)

user_id: Mapped[int] =

mapped_column(ForeignKey("users.id"))

video id: Mapped[int] =

mapped_column (ForeignKey("short_videos.i

d")) watched at: Mapped datetime] =

mapped column(DateTime(timezone=True)

default-lambda:

datetime.now(MYANMAR TZ))

ENGINE

engine: AsyncEngine =

create async engine (DATABASE URL,

echo False, future True,

pool_pre ping=True) Session =

async sessionmaker(engine,

expire on_commit=False)

async def init db(): async with

engine.begin() as conn: await

conn.run_sync(Base

metadata.create_all)

async def ensure_user(tg_id: int) -> User: async with Session() as session: user

await

session.scalar(select(User). where(User.tg_id

tg id)) if not user: user =

User(tg_id=tg_id,

last active datetime.now(MYANMAR TZ))

session.add(user) await session.commit()

else: user.last_active

datetime.now(MYANMAR_TZ) await session.commit() return user

BOT

bot Bot(BOT_TOKEN, parse_mode="HTML") dp = Dispatcher() app = FastAPI()

Feature flags for future-proof modularity

ENABLED_MODULES = { "marketplace": True, "jobs": True, "housing": True,

"wallet": True, "lucky_draw": True, "public_service": True, "education": True, "health": True, "entertainment": True }

T = {"welcome": { "MM": "βύλυς! \nSelect the menu you want. ", "EN": "

Welcome!\nSelect your menu."}}

def main_menu_keyboard(): kb = InlineKeyboard Markup(row_width=2) kb.add(InlineKeyboardButton("

Marketplace",

callback_data="marketplace"),

InlineKeyboard Button(" Jobs",

callback_data="jobs"),

InlineKeyboardButton(" Housing", callback_data="housing"), InlineKeyboard Button(" Weather", callback_data="weather"),

InlineKeyboard Button(" Wallet/Stars", callback_data="wallet"),

InlineKeyboardButton(" Lucky Draw",

callback_data="lucky_draw"), InlineKeyboard Button(" Public Service", callback_data="public_service"),

InlineKeyboard Button(" Education", callback_data="education"), InlineKeyboard Button(" Health/Insurance", callback_data="health"), InlineKeyboardButton(" Short Videos", callback_data="entertainment")) retum kb

HANDLERS

@dp.message() async def message_handler(msg: "types.Message"): user = await

ensure_user(msg.from_user.id) await msg.answer(T["welcome"].get(user.lang, T["welcome"]["MM"]),

reply_markup=main_menu_keyboard())

@dp.callback_query() async def callback_handler(cq:

"types. CallbackQuery"): user = await ensure_user(cq.from_user.id) data =

cq.data if not

ENABLED MODULES.get(data, False): await

cq.message.answer("Module under development...") await cq.answer() return modules = { "marketplace":"

Marketplace module ready! Use /browse or/sell", "jobs": " Jobs module ready!

Use/list or /apply", "housing": " Housing

module ready!/rent or /sell", "wallet": f" Wallet Balance: (user.wallet_balance)

MMK\n Stars: (user.stars}",

"lucky_draw": "Lucky Draw module ready!/spin/history", "public_service": " Public Service module ready! /bills/tax",

"education": "S Education/AI Tutor

module ready! /lesson/quiz", "health":"

Health/Insurance module ready!/doctor/insurance", "entertainment": "Short

Videos + Engagement Rewards!/watch/

history"} reply_text = modules.get(data,

"Module coming soon...") logger.info("User {user.tg_id) triggered callback: {data}")

WEBHOOK + LIFECYCLE

await cq.message.answer(reply_text)

Build webhook url using Render env or manual WEBHOOK_BASE

RENDER_HOST=

os.getenv("RENDER_EXTERNAL_HOSTNAM

E") if RENDER_HOST: base_url = f"https://(RENDER_HOST}" elif WEBHOOK BASE: base url =

WEBHOOK_BASE.rstrip("/") else: base_url None

WEBHOOK_PATH = f"/webhook/

(WEBHOOK SECRET)" WEBHOOK URL = base url + WEBHOOK PATH if base_url

else None

@app.on_event("startup") async def on_startup(): logger.info("Startup: initializing DB...") await init_db()

# set webhook if we have a public base if

WEBHOOK_URL: logger.info(f"Setting

webhook to (WEBHOOK_URL}") try: await bot.set_webhook(WEBHOOK_URL,

secret_token=WEBHOOK_SECRET,

drop_pending_updates=True)

logger.info("Webhook set successfully") except Exception as e:

logger.exception("Failed to set webhook:

%s", e) else: logger.warning("No

WEBHOOK_URL configured; webhook not set. Use WEBHOOK BASE or deploy to

Render.")

@app.on_event("shutdown") async def on_shutdown(): logger.info("Shutdown:

cleaning up bot session...") try: # aiogram's

Bot.session may be aiohttp. ClientSession; try to close it gracefully sess = getattr(bot,

"session", None) if sess is not None: close

getattr(sess, "close", None) if close: res =

close() # if close is awaitable, await it if hasattr(res, "await"): await res except

Exception: logger.exception("Error while

closing bot session")

webhook endpoint

@app.post(WEBHOOK_PATH) async def telegram_webhook(request: Request): #

verify Telegram secret header header=

request.headers.get("X-Telegram-Bot-Api-Se

cret-Token") if header !=

WEBHOOK SECRET: raise

HTTPException(status_code=403,

detail="forbidden") data = await request.json() try: update

Update.model_validate(data) except

Exception: # fallback: try constructing normally update = Update(**data) # feed update to dispatcher await

dp.feed_update(bot, update) return ("ok": True)

simple health

@app.get("/healthz") async def healthz(): return ("ok": True)

Keep a tiny index route

@app.get("/") async def index(): return {"ok": "bot running"}

ENTRY (for local tests)

Note: Render will run uvicorn main:app -host 0.0.0.0-port $PORT

if name="main": import uvicon

uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

