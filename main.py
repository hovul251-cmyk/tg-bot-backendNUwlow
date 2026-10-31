import hashlib
import hmac
from urllib.parse import parse_qsl
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

# Разрешаем запросы с GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Для продакшена лучше указать ваш https://<логин>.github.io
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")

# 1. Безопасная валидация Telegram initData
def verify_telegram_init_data(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="Отсутствует авторизация")

    raw_init_data = authorization[4:]
    parsed_data = dict(parse_qsl(raw_init_data))
    
    received_hash = parsed_data.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Неверная подпись")

    # Сортируем параметры по алфавиту
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
    
    # Вычисляем секретный ключ через HMAC-SHA256
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != received_hash:
        raise HTTPException(status_code=403, detail="Подпись Telegram не совпадает")

    return parsed_data

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "USDT"

@app.post("/api/pay/create")
async def create_payment(req: PaymentRequest, auth_data: dict = Depends(verify_telegram_init_data)):
    # Здесь вызывается логика из cryptobot.py
    # Пример вызова CryptoPay API для создания инвойса:
    # pay_url = await cryptobot_client.create_invoice(amount=req.amount, asset=req.currency)
    
    mock_pay_url = f"https://t.me/CryptoBot?start=test_invoice"
    return {"status": "ok", "pay_url": mock_pay_url}

@app.post("/api/tasks/start-invite")
async def start_invite(auth_data: dict = Depends(verify_telegram_init_data)):
    # Здесь вызывается логика из telethon_manager.py
    # asyncio.create_task(run_telethon_invite(...))
    return {"status": "started", "message": "Процесс инвайтинга запущен в фоновом режиме"}
