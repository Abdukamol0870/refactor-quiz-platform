import os, re, unicodedata
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-change-before-deploy")
url = os.getenv("DATABASE_URL", "sqlite:///quiz.db")
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
db = SQLAlchemy(app)

QUESTIONS = [
("Refaktoring nima?", ["Dasturning tashqi xatti-harakatini saqlab ichki tuzilishini yaxshilash","Yangi funksiyalar qo‘shish","Tilni almashtirish","Faqat ranglarni o‘zgartirish"],0,"Refaktoring ichki tuzilishni yaxshilaydi, tashqi xatti-harakatni saqlaydi."),
("Takroriy kodni kamaytirish uchun qaysi yo‘l mos?", ["Koddan nusxa olish","Umumiy mantiqni funksiya yoki modulga ajratish","Bitta ulkan funksiya yozish","Nomlarni olib tashlash"],1,"Umumiy mantiqni qayta ishlatish DRY tamoyiliga mos."),
("DRY tamoyili nimani anglatadi?", ["Dasturni ikki baravar tez qilish","Har bir funksiyani boshqa faylga yozish","Bir xil mantiqni keraksiz takrorlamaslik","Faqat qisqa nom ishlatish"],2,"DRY — Don't Repeat Yourself."),
("Uzun va ko‘p vazifali funksiyani qanday yaxshilash mumkin?", ["Faqat nomini o‘zgartirish","Izohlarni o‘chirish","Yana vazifa qo‘shish","Kichik, ma’noli funksiyalarga ajratish"],3,"Extract Function katta funksiyani kichik vazifalarga ajratadi."),
("Yaxshi o‘zgaruvchi nomi qanday bo‘ladi?", ["Tushunarli va vazifani ifodalovchi","Doim bir belgili","Imkon qadar uzun","Faqat raqamli"],0,"Nom qiymat yoki vazifaning ma’nosini ko‘rsatishi kerak."),
("Unit testlar refaktoringda nima uchun kerak?", ["Kod rangini tanlash","Mavjud xatti-harakat saqlanganini tekshirish","Izoh yozish","Bazani tozalash"],1,"Testlar o‘zgarishlardan keyin funksionallik buzilmaganini tekshiradi."),
("Code smell nima?", ["Dastur albatta ishlamasligi","Doim sintaksis xatosi","Muammo keltirishi mumkin bo‘lgan kod tuzilmasi belgisi","Yomon rangli interfeys"],2,"Code smell muammo ehtimolini ko‘rsatadi, lekin o‘zi doim xato emas."),
("Magic number muammosiga misol qaysi?", ["Konstantaga izoh yozish","Aniq nomli funksiya","Qiymatni sozlamadan olish","Ma’nosi izohlanmagan 0.18 sonini kodda ishlatish"],3,"Ma’nosiz literal qiymatni nomlangan konstanta bilan ifodalash tushunarlilikni oshiradi."),
("Single Responsibility Principle nimani tavsiya qiladi?", ["Modulning bitta asosiy mas’uliyati bo‘lishi","Barcha funksiyalar global bo‘lishi","Har sinfda o‘nta metod bo‘lishi","Bitta fayldan foydalanish"],0,"SRP modulning bitta asosiy o‘zgarish sababiga ega bo‘lishini ko‘zlaydi."),
("Formatter asosan nima qiladi?", ["Barcha mantiqiy xatoni tuzatadi","Kod yozilish uslubini bir xil qiladi","Talablarni belgilaydi","Testlarni muvaffaqiyatli qiladi"],1,"Formatter ko‘rinish va uslubni standartlashtiradi."),
("Extract Function usulining maqsadi nima?", ["Barcha metodlarni o‘chirish","Kodni izohga aylantirish","Kod bo‘lagini alohida nomlangan funksiyaga ajratish","Parametrlarni doim ko‘paytirish"],2,"Bu usul kod bo‘lagini qayta ishlatiladigan va tushunarli funksiya qiladi."),
("Qaysi yondashuv kodni saqlashni osonlashtiradi?", ["Hammasini bitta qatorda yozish","Barcha nomlarni a, b, c qilish","Har qanday abstraksiyadan qochish","Tushunarli nomlar va izchil tuzilma"],3,"Aniq nomlar va izchil tuzilma o‘qishni yengillashtiradi."),
("Dead code aniqlansa nima qilish kerak?", ["Tekshirib, xavfsiz bo‘lsa olib tashlash","Ko‘paytirish","Har modulga ko‘chirish","Global qilish"],0,"Ishlatilmaydigan kodni xavfsiz olib tashlash murakkablikni kamaytiradi."),
("Regression test nimani tekshiradi?", ["Ranglarni","Yangi o‘zgarishlar oldingi funksiyalarni buzmaganini","Nomlar uzunligini","Fayllar sonini"],1,"Regression test avval ishlagan funksiyalar saqlanganini tekshiradi."),
("Kichik bosqichlarda refaktoring qilishning foydasi nima?", ["Hujjatlarni yo‘qotish","Testlarni bekor qilish","Xatoni topish va ta’sirni nazorat qilishni osonlashtirish","Kod hajmini oshirish"],2,"Kichik o‘zgarishlarni tekshirish muammoni aniqlashni osonlashtiradi."),
("Keraksiz murakkablikka qaysi misol mos?", ["Aniq funksiya nomi","Takroriy kodni birlashtirish","Sodda yechim ishlatish","Oddiy vazifa uchun ortiqcha ko‘p qatlamli arxitektura"],3,"Keraksiz abstraksiyalar kodni tushunishni qiyinlashtiradi."),
("Static analysis nima yordam beradi?", ["Kodni ishga tushirmasdan ayrim muammolarni topish","Boshqa odam o‘rniga test ishlash","Talablarni o‘zgartirish","Bazani loyihalash"],0,"Statik tahlil kodni bajarmasdan ayrim xato va uslub muammolarini topadi."),
("Refaktoring va yangi imkoniyat qo‘shish farqi nima?", ["Refaktoring faqat CSS","Refaktoring ichki tuzilmani yaxshilaydi, yangi imkoniyat funksiyani kengaytiradi","Yangi imkoniyatda test shart emas","Ular bir xil"],1,"Refaktoring tashqi xatti-harakatni saqlaydi; yangi imkoniyat uni kengaytiradi."),
("Katta sinfda aloqasi kam vazifalar jamlangan bo‘lsa, nima qilish mumkin?", ["Barchasini bitta metodga birlashtirish","Sinf nomini qisqartirish","Extract Class bilan mas’uliyatlarni ajratish","Barcha metodlarni o‘chirish"],2,"Extract Class alohida mas’uliyatlarni boshqa sinflarga ajratadi."),
("Sifatli refaktoring ketma-ketligi qaysi?", ["Hammasini birdan o‘zgartirish","Testlarni o‘chirish","Faqat nomlarni o‘zgartirish","Avval testlash, kichik o‘zgarish qilish va qayta testlash"],3,"Kichik o‘zgarish va qayta testlash xatarni kamaytiradi."),
]

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    normalized_name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False, default=20)
    duration_seconds = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

def norm_name(name):
    name = unicodedata.normalize("NFKC", name or "")
    return re.sub(r"\s+", " ", name).strip().casefold()

def public_questions():
    return [{"id": i, "question": q, "options": opts} for i, (q, opts, ans, why) in enumerate(QUESTIONS, 1)]

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/questions")
def api_questions():
    return jsonify({"questions": public_questions()})

@app.post("/api/start")
def start():
    data = request.get_json(silent=True) or {}
    name = re.sub(r"\s+", " ", str(data.get("full_name", ""))).strip()
    if len(name) < 3 or len(name) > 120:
        return jsonify(success=False, error="Ism-familiyangizni to‘liq kiriting."), 400
    if Result.query.filter_by(normalized_name=norm_name(name)).first():
        return jsonify(success=False, error="Bu ism-familiya bilan test allaqachon topshirilgan."), 409
    return jsonify(success=True, full_name=name, questions=public_questions())

@app.post("/api/submit")
def submit():
    data = request.get_json(silent=True) or {}
    name = re.sub(r"\s+", " ", str(data.get("full_name", ""))).strip()
    answers = data.get("answers")
    if len(name) < 3 or len(name) > 120:
        return jsonify(success=False, error="Ism-familiya noto‘g‘ri."), 400
    if not isinstance(answers, dict) or set(answers) != {str(i) for i in range(1, 21)}:
        return jsonify(success=False, error="Barcha 20 savolga javob bering."), 400
    normalized = norm_name(name)
    if Result.query.filter_by(normalized_name=normalized).first():
        return jsonify(success=False, error="Bu ism-familiya bilan test allaqachon topshirilgan."), 409
    score = 0
    for i, (_, opts, correct, _) in enumerate(QUESTIONS, 1):
        choice = answers.get(str(i))
        if isinstance(choice, bool) or not isinstance(choice, int) or choice not in range(len(opts)):
            return jsonify(success=False, error="Javob formati noto‘g‘ri."), 400
        score += int(choice == correct)
    try:
        duration = max(0, min(int(data.get("duration_seconds", 0)), 86400))
    except (TypeError, ValueError):
        duration = 0
    result = Result(full_name=name, normalized_name=normalized, score=score, total=len(QUESTIONS), duration_seconds=duration)
    db.session.add(result)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(success=False, error="Bu ism-familiya bilan test allaqachon topshirilgan."), 409
    return jsonify(success=True, result={"full_name": name, "score": score, "total": 20, "percentage": round(score * 5), "duration_seconds": duration})

@app.get("/results")
def results():
    rows = Result.query.order_by(Result.score.desc(), Result.duration_seconds.asc(), Result.created_at.asc()).all()
    return render_template("results.html", results=rows, total=len(rows))

@app.get("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify(status="ok", database="connected")
    except Exception:
        app.logger.exception("Database health check failed")
        return jsonify(status="error"), 503

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
