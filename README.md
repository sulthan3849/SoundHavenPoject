# SoundHaven Music Platform 🎵

SoundHaven adalah platform streaming dan pengunduh audio berkualitas tinggi (Hi-Res Lossless) yang dibangun menggunakan arsitektur modern berbasis FastAPI dan Web Player responsif.

## ✨ Fitur Utama

- 🎧 **Hi-Res Audio Streaming**: Streaming musik berkualitas studio (FLAC / HiFi).
- ⚡ **Fast & Lightweight Backend**: Dibangun di atas FastAPI dengan performa asinkron tinggi.
- 📥 **Batch & Single Track Downloader**: Pengunduhan trek dan metadata lengkap secara otomatis.
- 🔍 **Universal Search & Explorer**: Pencarian trek, artis, album, dan playlist dengan antarmuka yang bersih.
- 📱 **Modern Web Interface**: Antarmuka pemutar musik interaktif yang responsif untuk berbagai ukuran layar.

## 📁 Struktur Direktori

```text
soundhaven-music-platform/
├── backend/               # Server API berbasis FastAPI
│   ├── app/               # Modul logika bisnis, routing & parser
│   ├── tests/             # Skrip pengujian otomatis & integrasi API
│   ├── requirements.txt   # Dependensi Python
│   └── main.py            # Entry point backend server
├── frontend/              # Antarmuka web player
├── scripts/               # Utilitas deployment & installer
├── .gitignore             # Aturan ignorir file sementara & rahasia
└── README.md              # Dokumentasi proyek
```

## 🚀 Memulai (Getting Started)

### 1. Prasyarat
- Python 3.10+
- Node.js 18+ (untuk frontend)

### 2. Menjalankan Backend
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Menjalankan Frontend
```bash
cd frontend
# Buka index.html di browser atau jalankan melalui live server
```

## 📄 Lisensi
Distributed under the MIT License.
