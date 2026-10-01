# 𝕏 (Twitter) Multi-Account Autonomous Crypto & Airdrop Bot Suite 🚀

Suite otomatisasi multi-akun Twitter / X terlengkap dan modern berbasis **Python + Playwright (Headless Chrome)**. Dirancang khusus untuk **Crypto Yapping Ber-Value Tinggi**, **Viral Crypto & Airdrop Engagement**, **Pembersih Following (0 Following Maintenance)**, **Pengecekan Status Kesehatan Akun**, serta **Auto-Hunter Airdrop Giveaway (EVM & Solana)**.

---

## 🌟 Fitur Unggulan Terbaru

### 1. 🤖 Master Autonomous Crypto Bot (`master_crypto_bot.py`)
Orkestrator utama yang menjalankan dua engine secara simultan dan otomatis 24/7 tanpa benturan memori:
- **Engine 1 (Original Post Yapping)**:
  - 1x postingan tweet crypto yapping per akun aktif.
  - Menyematkan Cashtags dinamis (`$SOL`, `$BTC`, `$ETH`, `$SUI`, dll.) dan Hashtags relevan (`#Crypto`, `#Solana`, `#Bitcoin`, `#DeFi`, dll.).
  - **Jeda Antar Siklus**: 1 – 2 Jam (60 – 120 menit acak).
- **Engine 2 (Viral Crypto & Airdrop Engagement)**:
  - 5x postingan viral per batch per akun aktif.
  - **Aksi Nyata**: Auto-Like ❤️ + Auto-Retweet 🔁 + Komentar Kontekstual Berbobot 💬.
  - **Anti-Spam & Keamanan**:
    - 🚫 **Tanpa Follow (0 Following Tetap Terjaga)**: Tidak pernah mem-follow akun siapapun.
    - 🚫 **Bukan Giveaway Drop Address**: Melewati tweet giveaway drop wallet/raffle agar tidak dianggap bot spam.
  - **Jeda Antar Batch**: 30 – 60 Menit acak.
- **Hardware RAM Lock (`asyncio.Lock`)**:
  - Memastikan hanya ada 1 instance browser Chrome yang aktif dalam satu waktu.
  - RAM dan CPU laptop/VPS tetap dingin, ringan, dan stabil.

---

### 2. 🧠 High-Value Combinatorial Generator & Anti-Duplikasi Persisten
Dirancang khusus untuk menghasilkan konten berbobot tinggi (high-value alpha) dengan **Zero Duplication Guarantee**:
- **Arsitektur Modular Multi-Layer**:
  - Postingan yapping dan komentar disusun dari layer: `Hook / Perspective` + `Deep Technical / Macro Insight` + `Actionable Takeaway` + `Sign-off / Engagement Closer`.
  - Meliputi topik: Macro Liquidity (M2 & ETF flows), High-Throughput L1s & Parallel EVM (Solana, Monad, Sui), Sybil-Proof Airdrop Grinding, DeFi Real Yield, dan Psikologi & Manajemen Risiko Trading.
  - Menghasilkan **> 1,500,000 kombinasi unik** yang koheren, profesional, dan berbobot.
- **Persistent Anti-Duplication Engine**:
  - `results/used_yapping_signatures.json`: Mencatat hash SHA256 & teks bersih setiap yapping.
  - `results/used_viral_comments.json`: Mencatat hash SHA256 seluruh komentar viral.
  - Sistem otomatis mengecek riwayat sebelum memposting. Jika terdeteksi kemiripan, bot otomatis melakukan regenerasi instan sampai tweet/komentar 100% segar dan unik.

---

### 3. 🧹 Mass Multi-Account Unfollow Bot (`multi_account_unfollow.py`)
- Menelusuri daftar following seluruh akun dan melakukan unfollow otomatis hingga **0 Following**.
- Membantu menjaga profil akun tetap bersih dan terhindar dari deteksi farm bot.

---

### 4. 🔍 Account Status & Health Checker (`check_all_accounts_status.py`)
- Memindai status API dan sesi seluruh akun di `accounts.json`.
- Mendeteksi akun suspended (Error 64) secara otomatis dan memberi tanda `"suspended": true` agar engine yapping & engagement otomatis melewatinya dengan aman tanpa crash.

---

### 5. 🎁 Classic Giveaway Hunter (`browser_hunter.py` & `web_dashboard.py`)
- Scraping giveaway EVM & Solana dengan eksekusi 4 aksi: Like, Retweet, Follow, dan Drop Address via Web Dashboard (Port 5050).

---

## 🛠️ Panduan Instalasi & Persiapan

### 1. Prasyarat Sistem
- **Python 3.10+** terinstal di sistem.
- **Google Chrome** terinstal.

### 2. Install Dependensi & Browser Playwright
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Konfigurasi Akun di `accounts.json`
Salin template konfigurasi:
```bash
cp accounts.json.example accounts.json
```
Isi cookie `auth_token` dan `ct0` dari browser (melalui *Inspect Element ➔ Application ➔ Cookies ➔ https://x.com*):
```json
{
  "active_account": "fannettt",
  "accounts": {
    "fannettt": {
      "screen_name": "fannettt",
      "name": "Fannet",
      "auth_token": "ISI_AUTH_TOKEN",
      "ct0": "ISI_CT0",
      "evm_address": "0x...",
      "solana_address": "..."
    }
  }
}
```

---

## 🚀 Cara Menjalankan Bot

### 📌 1. Menjalankan Master Bot Crypto (Rekomendasi Utama)
Menjalankan posting mandiri (delay 1-2 jam) dan viral engagement 2x batch (delay 30-60 menit) secara otomatis dan bergantian:
```bash
# Jalankan untuk semua akun aktif:
python master_crypto_bot.py

# Jalankan khusus 1 akun tertentu (contoh: fannettt):
python master_crypto_bot.py -a fannettt
```
*Opsi tambahan:*
- `-a, --account <nama_akun>`: Target hanya 1 akun tertentu.
- `--post-min 60 --post-max 120`: Mengatur rentang jeda posting mandiri (dalam menit).
- `--viral-min 30 --viral-max 60`: Mengatur rentang jeda viral engagement (dalam menit).
- `--viral-count 2`: Jumlah tweet viral per batch per akun (default: 2, aman dari spam limit).
- `--visible`: Menampilkan jendela browser Chrome.

---

### 📌 2. Menjalankan Engine Secara Terpisah (CLI Standalone)

#### A. Giveaway Hunter & Scraper (Drop Address SOL, EVM, BASE):
```bash
# 1. Scrape & temukan giveaway valid terkini (kategori: ALL, EVM, SOLANA):
python giveaway_engine.py -c ALL -m 10

# 2. Scrape sekaligus otomatis ikutan (Like + RT + Follow + Drop Wallet):
python giveaway_engine.py -c ALL -m 10 --auto-enter

# 3. Looping perburuan giveaway terus-menerus:
python browser_hunter.py -a fannettt -c all -m 10 --hours 24 --loop --interval 5 --delay-min 10 --delay-max 30
```
# Opsi parameter:
# -a, --account    : Target akun di accounts.json (contoh: fannettt)
# -c, --category   : Kategori target (all = SOL, EVM, BASE; solana; evm)
# -m, --max        : Jumlah target tweet giveaway per siklus (default: 10)
# --hours          : Batas usia tweet dalam jam (default: 24.0)
# --loop           : Jalankan siklus berkelanjutan otomatis
# --interval       : Jeda istirahat antar siklus dalam menit (default: 5 menit)
# --delay-min/max  : Rentang delay alami antar entri tweet dalam detik (default: 10-30s)
```

#### B. Postingan Yapping Crypto Mandiri:
```bash
# 1x postingan ke seluruh akun aktif:
python crypto_yapper.py

# Khusus 1 akun tertentu:
python crypto_yapper.py -a fannettt

# Looping terjadwal mandiri dengan jeda 60 - 120 menit:
python crypto_yapper.py --loop --interval-min 60 --interval-max 120
```

#### C. Viral Crypto & Airdrop Engagement:
```bash
# 2 tweet viral per akun (Like + RT + Komen kontekstual):
python viral_crypto_engager.py -n 2

# Khusus 1 akun tertentu:
python viral_crypto_engager.py -a fannettt -n 2

# Mode looping mandiri:
python viral_crypto_engager.py --loop -n 2 --interval-min 30 --interval-max 60
```

#### D. Cek Status Kesehatan Semua Akun:
```bash
python check_all_accounts_status.py
```

#### E. Unfollow Massal Semua Akun (Reset ke 0 Following):
```bash
python multi_account_unfollow.py
```

---

## 📁 Struktur Folder Proyek

```text
twitter-scraper-bot/
├── master_crypto_bot.py        # Orkestrator utama Autonomous Dual Engine (Yapping + Viral)
├── crypto_yapper.py            # Engine yapping crypto berbobot tinggi + anti-duplikasi
├── viral_crypto_engager.py     # Engine interaksi tweet viral (Like, RT, Smart Comment)
├── multi_account_unfollow.py   # Bot unfollow massal seluruh akun ke 0 following
├── check_all_accounts_status.py# Scanner kesehatan & pendeteksi suspend akun
├── accounts_manager.py         # Modul manajemen cookie & akun
├── accounts.json               # Kredensial akun (Aman, diabaikan oleh .gitignore)
├── config.py                   # Konfigurasi path & direktori
├── requirements.txt            # Dependensi Python
└── results/                    # Database persistent riwayat & deduplikasi
    ├── crypto_yapping_history.json
    ├── used_yapping_signatures.json
    ├── viral_crypto_engagement_history.json
    └── used_viral_comments.json
```

---

## 🛡️ Keamanan & Anti-Ban Best Practices

1. **Strictly Ignored Credentials**: `accounts.json`, `cookies.json`, `wallets.json`, serta folder `results/` dijamin tidak akan terunggah ke repositori publik melalui konfigurasi `.gitignore`.
2. **Modular Combinatorial Anti-Spam**: Setiap konten dirancang unik secara matematis dan divalidasi silang terhadap log sebelumnya, mencegah flag bot copy-paste oleh algoritma X.
3. **No Wallet Spams**: Bot tidak menjatuhkan alamat wallet di reply tweet publik yang bukan giveaway resmi.
4. **Natural Mouse & Typing Delays**: Seluruh pengetikan menggunakan delay mikro manusiawi dan pembersihan backdrop mask secara mulus.

---

## 📄 Lisensi
Distributed under the MIT License.
