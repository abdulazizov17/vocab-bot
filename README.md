# Vocab Bot — O'rnatish va Ishga Tushirish

## 1. Tokenni almashtiring (MUHIM!)
Eski tokeningiz ommaviy joyda ko'rsatildi — uni bekor qiling:
1. Telegramda @BotFather ga yozing
2. /mybots → botingizni tanlang
3. API Token → Revoke token
4. Yangi tokenni nusxalang

## 2. O'rnatish

```bash
# Papka yarating
mkdir vocab_bot && cd vocab_bot

# Fayllarni shu papkaga ko'chiring

# Virtual muhit yarating (tavsiya)
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# yoki
venv\Scripts\activate      # Windows

# Kutubxonalarni o'rnating
pip install -r requirements.txt
```

## 3. Token sozlash

```bash
# .env fayl yarating
cp .env.example .env

# .env faylni oching va tokeningizni kiriting
# BOT_TOKEN=1234567890:ABCdef...
```

## 4. Botni ishga tushirish

```bash
# .env fayldan token o'qish uchun
export $(cat .env | xargs)   # Linux/Mac

# Windows PowerShell
$env:BOT_TOKEN="sizning_tokeningiz"

# Botni ishga tushirish
python bot.py
```

## 5. Serverda doim ishlashi uchun (Linux)

```bash
# systemd service yozing:
sudo nano /etc/systemd/system/vocabbot.service

# Quyidagini yozing:
[Unit]
Description=Vocab Telegram Bot
After=network.target

[Service]
WorkingDirectory=/home/user/vocab_bot
EnvironmentFile=/home/user/vocab_bot/.env
ExecStart=/home/user/vocab_bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target

# Saqlang va ishga tushiring:
sudo systemctl enable vocabbot
sudo systemctl start vocabbot
```

## Bot buyruqlari
- /start — Botni boshlash
- /menu — Asosiy menyu

## Funksiyalar
- Kunlik so'zlar (daraja bo'yicha)
- So'z kartasi (talaffuz + tarjima + misol)
- Yodladim tugmasi + progress
- Gap tuzish mashqi (avtomatik tekshirish)
- Lug'at (o'rganilganlar ko'rinadi)
- Statistika (streak, progress)
- Sozlamalar (daraja + kunlik maqsad)
