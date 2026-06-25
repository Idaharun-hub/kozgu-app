"""
Ko'zgu — Foydalanuvchi Boti
Ishga tushirish: python bot.py
"""
import asyncio, logging, os, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

BOT_TOKEN    = os.environ.get("BOT_TOKEN", "8348385427:AAEUYQ_7EKMHagca4cGLXHARguoFa48qtZg")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://idaharun-hub.github.io/kozgu-app/")
RENDER_URL   = os.environ.get("RENDER_URL", "https://kozgu-app.onrender.com")
PORT         = int(os.environ.get("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

WELCOME_UZ = (
    "🪞 *Ko'zgu*\n\n"
    "O'zingni ko'r — hukm qilmay.\n\n"
    "Bu yerda savollar yo'q.\n"
    "Faqat suhbat. Faqat sen."
)
WELCOME_RU = (
    "🪞 *Ko'zgu*\n\n"
    "Увидь себя — без осуждения.\n\n"
    "Здесь нет вопросов.\n"
    "Только разговор. Только ты."
)

def main_keyboard(lang="uz"):
    label = "🪞 Ko'zguni ochish" if lang == "uz" else "🪞 Открыть зеркало"
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=label, web_app=WebAppInfo(url=MINI_APP_URL))
    ]])

@dp.message(CommandStart())
async def start(msg: Message):
    lang = msg.from_user.language_code or "uz"
    lang = "ru" if lang.startswith("ru") else "uz"
    text = WELCOME_UZ if lang == "uz" else WELCOME_RU
    await msg.answer(text, parse_mode="Markdown", reply_markup=main_keyboard(lang))

@dp.message(F.text)
async def any_msg(msg: Message):
    lang = msg.from_user.language_code or "uz"
    lang = "ru" if lang.startswith("ru") else "uz"
    if lang == "uz":
        hint = "Ko'zguni ochish uchun pastdagi tugmani bosing 👇"
    else:
        hint = "Нажмите кнопку ниже, чтобы открыть Ko'zgu 👇"
    await msg.answer(hint, reply_markup=main_keyboard(lang))

# ─── Health check server ───────────────────────────────────────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *args):
        pass

def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logging.info(f"Health server port {PORT} da ishga tushdi")
    server.serve_forever()

# ─── Self-ping (Render uxlamasligi uchun) ─────────────────────────────────────
async def self_ping():
    await asyncio.sleep(60)  # ishga tushgandan 1 daqiqa keyin boshlaydi
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RENDER_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    logging.info(f"Self-ping: {resp.status}")
        except Exception as e:
            logging.warning(f"Self-ping xato: {e}")
        await asyncio.sleep(8 * 60)  # har 8 daqiqada

async def main():
    # Health server
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()
    # Self-ping task
    asyncio.create_task(self_ping())
    logging.info(f"Ko'zgu boti ishga tushdi | Mini App: {MINI_APP_URL}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
