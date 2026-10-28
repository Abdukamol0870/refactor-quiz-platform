# RefactorQuiz

20 ta savolli, mobilga mos onlayn test. Flask + PostgreSQL, mahalliy rejimda SQLite.

## Windows'da ishga tushirish
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```
Brauzer: http://127.0.0.1:5000

## Render'da internetga joylash
1. Loyiha fayllarini GitHub repository'ga yuboring (`.env` ni hech qachon yubormang).
2. Render'da repository'dan Web Service yarating.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. PostgreSQL database yarating va uning internal connection string qiymatini Web Service `DATABASE_URL` environment variable'iga qo'ying.
6. `SECRET_KEY` uchun uzun tasodifiy qiymat o'rnating. `render.yaml` blueprint sifatida ham ishlatilishi mumkin.
7. Deploy tugagach, Render bergan HTTPS havolani talabalarga yuboring.

Sahifalar: `/` test, `/results` umumiy reyting, `/health` tekshiruv.

## Eslatma
Takroriy urinish ism-familiyaning normallashtirilgan shakli bo'yicha cheklanadi. Bu boshqa ism yozilishi yoki boshqa odamning ismini kiritilishini to'liq to'xtatmaydi. Kuchliroq tekshiruv uchun o'qituvchi kodi yoki talaba ID qo'shish kerak. Natijalar sahifasi ommaviy.
