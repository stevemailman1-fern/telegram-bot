import os
import json
import random
import re
import math
import statistics
import sympy as sp
import requests
from datetime import date
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# GLOBAL & KUOTA
# =========================
user_usage = {}
FREE_LIMIT = 6

def cek_kuota(user_id):
    today = date.today()
    if user_id not in user_usage:
        user_usage[user_id] = {"date": today, "count": 0}
    if user_usage[user_id]["date"] != today:
        user_usage[user_id] = {"date": today, "count": 0}
    if user_usage[user_id]["count"] >= FREE_LIMIT:
        return False
    user_usage[user_id]["count"] += 1
    return True

# =========================
# ARTIKEL PANJANG & RANDOM
# =========================
def generate_article(judul):
    pembuka = [
        f"Topik {judul.lower()} semakin banyak dibahas karena peluang yang ditawarkannya di era digital.",
        f"Belakangan ini, {judul.lower()} menjadi perhatian banyak orang dari berbagai latar belakang.",
        f"Tidak sedikit orang yang tertarik mempelajari {judul.lower()} sebagai solusi jangka panjang."
    ]
    isi_kalimat = [
        "Langkah awal yang penting adalah memahami konsep dasarnya secara menyeluruh.",
        "Banyak pemula langsung memulai tanpa persiapan sehingga hasilnya tidak maksimal.",
        "Perencanaan yang matang akan membantu proses berjalan lebih terarah.",
        "Konsistensi menjadi faktor utama dalam mencapai hasil yang diinginkan.",
        "Kesalahan adalah bagian alami dari proses belajar.",
        "Evaluasi rutin sangat diperlukan untuk meningkatkan kualitas hasil.",
        "Belajar dari pengalaman orang lain dapat mempercepat pemahaman.",
        "Disiplin dalam menjalankan strategi akan sangat mempengaruhi hasil akhir.",
        "Tidak ada hasil instan, tetapi usaha konsisten akan membuahkan hasil.",
        "Kemauan untuk terus belajar adalah modal utama."
    ]
    penutup = [
        f"Kesimpulannya, {judul.lower()} dapat memberikan manfaat besar jika dilakukan dengan serius.",
        f"Pada akhirnya, kunci sukses dari {judul.lower()} terletak pada konsistensi dan disiplin.",
        f"Dengan pendekatan yang tepat, {judul.lower()} bukanlah hal yang mustahil."
    ]
    artikel = f"{judul}\n\nPendahuluan\n{random.choice(pembuka)}\n\nPembahasan\n\n"
    for _ in range(random.randint(15, 25)):
        artikel += random.choice(isi_kalimat) + "\n\n"
    artikel += "Kesimpulan\n" + random.choice(penutup)
    return artikel

# =========================
# REWRITE CERDAS
# =========================
def smart_rewrite(teks):
    sinonim = {
        "penting": ["krusial", "sangat penting", "berperan besar"],
        "adalah": ["merupakan", "dapat dikatakan sebagai"],
        "banyak": ["cukup banyak", "sejumlah besar"],
        "cara": ["metode", "langkah", "pendekatan"],
        "hasil": ["output", "pencapaian", "hasil akhir"]
    }
    kata = teks.split()
    hasil = []
    for k in kata:
        kb = k.lower().strip(",.")
        if kb in sinonim and random.random() > 0.5:
            hasil.append(random.choice(sinonim[kb]))
        else:
            hasil.append(k)
    return " ".join(hasil)

# =========================
# MATEMATIKA TINGKAT KULIAH
# =========================
def hitung_matematika(soal):
    soal = soal.lower().strip()
    if "x" in soal or "y" in soal:
        try:
            x, y = sp.symbols("x y")
            eq = sp.sympify(soal.replace("=", "-(") + ")")
            hasil = sp.solve(eq)
            return f"Hasil = {hasil}"
        except:
            return "Tidak bisa menyelesaikan persamaan."
    if soal.startswith("derivative") or soal.startswith("turunan"):
        try:
            func = soal.split(" ",1)[1]
            x = sp.symbols("x")
            hasil = sp.diff(sp.sympify(func), x)
            return f"Turunan = {hasil}"
        except:
            return "Format turunan salah."
    if soal.startswith("integral") or soal.startswith("integral"):
        try:
            func = soal.split(" ",1)[1]
            x = sp.symbols("x")
            hasil = sp.integrate(sp.sympify(func), x)
            return f"Integral = {hasil} + C"
        except:
            return "Format integral salah."
    if soal.startswith("mean") or soal.startswith("rata"):
        try:
            angka = list(map(float, re.findall(r"-?\d+\.?\d*", soal)))
            return f"Rata-rata = {statistics.mean(angka)}"
        except:
            return "Format statistik salah."
    if soal.startswith("median"):
        try:
            angka = list(map(float, re.findall(r"-?\d+\.?\d*", soal)))
            return f"Median = {statistics.median(angka)}"
        except:
            return "Format statistik salah."
    try:
        soal = soal.replace("^", "**")
        if not all(c in "0123456789+-*/(). x^" for c in soal):
            return "Soal tidak valid."
        hasil = eval(soal, {"__builtins__": {}}, {"math": math})
        return f"Hasil = {hasil}"
    except:
        return "Tidak bisa menghitung soal tersebut."

# =========================
# QUIZ / PENGETAHUAN UMUM + LIVE SEARCH
# =========================
quiz_db = {
    "ibu kota indonesia": "Jakarta",
    "presiden indonesia saat ini": "Joko Widodo",
    "bendera jepang": "Merah Putih dengan lingkaran merah",
    "planet terdekat dari matahari": "Merkurius"
}

def live_search(query):
    API_KEY = os.getenv("SERPAPI_KEY")
    if not API_KEY:
        return "Live search API key tidak ditemukan."
    params = {"engine":"google","q":query,"api_key":API_KEY}
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        if "answer_box" in data and "answer" in data["answer_box"]:
            return data["answer_box"]["answer"]
        elif "organic_results" in data and len(data["organic_results"])>0:
            return data["organic_results"][0]["snippet"]
        else:
            return "Jawaban tidak ditemukan."
    except Exception as e:
        return f"Terjadi kesalahan: {e}"

def jawab_quiz(pertanyaan):
    kunci = pertanyaan.lower()
    if kunci in quiz_db:
        return quiz_db[kunci]
    else:
        return live_search(pertanyaan)

# =========================
# COMMANDS BOT
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo 👋 teman belajar siap membantu\n\n"
        "Artikel & Rewrite\n"
        "/artikel Judul artikel\n"
        "/rewrite Teks yang ingin diubah\n\n"
        "Matematika\n"
        "/math soal\n"
        "/mathhelp\n\n"
        "Quiz / Pengetahuan Umum\n"
        "/quiz Pertanyaan"
    )

async def artikel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not cek_kuota(user_id):
        await update.message.reply_text("Kuota gratis habis (6x). Upgrade premium untuk unlimited.")
        return
    judul = " ".join(context.args)
    if not judul:
        await update.message.reply_text("Masukkan judul artikel.")
        return
    await update.message.reply_text(generate_article(judul))

async def rewrite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not cek_kuota(user_id):
        await update.message.reply_text("Kuota gratis habis (6x). Upgrade premium untuk unlimited.")
        return
    teks = " ".join(context.args)
    if not teks:
        await update.message.reply_text("Masukkan teks.")
        return
    await update.message.reply_text("Hasil Rewrite:\n\n" + smart_rewrite(teks))

async def math(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not cek_kuota(user_id):
        await update.message.reply_text("Kuota gratis habis (6x). Upgrade premium untuk unlimited.")
        return
    soal = " ".join(context.args)
    if not soal:
        await update.message.reply_text("Masukkan soal matematika.")
        return
    await update.message.reply_text(hitung_matematika(soal))

async def mathhelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Panduan Matematika\n"
        "Penjumlahan: +\nPengurangan: -\nPerkalian: *\nPembagian: /\nPangkat: ^\n"
        "Gunakan ( ) untuk prioritas hitung\n"
        "Persamaan: 2x + 4 = 10\n"
        "Turunan: derivative x^2 + 3*x\n"
        "Integral: integral x^2 + 3*x\n"
        "Statistik: mean 2,4,6 / median 3,5,7"
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not cek_kuota(user_id):
        await update.message.reply_text("Kuota gratis habis (6x). Upgrade premium untuk unlimited.")
        return
    pertanyaan = " ".join(context.args)
    if not pertanyaan:
        await update.message.reply_text("Masukkan pertanyaan quiz.")
        return
    jawaban = jawab_quiz(pertanyaan)
    await update.message.reply_text(jawaban)

# =========================
# RUN BOT
# =========================
TOKEN = os.getenv("BOT_TOKEN")
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("artikel", artikel))
app.add_handler(CommandHandler("rewrite", rewrite))
app.add_handler(CommandHandler("math", math))
app.add_handler(CommandHandler("mathhelp", mathhelp))
app.add_handler(CommandHandler("quiz", quiz))

print("Bot berjalan...")
try:
    app.run_polling()
except Exception as e:
    print("Bot error:", e)
