import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest

# ============ НАСТРОЙКИ ============
API_ID = 39194802
API_HASH = "45067e7bea2404a8c6fb7166d52e7c21"

# ВСТАВЬ СЮДА СТРОКУ, КОТОРУЮ ВЫДАЛ gen_session.py (внутри кавычек)
SESSION_STR = "1ApWapzMBu1sAQ94J3CKQvxcb32mSkpg84EDzU3YudunfHdk9AfZ9KfCkkx8xVrKZemTOvs3fH2lMzWLxrEWsbXfz4fzOPFFTqJR1UV7BfzN8yADRiAo4wcnU9wGXX1Yk2Ji3Zxh940XMnHcSZrIzCBH18SH7X9PjRbdFB1BKG-5M2Gk1CvA2L4lUw2WY87lJpeDAP2ywld1U7IswTR_WAISC2TPSw4LbbWKRVd5GzxCyohm6_Zd4pjdgpBMLUCdm-H6SOE4RtEQjUMWWNg6b2AwLSuNAe8vJaya8A-IjLRaTe6ePsPUoO-6yHOmtS18h4ULV6yYB-Lz6SXJ4sEbV8nzKLR4zex4="  

# Укажи свой канал (юзернейм с @ или ID вида -100123456789)
CHANNEL = "@qnewich"  
# ===================================

client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
LAST_NICK = None # Переменная для хранения последнего установленного ника

# ---------- Функция получения времени МСК ----------
def get_msk_time():
    # Указываем часовой пояс UTC+3 (Europe/Moscow)
    now_msk = datetime.now(ZoneInfo("Europe/Moscow"))
    return now_msk.strftime("[%H:%M]")

# ---------- 1. Ник с временем ----------
async def update_nick_time():
    global LAST_NICK
    while True:
        now_str = get_msk_time()
        
        # Меняем ник только если время изменилось, чтобы не спамить API Telegram
        if now_str != LAST_NICK:
            try:
                await client(UpdateProfileRequest(last_name=now_str))
                LAST_NICK = now_str
                print(f"[nick] Фамилия обновлена на МСК время: {now_str}")
            except Exception as e:
                print(f"[nick] Ошибка обновления: {e}")
        
        # Ждем 15 секунд и проверяем снова
        await asyncio.sleep(15)


# ---------- 2. Автоформат своих сообщений в канале ----------
@client.on(events.NewMessage(chats=CHANNEL, outgoing=True))
async def auto_format(event):
    """
    Если ты написал в своём канале обычное сообщение — бот перезапишет его
    в жирный формат: **— текст**
    """
    text = event.raw_text
    if not text or text.startswith("**—"):
        return

    formatted = f"**— {text}**"
    try:
        await event.edit(formatted, parse_mode="markdown")
        print(f"[format] переформатировано: {text[:30]}...")
    except Exception as e:
        print(f"[format] ошибка: {e}")


async def main():
    await client.start()
    me = await client.get_me()
    print(f"Успешный вход: {me.first_name} (@{me.username})")

    # Запускаем фоновую задачу обновления ника
    asyncio.create_task(update_nick_time())

    print(f"Слушаю канал: {CHANNEL}")
    print("Бот запущен. Время используется по МСК (UTC+3).")
    
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
