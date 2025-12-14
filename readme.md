# Telegram Bot 24 Jam

Bot Telegram ini bisa:
- Membuat artikel panjang & random
- Rewrite teks
- Matematika tingkat kuliah (persamaan, turunan, integral, statistik)
- Quiz / Pengetahuan umum
- Live search jawaban (SerpAPI)

## Cara Deploy ke Railway

1. Fork repository ini ke akun GitHub kamu
2. Masukkan token Telegram di Environment Variable `BOT_TOKEN`
3. Masukkan SerpAPI key (opsional) di Environment Variable `SERPAPI_KEY`
4. Deploy ke Railway
5. Klik **Start Project**
6. Bot akan berjalan 24 jam online

## Library yang dibutuhkan

Semua library sudah tercantum di `requirements.txt`:
- python-telegram-bot==22.5
- requests==2.32.5
- sympy==1.12
- statistics==1.0
