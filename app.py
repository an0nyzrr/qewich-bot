import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest

# ============ НАСТРОЙКИ ============
API_ID = 39194802
API_HASH = "45067e7bea2404a8c6fb7166d52e7c21"

SESSION_STR = "1ApWapzMBu1sAQ94J3CKQvxcb32mSkpg84EDzU3YudunfHdk9AfZ9KfCkkx8xVrKZemTOvs3fH2lMzWLxrEWsbXfz4fzOPFFTqJR1UV7BfzN8yADRiAo4wcnU9wGXX1Yk2Ji3Zxh940XMnHcSZrIzCBH18SH7X9PjRbdFB1BKG-5M2Gk1CvA2L4lUw2WY87lJpeDAP2ywld1U7IswTR_WAISC2TPSw4LbbWKRVd5GzxCyohm6_Zd4pjdgpBMLUCdm-H6SOE4RtEQjUMWWNg6b2AwLSuNAe8vJaya8A-IjLRaTe6ePsPUoO-6yHOmtS18h4ULV6yYB-Lz6SXJ4sEbV8nzKLR4zex4="  

# Если хочешь оставить жирный шрифт только в определенных чатах, 
# оставь CHANNEL, но для "везде" мы убрали привязку к каналу.
# ===================================

client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
LAST_NICK = None

# ---------- Функция получения времени МСК ----------
def get_msk_time():
    now_utc = datetime.utcnow()
    now_msk = now_utc + timedelta(hours=3)
    return now_msk.strftime("%H:%M")

# ---------- 1. Анимация сердечек + время в нике ----------
async def update_nick_animation():
    global LAST_NICK
    frame = 0
    
    # Кадры "анимации" сердечек
    hearts_frames = [
        "♡ ♡ ♡",
        "♥ ♡ ♡",
        "♥ ♥ ♡",
        "♥ ♥ ♥",
        "♥ ♥ ♡",
        "♥ ♡ ♡"
    ]

    while True:
        now_str = get_msk_time()
        
        # Берем текущий кадр
        current_hearts = hearts_frames[frame]
        # Формат ника: [Время] Сердечки
        new_nick = f"[{now_str}] {current_hearts}"

        # Меняем ник только если он отличается от предыдущего
        if new_nick != LAST_NICK:
            try:
                # ВАЖНО: здесь мы меняем last_name (фамилию). 
                # Если хочешь, чтобы менялось имя, используй first_name=new_nick
                await client(UpdateProfileRequest(last_name=new_nick))
                LAST_NICK = new_nick
                print(f"[nick] Ник обновлен: {new_nick}")
            except Exception as e:
                print(f"[nick] Ошибка обновления (возможно FloodWait): {e}")
        
        # Переключаем кадр
        frame = (frame + 1) % len(hearts_frames)
        
        # Ждем 60 секунд. Telegram не даст менять профиль чаще.
        await asyncio.sleep(60)


# ---------- 2. Жирный шрифт ВЕЗДЕ ----------
@client.on(events.NewMessage(outgoing=True))
async def auto_format_everywhere(event):
    """
    Ловит ВСЕ исходящие сообщения от твоего аккаунта.
    """
    text = event.raw_text
    
    # Игнорируем пустые сообщения, медиа без текста и уже отформатированные
    if not text or text.startswith("**—"):
        return
        
    # Игнорируем сервисные сообщения (например, "Вы зашли в группу")
    if event.message.action:
        return

    formatted = f"**— {text}**"
    try:
        # Пытаемся отредактировать сообщение
        await event.edit(formatted, parse_mode="markdown")
        print(f"[format] Отредактировано в чате {event.chat_id}: {text[:20]}...")
    except Exception as e:
        # Если бот не админ в чужом канале или прошло много времени — 
        # Telegram выдаст ошибку, мы её просто проигнорируем, чтобы не спамить в логи.
        pass


async def main():
    await client.start()
    me = await client.get_me()
    print(f"Успешный вход: {me.first_name} (@{me.username})")

    # Запускаем фоновую задачу
    asyncio.create_task(update_nick_animation())

    print("Бот запущен. Жирный шрифт включен ВЕЗДЕ.")
    print("Анимация сердечек в нике включена (обновление раз в минуту).")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
