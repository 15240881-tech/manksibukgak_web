import json
import time
from io import BytesIO
from flask import Flask, jsonify, render_template_string, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)

# --- MOCK DATABASE ---
JAM_OPERASIONAL = [
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
]

antrean_live = {
    "total_antrean": 4,
    "sedang_dilayani": "B 1234 ABC (Vario 160)",
    "nomor_terakhir": 44,
}

jam_terisi_db = {
    "2026-09-30": ["08:00", "09:00", "10:00"],
}

data_booking_pelanggan = []

# Credential Admin
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# --- HTML TEMPLATE ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MANKSIBUKGAK - Servis Motor Modern & Terpercaya</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding-bottom: 50px; }
        
        /* Navbar */
        nav { background-color: #1e293b; border-bottom: 1px solid #334155; padding: 12px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); position: sticky; top: 0; z-index: 50; }
        .logo-container { display: flex; align-items: center; gap: 10px; cursor: pointer; }
        .logo-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
        .logo-text { font-size: 18px; font-weight: 800; color: #fff; letter-spacing: 0.5px; }
        .nav-btns { display: flex; gap: 10px; }
        .btn-tab { padding: 8px 16px; border-radius: 8px; border: none; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .btn-active { background-color: #f59e0b; color: #0f172a; }
        .btn-inactive { background-color: #334155; color: #cbd5e1; }
        .btn-inactive:hover { background-color: #475569; color: #fff; }

        /* Container */
        .container { max-width: 950px; margin: 30px auto; padding: 0 20px; }

        /* HERO SECTION BERANDA */
        .hero { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; border-radius: 20px; padding: 40px 30px; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); position: relative; overflow: hidden; }
        .hero-logo { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; margin-bottom: 15px; border: 2px solid #f59e0b; box-shadow: 0 0 15px rgba(245, 158, 11, 0.3); }
        .hero-badge { display: inline-block; background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: 700; margin-bottom: 15px; }
        .hero h1 { font-size: 32px; font-weight: 800; color: #fff; margin-bottom: 12px; line-height: 1.2; }
        .hero h1 span { color: #f59e0b; }
        .hero p { color: #94a3b8; font-size: 15px; max-width: 600px; margin: 0 auto 25px auto; line-height: 1.6; }
        .btn-hero { background-color: #f59e0b; color: #0f172a; border: none; padding: 14px 28px; border-radius: 10px; font-size: 16px; font-weight: 800; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4); }
        .btn-hero:hover { background-color: #d97706; transform: translateY(-2px); }

        /* SECTION TITLE */
        .section-header { text-align: center; margin-bottom: 25px; margin-top: 40px; }
        .section-title { font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 5px; }
        .section-subtitle { font-size: 13px; color: #94a3b8; }

        /* GRID KATALOG LAYANAN */
        .service-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 18px; }
        .service-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; transition: 0.2s; text-align: left; }
        .service-card:hover { border-color: #f59e0b; transform: translateY(-3px); }
        .service-title { font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 6px; }
        .service-desc { font-size: 12px; color: #94a3b8; margin-bottom: 12px; line-height: 1.4; }
        .service-price { font-size: 14px; font-weight: 800; color: #38bdf8; }

        /* GRID KEUNGGULAN */
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 15px; }
        .feature-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; display: flex; gap: 15px; align-items: flex-start; }
        .feature-num { font-size: 20px; font-weight: 800; color: #f59e0b; background: rgba(245, 158, 11, 0.1); width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .feature-text h4 { font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 4px; }
        .feature-text p { font-size: 12px; color: #94a3b8; line-height: 1.4; }

        /* CONTACT US SECTION */
        .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-top: 15px; }
        .contact-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 22px; text-align: center; transition: 0.2s; }
        .contact-card:hover { border-color: #f59e0b; }
        .contact-icon { font-size: 32px; margin-bottom: 10px; }
        .contact-title { font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 6px; }
        .contact-detail { font-size: 13px; color: #94a3b8; margin-bottom: 15px; line-height: 1.5; }
        .btn-contact { display: inline-block; text-decoration: none; padding: 8px 16px; border-radius: 8px; font-size: 12px; font-weight: 700; transition: 0.2s; }
        .btn-contact-wa { background-color: #22c55e; color: #fff; }
        .btn-contact-wa:hover { background-color: #16a34a; }
        .btn-contact-map { background-color: #38bdf8; color: #0f172a; }
        .btn-contact-map:hover { background-color: #0284c7; color: #fff; }

        /* Live Status Bar */
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .status-card { background-color: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; }
        .status-title { font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 700; margin-bottom: 5px; }
        .status-value { font-size: 24px; font-weight: 800; color: #f59e0b; }
        .status-value.blue { color: #38bdf8; }
        .status-value.text { font-size: 15px; font-weight: 600; color: #fff; }

        /* Card Form & Table */
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 25px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); margin-bottom: 20px; }
        .card-header { margin-bottom: 20px; }
        .card-title { font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 5px; }
        .card-subtitle { font-size: 13px; color: #94a3b8; }
        
        /* Form Styling */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 15px; margin-bottom: 15px; }
        .form-group { display: flex; flex-direction: column; }
        label { font-size: 12px; font-weight: 600; color: #cbd5e1; margin-bottom: 6px; }
        input, select { background-color: #0f172a; border: 1px solid #334155; color: #fff; padding: 10px 14px; border-radius: 8px; font-size: 14px; outline: none; width: 100%; transition: 0.2s; }
        input:focus, select:focus { border-color: #f59e0b; }

        /* Time Slot Grid */
        .time-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 8px; }
        .btn-time { background-color: #0f172a; border: 1px solid #334155; color: #cbd5e1; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; text-align: center; transition: 0.2s; }
        .btn-time:hover:not(.disabled) { border-color: #f59e0b; color: #fff; }
        .btn-time.selected { background-color: #f59e0b; color: #0f172a; border-color: #f59e0b; font-weight: 700; }
        .btn-time.disabled { background-color: #1e293b; border-color: #475569; color: #475569; cursor: not-allowed; text-decoration: line-through; opacity: 0.6; }

        /* Buttons */
        .btn-submit { width: 100%; background-color: #f59e0b; color: #0f172a; font-weight: 700; padding: 14px; border: none; border-radius: 10px; font-size: 15px; cursor: pointer; margin-top: 20px; transition: 0.2s; box-shadow: 0 4px 14px rgba(245, 158, 11, 0.3); }
        .btn-submit:hover { background-color: #d97706; }
        .btn-disabled { opacity: 0.5; cursor: not-allowed; background-color: #64748b !important; box-shadow: none !important; }

        /* Admin Controls */
        .admin-control-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .btn-admin-action { background-color: #38bdf8; color: #0f172a; border: none; padding: 10px 15px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; }
        .btn-admin-action:hover { background-color: #0284c7; color: #fff; }

        /* Table Admin */
        table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
        th { background-color: #0f172a; color: #94a3b8; padding: 12px; text-transform: uppercase; font-size: 11px; border-bottom: 1px solid #334155; }
        td { padding: 12px; border-bottom: 1px solid #334155; color: #cbd5e1; }

        .btn-invoice { background-color: #38bdf8; color: #0f172a; border: none; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-bottom: 4px; display: inline-block; }
        .btn-invoice:hover { background-color: #0284c7; color: #fff; }
        .btn-delete { background-color: #ef4444; color: #fff; border: none; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; transition: 0.2s; display: inline-block; }
        .btn-delete:hover { background-color: #dc2626; }

        /* MODAL COMMON */
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: flex; justify-content: center; align-items: center; padding: 20px; z-index: 99; }
        
        .modal-login {
            background: #1e293b; border: 1px solid #334155; color: #fff; border-radius: 16px; max-width: 360px; width: 100%; padding: 25px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); text-align: center;
        }

        .modal-receipt {
            background: #ffffff; color: #1e293b; border-radius: 16px; max-width: 500px; width: 100%; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); font-family: 'Segoe UI', sans-serif;
        }

        .receipt-header { text-align: center; margin-bottom: 12px; }
        .receipt-header h2 { font-size: 20px; font-weight: 800; color: #0f172a; margin-top: 5px; }
        .receipt-header p { font-size: 11px; color: #64748b; }
        
        .receipt-actions { display: flex; flex-direction: column; gap: 8px; margin-top: 15px; }
        .btn-wa { background: #22c55e; color: #fff; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; text-align: center; }
        .btn-wa:hover { background: #16a34a; }
        .btn-thermal { background: #f59e0b; color: #0f172a; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; text-align: center; }
        .btn-thermal:hover { background: #d97706; }
        .btn-pdf { background: #e11d48; color: #fff; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; text-align: center; }
        .btn-pdf:hover { background: #be123c; }
        .btn-close-link { background: transparent; border: none; color: #64748b; font-size: 12px; cursor: pointer; margin-top: 4px; text-align: center; }

        .hidden { display: none !important; }
    </style>
</head>
<body>

    <!-- Navbar -->
    <nav>
        <div class="logo-container" onclick="toggleTab('home')">
            <svg class="logo-img" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                <circle cx="100" cy="100" r="98" fill="#0b0b0b"/>
                <path d="M 50,100 C 50,65 65,50 100,50 C 135,50 150,65 150,100 C 150,135 135,150 100,150 C 65,150 50,135 50,100 Z" fill="#e62225"/>
                <path d="M 68,100 C 68,76 76,68 100,68 C 124,68 132,76 132,100 C 132,124 124,132 100,132 C 76,132 68,124 68,100 Z" fill="#fbb03b"/>
                <rect x="78" y="78" width="44" height="44" fill="#ffffff" rx="8"/>
                <rect x="85" y="85" width="30" height="30" fill="#0b0b0b" rx="4"/>
            </svg>
            <span class="logo-text">MANKSIBUKGAK</span>
        </div>
        <div class="nav-btns">
            <button onclick="toggleTab('home')" id="btnTabHome" class="btn-tab btn-active">Beranda</button>
            <button onclick="toggleTab('booking')" id="btnTabBooking" class="btn-tab btn-inactive">Form Booking</button>
            <button onclick="toggleTab('admin')" id="btnTabAdmin" class="btn-tab btn-inactive">Panel Admin</button>
        </div>
    </nav>

    <!-- TAB 1: BERANDA -->
    <div id="tabHome" class="container">
        <!-- Hero Banner -->
        <div class="hero">
            <svg class="hero-logo" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                <circle cx="100" cy="100" r="98" fill="#0b0b0b"/>
                <path d="M 50,100 C 50,65 65,50 100,50 C 135,50 150,65 150,100 C 150,135 135,150 100,150 C 65,150 50,135 50,100 Z" fill="#e62225"/>
                <path d="M 68,100 C 68,76 76,68 100,68 C 124,68 132,76 132,100 C 132,124 124,132 100,132 C 76,132 68,124 68,100 Z" fill="#fbb03b"/>
                <rect x="78" y="78" width="44" height="44" fill="#ffffff" rx="8"/>
                <rect x="85" y="85" width="30" height="30" fill="#0b0b0b" rx="4"/>
            </svg>
            <br>
            <span class="hero-badge">WELCOME TO MANKSIBUKGAK</span>
            <h1>Servis Motor Tanpa Antre di <span>MANKSIBUKGAK</span>,<br>Booking Online Sekarang!</h1>
            <p>Rasakan pengalaman servis motor matic & manual secara presisi dengan mekanik profesional, standar tools modern, serta jaminan garansi servis.</p>
            <button onclick="toggleTab('booking')" class="btn-hero"> Buat Janji Servis Online</button>
        </div>

        <!-- Live Status Antrean -->
        <div class="status-grid">
            <div class="status-card">
                <div>
                    <div class="status-title">Total Antrean Hari Ini</div>
                    <div id="antrean-total-home" class="status-value">0</div>
                </div>
            </div>
            <div class="status-card">
                <div>
                    <div class="status-title">Sedang Dilayani</div>
                    <div id="antrean-servis-home" class="status-value text">-</div>
                </div>
            </div>
            <div class="status-card">
                <div>
                    <div class="status-title">Nomor Terakhir</div>
                    <div id="antrean-nomor-home" class="status-value blue">#000</div>
                </div>
            </div>
        </div>

        <!-- Catalog Layanan -->
        <div class="section-header">
            <div class="section-title">Layanan Favorit Pelanggan</div>
            <div class="section-subtitle">Pilih paket perawatan terbaik sesuai kebutuhan motor kamu.</div>
        </div>

        <div class="service-grid">
            <div class="service-card">
                <div class="service-title">Servis Injeksi & Throttle Body</div>
                <div class="service-desc">Pembersihan kerak karbon, remapping ringan, dan ganti oli mesin.</div>
                <div class="service-price">Mulai Rp 75.000</div>
            </div>
            <div class="service-card">
                <div class="service-title">Servis CVT</div>
                <div class="service-desc">Pembersihan pulley, mangkok, greasing, atasi CVT gredek pada matic.</div>
                <div class="service-price">Mulai Rp 55.000</div>
            </div>
            <div class="service-card">
                <div class="service-title">Paket Oli Mesin & Oli Gardan</div>
                <div class="service-desc">Ganti oli mesin, oli gardan, setel rem, dan cek tekanan angin ban.</div>
                <div class="service-price">Mulai Rp 75.000</div>
            </div>
            <div class="service-card">
                <div class="service-title">Servis Karburator</div>
                <div class="service-desc">Pembersihan total ruang karburator, penyetelan ulang spuyer, dan kalkulasi suplai bensin.</div>
                <div class="service-price">Mulai Rp 45.000</div>
            </div>
            <div class="service-card">
                <div class="service-title">Servis Kelistrikan & Lampu</div>
                <div class="service-desc">Pengecekan aki, pengisian kiprok, ganti bohlam/LED, dan perbaikan kabel korslet.</div>
                <div class="service-price">Mulai Rp 35.000</div>
            </div>
            <div class="service-card">
                <div class="service-title">Servis Shockbraker</div>
                <div class="service-desc">Pembersihan total, penggantian oli shock, dan re-setting keempukan/rebound agar motor kembali stabil dan empuk.</div>
                <div class="service-price">Mulai Rp 150.000</div>
            </div>
            <div class="service-card">
                <div class="service-title">Servis Besar / Overhaul</div>
                <div class="service-desc">Bongkar pasang blok mesin, ganti piston, skir klep secara presisi.</div>
                <div class="service-price">Estimasi via WA</div>    
            </div>
            <div class="service-card">
                <div class="service-title">Restorasi Motor</div>
                <div class="service-desc">Pengerjaan bangun ulang motor matic/manual, repaint bodi, peremajaan part ori, hingga mesin kembali fresh seperti baru dari pabrik.</div>
                <div class="service-price">Estimasi via WA</div>
            </div>
        </div>

        <!-- Keunggulan Bengkel -->
        <div class="section-header">
            <div class="section-title">Mengapa Memilih MANKSIBUKGAK?</div>
            <div class="section-subtitle">Komitmen kami dalam memberikan kenyamanan dan hasil servis maksimal.</div>
        </div>

        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-num">1</div>
                <div class="feature-text">
                    <h4>Tanpa Buang Waktu</h4>
                    <p>Pilih jam kedatanganmu sendiri lewat sistem booking online kami.</p>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-num">2</div>
                <div class="feature-text">
                    <h4>Garansi Servis 7 Hari</h4>
                    <p>Kendaraan masih kurang enak? Bawa kembali, kami tangani tanpa biaya tambahan.</p>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-num">3</div>
                <div class="feature-text">
                    <h4>Sparepart 100% Original</h4>
                    <p>Kami hanya menyediakan suku cadang asli dan oli berkualitas terjamin.</p>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-num">4</div>
                <div class="feature-text">
                    <h4>Ruang Tunggu Santai</h4>
                    <p>Area tunggu yang bersih dan nyaman, bisa dilihat langsung oleh customer.</p>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-num">5</div>
                <div class="feature-text">
                    <h4>Transparansi Biaya</h4>
                    <p>Semua biaya perbaikan atau pergantian sparepart dikonfirmasi terlebih dahulu kepada customer.</p>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-num">6</div>
                <div class="feature-text">
                    <h4>Layanan Antar-Jemput Motor</h4>
                    <p>Sibuk kerja atau malas keluar rumah? Tim kami siap menjemput motor dari rumah/kantor Anda.</p>
                </div>
            </div>
        </div>

        <!-- SECTION CONTACT PERSON / HUBUNGI KAMI -->
        <div class="section-header">
            <div class="section-title">Hubungi Kami / Contact Person</div>
            <div class="section-subtitle">Ada pertanyaan seputar kendala motor atau booking? Tim kami siap membantu!</div>
        </div>

        <div class="contact-grid">
            <div class="contact-card">
                <div class="contact-icon">💬</div>
                <div class="contact-title">WhatsApp Admin</div>
                <div class="contact-detail">Respons cepat untuk konsultasi keluhan motor & bantuan booking.</div>
                <a href="https://wa.me/6285885618418?text=Halo%20Admin%20MANKSIBUKGAK,%20saya%20ingin%20bertanya%20seputar%20servis%20motor" target="_blank" class="btn-contact btn-contact-wa"> Chat WhatsApp</a>
            </div>
            <div class="contact-card">
                <div class="contact-icon">📍</div>
                <div class="contact-title">Lokasi Bengkel</div>
                <div class="contact-detail">Jl. Rasamala Gg. N No.12 8, Jakarta Selatan<br>(Patokan dekat area persimpangan)</div>
                <a href="https://maps.google.com/?q=Jl.+Rasamala+Gang+N+Jakarta+Selatan" target="_blank" class="btn-contact btn-contact-map"> Buka Google Maps</a>
            </div>
            <div class="contact-card">
                <div class="contact-icon">🕒</div>
                <div class="contact-title">Jam Operasional</div>
                <div class="contact-detail">Sabtu - Minggu<br><strong>08:00 WIB - 17:00 WIB</strong></div>
                <button onclick="toggleTab('booking')" class="btn-contact btn-contact-wa" style="background:#f59e0b; color:#0f172a;"> Booking Online</button>
            </div>
        </div>
    </div>

    <!-- TAB 2: FORM BOOKING -->
    <div id="tabBooking" class="container hidden">
        <div class="card">
            <div class="card-header">
                <div class="card-title">Buat Janji Servis Online</div>
                <div class="card-subtitle">Pilih tanggal, jam kedatangan, dan isi data kendaraan Anda.</div>
            </div>

            <form id="bookingForm" onsubmit="handleFormSubmit(event)">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Nama Lengkap</label>
                        <input type="text" id="nama" required placeholder="Budi Santoso">
                    </div>
                    <div class="form-group">
                        <label>Nomor WhatsApp</label>
                        <input type="tel" id="whatsapp" required placeholder="08123456789">
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Merk & Tipe Motor</label>
                        <input type="text" id="motor" required placeholder="Honda Vario 160 / NMAX">
                    </div>
                    <div class="form-group">
                        <label>Nomor Polisi (Plat)</label>
                        <input type="text" id="plat" required placeholder="B 1234 XYZ">
                    </div>
                </div>

                <!-- JENIS SERVIS: MULTI-SELECT CHECKBOX -->
                <div class="form-group" style="margin-bottom: 15px;">
                    <label>Jenis Servis (Bisa pilih lebih dari 1 opsi)</label>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; background: #0f172a; padding: 14px; border: 1px solid #334155; border-radius: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #fff; font-weight: normal;">
                            <input type="checkbox" name="jenis_service" value="Servis Injeksi & Throttle Body" style="width: auto;"> Servis Injeksi & Throttle Body
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #fff; font-weight: normal;">
                            <input type="checkbox" name="jenis_service" value="Servis CVT" style="width: auto;"> Servis CVT
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #fff; font-weight: normal;">
                            <input type="checkbox" name="jenis_service" value="Paket Oli Mesin & Oli Gardan" style="width: auto;"> Paket Oli Mesin & Oli Gardan
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #fff; font-weight: normal;">
                            <input type="checkbox" name="jenis_service" value="Servis Karburator" style="width: auto;"> Servis Karburator
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #fff; font-weight: normal;">
                            <input type="checkbox" name="jenis_service" value="Servis Kelistrikan & Lampu" style="width: auto;"> Servis Kelistrikan & Lampu
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #fff; font-weight: normal;">
                            <input type="checkbox" name="jenis_service" value="Servis Shockbraker" style="width: auto;"> Servis Shockbraker
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #fff; font-weight: normal;">
                            <input type="checkbox" name="jenis_service" value="Servis Besar / Overhaul" style="width: auto;"> Servis Besar / Overhaul
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: #fff; font-weight: normal;">
                            <input type="checkbox" name="jenis_service" value="Restorasi Motor" style="width: auto;"> Restorasi Motor
                        </label>
                    </div>
                </div>

                <div class="form-group" style="margin-bottom: 15px;">
                    <label>Tanggal Booking</label>
                    <input type="date" id="tanggal" required onchange="loadTimeSlots()">
                </div>

                <!-- PILIHAN JAM KEDATANGAN -->
                <div class="form-group" style="margin-bottom: 15px;">
                    <label>Pilih Jam Kedatangan (Kedatangan Tepat Waktu)</label>
                    <div id="timeSlotContainer" class="time-grid">
                        <!-- Slot jam dimuat via JS -->
                    </div>
                    <input type="hidden" id="selected_jam" required>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Kilometer Terakhir (KM)</label>
                        <input type="number" id="km" placeholder="15000">
                    </div>
                    <div class="form-group">
                        <label>Keluhan Kendaraan</label>
                        <input type="text" id="keluhan" placeholder="Rem berdecit, CVT gredek">
                    </div>
                </div>

                <button type="submit" id="btnSubmit" class="btn-submit btn-disabled" disabled>
                    Konfirmasi & Kirim Booking via WhatsApp
                </button>
            </form>
        </div>
    </div>

    <!-- TAB 3: PANEL ADMIN -->
    <div id="tabAdmin" class="container hidden">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <h3 style="color:#fff;">Dashboard Administrator</h3>
            <button onclick="logoutAdmin()" style="background:#ef4444; color:#fff; border:none; padding:6px 14px; border-radius:6px; font-weight:bold; cursor:pointer;">Logout Admin</button>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">Pengaturan Live Antrean Bengkel</div>
                <div class="card-subtitle">Ubah informasi antrean secara real-time untuk ditampilkan ke layar pelanggan.</div>
            </div>
            
            <div class="admin-control-grid">
                <div class="form-group">
                    <label>Kendaraan Sedang Dilayani</label>
                    <input type="text" id="admin_sedang_dilayani" placeholder="Contoh: B 1234 ABC (Vario 160)">
                </div>
                <div class="form-group">
                    <label>Nomor Terakhir Dipanggil</label>
                    <input type="number" id="admin_nomor_terakhir" placeholder="44">
                </div>
            </div>
            
            <button onclick="updateAntreanByAdmin()" class="btn-admin-action">Update Status Live Antrean</button>
        </div>

        <div class="card">
            <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="card-title">Panel Admin - Data Booking</div>
                    <div class="card-subtitle">Kelola antrean dan buat invoice (Format WA Teks, Struk Kasir Termal, atau PDF Cetak A4).</div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick="loadAdminData()" class="btn-inactive" style="padding: 6px 12px; border-radius: 6px; cursor:pointer;">Refresh Tabel</button>
                    <button onclick="resetAdminData()" style="padding: 6px 12px; border-radius: 6px; cursor:pointer; background-color: #ef4444; color: white; border: none; font-weight: 600;">Reset Semua Data</button>
                </div>
            </div>

            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>ID Booking</th>
                            <th>Pelanggan</th>
                            <th>Motor & Plat</th>
                            <th>Layanan</th>
                            <th>Jadwal Kedatangan</th>
                            <th>Aksi Admin</th>
                        </tr>
                    </thead>
                    <tbody id="adminTableBody">
                        <!-- Data masuk di sini -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- MODAL ADMIN LOGIN -->
    <div id="loginModal" class="modal-overlay hidden">
        <div class="modal-login">
            <h3 style="margin-bottom:8px; font-size:18px;">Login Panel Admin</h3>
            <p style="color:#94a3b8; font-size:12px; margin-bottom:20px;">Masukkan username dan password admin untuk melanjutkan.</p>
            
            <form onsubmit="handleAdminLogin(event)">
                <div class="form-group" style="margin-bottom:12px; text-align:left;">
                    <label>Username</label>
                    <input type="text" id="admin_username" required placeholder="admin">
                </div>
                <div class="form-group" style="margin-bottom:20px; text-align:left;">
                    <label>Password</label>
                    <input type="password" id="admin_password" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn-submit" style="margin-top:0;">Masuk Admin</button>
                <button type="button" onclick="closeLoginModal()" class="btn-close-link" style="margin-top:10px; width:100%;">Batal</button>
            </form>
        </div>
    </div>

    <!-- MODAL POPUP KONFIRMASI BOOKING PELANGGAN -->
    <div id="bookingModal" class="modal-overlay hidden">
        <div class="modal-receipt" style="text-align: center;">
            <div style="font-size: 40px; margin-bottom: 10px;"></div>
            <h2 style="font-size: 18px; color: #0f172a; margin-bottom: 8px;">Booking Berhasil Dibuat!</h2>
            <p style="font-size: 13px; color: #64748b; margin-bottom: 20px;">
                Terima kasih, data booking Anda telah tercatat. Silakan klik tombol di bawah untuk mengonfirmasi jadwal ke WhatsApp Admin Bengkel.
            </p>
            <div class="receipt-actions">
                <button onclick="confirmWhatsAppBooking()" class="btn-wa">
                     Kirim Konfirmasi Booking ke WA Admin
                </button>
                <button onclick="closeBookingModal()" class="btn-close-link">Tutup</button>
            </div>
        </div>
    </div>

    <!-- MODAL GENERATOR INVOICE FINAL (PANEL ADMIN) -->
    <div id="invoiceModal" class="modal-overlay hidden">
        <div class="modal-receipt">
            <div class="receipt-header">
                <h2>MANKSIBUKGAK</h2>
                <p>Jl. Rasamala Gg N No.12 8, Jakarta Selatan</p>
                <div style="background:#e0f2fe; color:#0369a1; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; display:inline-block; margin-top:5px;">INVOICE PELUNASAN SERVIS</div>
            </div>

            <div style="font-size:12px; border-bottom:1px dashed #cbd5e1; padding-bottom:10px; margin-bottom:10px;">
                <div><strong>Kode Booking:</strong> <span id="inv-code">-</span></div>
                <div><strong>Pelanggan:</strong> <span id="inv-nama">-</span> (<span id="inv-wa">-</span>)</div>
                <div><strong>Kendaraan:</strong> <span id="inv-motor">-</span></div>
            </div>

            <div class="form-group" style="margin-bottom:10px;">
                <label style="color:#0f172a;">Nama Mekanik</label>
                <input type="text" id="inv_mekanik" placeholder="Contoh: Fikri" style="background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1;">
            </div>

            <!-- Tabel Rincian Barang / Jasa -->
            <label style="color:#0f172a; margin-bottom:4px; display:block;">Rincian Pekerjaan & Sparepart:</label>
            <div id="invoiceItemsContainer">
                <!-- Row Item dimasukkan via JS -->
            </div>
            
            <button type="button" onclick="addInvoiceRow()" style="background:#f1f5f9; color:#334155; border:1px dashed #cbd5e1; width:100%; padding:6px; border-radius:6px; font-weight:bold; font-size:12px; cursor:pointer; margin-bottom:15px;">
                + Tambah Item Pekerjaan / Sparepart
            </button>

            <div style="display:flex; justify-content:space-between; align-items:center; background:#fef3c7; padding:10px; border-radius:8px; margin-bottom:15px; font-weight:bold; color:#b45309;">
                <span>TOTAL BAYAR:</span>
                <span id="inv-total-text">Rp 0</span>
            </div>

            <!-- Tombol 3 Opsi Pilihan Output Invoice -->
            <div class="receipt-actions">
                <button onclick="sendInvoiceToWA()" class="btn-wa">
                     Versi 1: Kirim Pesan WA Teks
                </button>
                <button onclick="openThermalStrukModal()" class="btn-thermal">
                     Versi 2: Tampilkan Struk Belanja (Kasir Termal)
                </button>
                <button onclick="downloadInvoicePDF()" class="btn-pdf">
                     Versi 3: Download PDF Invoice (A4 Resmi)
                </button>
                <button onclick="closeInvoiceModal()" class="btn-close-link">Batal</button>
            </div>
        </div>
    </div>

    <!-- MODAL TAMPILAN STRUK BELANJA (THERMAL PRINT) -->
    <div id="thermalStrukModal" class="modal-overlay hidden">
        <div style="background:#fff; color:#000; border-radius:12px; padding:20px; max-width:340px; width:100%; font-family:'Courier New', Courier, monospace; box-shadow:0 10px 25px rgba(0,0,0,0.5);">
            <div id="thermalPrintArea">
                <div style="text-align:center;">
                    <h3 style="font-size:16px; margin-bottom:2px;">MANKSIBUKGAK</h3>
                    <p style="font-size:10px;">Jl. Rasamala Gg N No.12 8, Jakarta Selatan</p>
                    <p style="font-size:10px;">Telp/WA: 085885618418</p>
                    <p style="margin:6px 0;">--------------------------------</p>
                </div>
                
                <div style="font-size:11px; line-height:1.4;">
                    <div>No. Nota : <span id="th-code">-</span></div>
                    <div>Tanggal  : <span id="th-tanggal">-</span></div>
                    <div>Mekanik  : <span id="th-mekanik">-</span></div>
                    <div>Cust.    : <span id="th-nama">-</span></div>
                    <div>Motor    : <span id="th-motor">-</span></div>
                </div>

                <p style="margin:6px 0;">--------------------------------</p>

                <!-- Table Item Struk -->
                <div id="th-items-container" style="font-size:11px;">
                    <!-- Item Rincian Struk Dimuat via JS -->
                </div>

                <p style="margin:6px 0;">--------------------------------</p>

                <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:12px;">
                    <span>TOTAL BAYAR:</span>
                    <span id="th-total">Rp 0</span>
                </div>

                <p style="margin:6px 0;">--------------------------------</p>
                <div style="text-align:center; font-size:10px; margin-top:8px;">
                    <p>BCA 7510798427 a.n Mank Sibuk Gak</p>
                    <p style="margin-top:4px;">*** TERIMA KASIH ***</p>
                    <p>Garansi Servis 7 Hari</p>
                </div>
            </div>

            <div style="margin-top:15px; display:flex; flex-direction:column; gap:6px;">
                <button onclick="window.print()" style="background:#0f172a; color:#fff; border:none; padding:8px; border-radius:6px; font-weight:bold; cursor:pointer;"> Cetak Struk</button>
                <button onclick="closeThermalStrukModal()" style="background:transparent; border:none; color:#64748b; font-size:12px; cursor:pointer;">Tutup</button>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('tanggal').value = new Date().toISOString().split('T')[0];

        let currentBookingData = {};
        let currentBookingId = 0;
        let selectedAdminBooking = null;
        let isAdminLoggedIn = false;

        // Auto-Polling Antrean
        function fetchLiveStatus() {
            fetch('/api/live-status')
                .then(res => res.json())
                .then(data => {
                    let numStr = "#" + data.nomor_terakhir.toString().padStart(3, '0');
                    document.getElementById('antrean-total-home').innerText = data.total_antrean;
                    document.getElementById('antrean-servis-home').innerText = data.sedang_dilayani;
                    document.getElementById('antrean-nomor-home').innerText = numStr;
                });
        }

        fetchLiveStatus();
        setInterval(fetchLiveStatus, 3000);

        function loadTimeSlots() {
            const tanggal = document.getElementById('tanggal').value;
            const container = document.getElementById('timeSlotContainer');
            document.getElementById('selected_jam').value = '';
            
            const btnSubmit = document.getElementById('btnSubmit');
            btnSubmit.disabled = true;
            btnSubmit.classList.add('btn-disabled');

            fetch(`/api/get-slots?tanggal=${tanggal}`)
                .then(res => res.json())
                .then(data => {
                    container.innerHTML = data.slots.map(slot => {
                        if (slot.is_booked) {
                            return `<div class="btn-time disabled" title="Sudah Penuh">${slot.jam} (Penuh)</div>`;
                        } else {
                            return `<div class="btn-time" onclick="selectJam('${slot.jam}', this)">${slot.jam} WIB</div>`;
                        }
                    }).join('');
                });
        }

        function selectJam(jam, element) {
            document.querySelectorAll('.btn-time').forEach(el => el.classList.remove('selected'));
            element.classList.add('selected');
            document.getElementById('selected_jam').value = jam;

            const btnSubmit = document.getElementById('btnSubmit');
            btnSubmit.disabled = false;
            btnSubmit.classList.remove('btn-disabled');
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            
            const checkedServices = Array.from(document.querySelectorAll('input[name="jenis_service"]:checked'))
                .map(cb => cb.value);

            if (checkedServices.length === 0) {
                alert("Silakan pilih minimal satu jenis servis!");
                return;
            }

            const jamSelected = document.getElementById('selected_jam').value;
            if(!jamSelected) {
                alert("Silakan pilih jam kedatangan terlebih dahulu!");
                return;
            }

            currentBookingData = {
                nama: document.getElementById('nama').value,
                whatsapp: document.getElementById('whatsapp').value,
                motor: document.getElementById('motor').value,
                plat: document.getElementById('plat').value,
                jenis_service: checkedServices.join(', '),
                tanggal: document.getElementById('tanggal').value,
                jam: jamSelected,
                km: document.getElementById('km').value,
                keluhan: document.getElementById('keluhan').value
            };

            fetch('/api/submit-booking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentBookingData)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentBookingId = data.booking_id;
                    document.getElementById('bookingModal').classList.remove('hidden');
                    fetchLiveStatus();
                } else {
                    alert(data.message);
                }
            });
        }

        function confirmWhatsAppBooking() {
            const noWA = "6285885618418";
            const idBookingStr = "#YN-" + String(currentBookingId).padStart(4, '0');
            
            const text = 
`============================
 *BOOKING SERVIS MANK SIBUK GAK*
============================
*No. Booking  :* ${idBookingStr}
*Nama Customer:* ${currentBookingData.nama}
*No. WhatsApp :* ${currentBookingData.whatsapp}
*Kendaraan    :* ${currentBookingData.motor} (${currentBookingData.plat})
*Layanan      :* ${currentBookingData.jenis_service}
*Jadwal       :* ${currentBookingData.tanggal} @ ${currentBookingData.jam} WIB
*KM Terakhir  :* ${currentBookingData.km || '-'}
*Keluhan      :* ${currentBookingData.keluhan || '-'}
============================

Halo Admin MANKSIBUKGAK, saya baru saja membuat janji servis melalui website. Mohon konfirmasinya. Terima kasih!`;
            
            window.open(`https://wa.me/${noWA}?text=${encodeURIComponent(text)}`, '_blank');
            closeBookingModal();
        }

        function closeBookingModal() {
            document.getElementById('bookingModal').classList.add('hidden');
            document.getElementById('bookingForm').reset();
            loadTimeSlots();
        }

        /* --- LOGIKA ADMIN --- */
        function toggleTab(tab) {
            if (tab === 'admin' && !isAdminLoggedIn) {
                document.getElementById('loginModal').classList.remove('hidden');
                return;
            }

            document.getElementById('tabHome').classList.add('hidden');
            document.getElementById('tabBooking').classList.add('hidden');
            document.getElementById('tabAdmin').classList.add('hidden');

            document.getElementById('btnTabHome').className = "btn-tab btn-inactive";
            document.getElementById('btnTabBooking').className = "btn-tab btn-inactive";
            document.getElementById('btnTabAdmin').className = "btn-tab btn-inactive";

            if(tab === 'home') {
                document.getElementById('tabHome').classList.remove('hidden');
                document.getElementById('btnTabHome').className = "btn-tab btn-active";
            } else if(tab === 'booking') {
                document.getElementById('tabBooking').classList.remove('hidden');
                document.getElementById('btnTabBooking').className = "btn-tab btn-active";
                loadTimeSlots();
            } else if(tab === 'admin') {
                document.getElementById('tabAdmin').classList.remove('hidden');
                document.getElementById('btnTabAdmin').className = "btn-tab btn-active";
                loadAdminData();
            }
        }

        function handleAdminLogin(e) {
            e.preventDefault();
            const u = document.getElementById('admin_username').value;
            const p = document.getElementById('admin_password').value;

            fetch('/api/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: u, password: p })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    isAdminLoggedIn = true;
                    document.getElementById('loginModal').classList.add('hidden');
                    document.getElementById('admin_username').value = '';
                    document.getElementById('admin_password').value = '';
                    toggleTab('admin');
                } else {
                    alert(data.message);
                }
            });
        }

        function closeLoginModal() {
            document.getElementById('loginModal').classList.add('hidden');
        }

        function logoutAdmin() {
            isAdminLoggedIn = false;
            alert("Anda berhasil logout dari Panel Admin.");
            toggleTab('home');
        }

        function loadAdminData() {
            fetch('/api/admin/bookings')
                .then(res => res.json())
                .then(data => {
                    const tbody = document.getElementById('adminTableBody');
                    if(data.length === 0) {
                        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#64748b; padding:20px;">Belum ada booking masuk</td></tr>`;
                        return;
                    }
                    tbody.innerHTML = data.map(b => {
                        return `
                        <tr>
                            <td>#YN-${String(b.id).padStart(4, '0')}</td>
                            <td><strong>${b.nama}</strong><br><small style="color:#94a3b8">${b.whatsapp}</small></td>
                            <td>${b.motor}<br><small style="color:#94a3b8">${b.plat}</small></td>
                            <td>${b.jenis_service}</td>
                            <td>${b.tanggal}<br><small style="color:#f59e0b">${b.jam} WIB</small></td>
                            <td>
                                <button onclick='openInvoiceModal(${JSON.stringify(b)})' class="btn-invoice"> Buat Invoice</button><br>
                                <button onclick="deleteBooking(${b.id})" class="btn-delete"> Hapus</button>
                            </td>
                        </tr>
                    `}).join('');
                });
        }

        /* LOGIKA INVOICE MODAL ADMIN */
        function openInvoiceModal(bookingObj) {
            selectedAdminBooking = bookingObj;
            document.getElementById('inv-code').innerText = "#YN-" + String(bookingObj.id).padStart(4, '0');
            document.getElementById('inv-nama').innerText = bookingObj.nama;
            document.getElementById('inv-wa').innerText = bookingObj.whatsapp;
            document.getElementById('inv-motor').innerText = `${bookingObj.motor} (${bookingObj.plat})`;
            
            const container = document.getElementById('invoiceItemsContainer');
            container.innerHTML = '';
            
            addInvoiceRow(bookingObj.jenis_service, 1, 0);
            document.getElementById('invoiceModal').classList.remove('hidden');
        }

        function addInvoiceRow(desc = '', qty = 1, price = 0) {
            const container = document.getElementById('invoiceItemsContainer');
            const rowId = Date.now() + Math.random();
            
            const div = document.createElement('div');
            div.className = 'item-row';
            div.style.cssText = "display: flex; gap: 6px; margin-bottom: 8px; align-items: center;";
            div.id = 'row-' + rowId;
            div.innerHTML = `
                <input type="text" placeholder="Keterangan / Part" value="${desc}" class="item-desc" style="flex:2; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; font-size:12px; padding:6px;">
                <input type="number" placeholder="Qty" value="${qty}" class="item-qty" onchange="calculateInvoiceTotal()" style="width:50px; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; font-size:12px; padding:6px;">
                <input type="number" placeholder="Harga" value="${price}" class="item-price" onchange="calculateInvoiceTotal()" style="flex:1; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; font-size:12px; padding:6px;">
                <button type="button" onclick="removeInvoiceRow('row-${rowId}')" style="background:#ef4444; color:#fff; border:none; border-radius:4px; padding:6px 8px; cursor:pointer; font-size:11px;">✕</button>
            `;
            container.appendChild(div);
            calculateInvoiceTotal();
        }

        function removeInvoiceRow(id) {
            const el = document.getElementById(id);
            if(el) el.remove();
            calculateInvoiceTotal();
        }

        function calculateInvoiceTotal() {
            let total = 0;
            const descs = document.querySelectorAll('.item-desc');
            const qtys = document.querySelectorAll('.item-qty');
            const prices = document.querySelectorAll('.item-price');

            for(let i=0; i < descs.length; i++) {
                const q = parseFloat(qtys[i].value) || 0;
                const p = parseFloat(prices[i].value) || 0;
                total += (q * p);
            }

            document.getElementById('inv-total-text').innerText = "Rp " + total.toLocaleString('id-ID');
            return total;
        }

        // VERSI 1: KIRIM VIA WA TEKS
        function sendInvoiceToWA() {
            if(!selectedAdminBooking) return;
            const mekanik = document.getElementById('inv_mekanik').value || '-';
            const descs = document.querySelectorAll('.item-desc');
            const qtys = document.querySelectorAll('.item-qty');
            const prices = document.querySelectorAll('.item-price');

            let itemText = '';
            let total = 0;

            for(let i=0; i < descs.length; i++) {
                const name = descs[i].value || 'Jasa/Part';
                const q = parseFloat(qtys[i].value) || 0;
                const p = parseFloat(prices[i].value) || 0;
                const sub = q * p;
                total += sub;

                itemText += `• ${name} (${q}x @Rp ${p.toLocaleString('id-ID')}) : Rp ${sub.toLocaleString('id-ID')}\n`;
            }

            const codeStr = "#YN-" + String(selectedAdminBooking.id).padStart(4, '0');
            const targetWA = selectedAdminBooking.whatsapp.replace(/[^0-9]/g, '');
            const formattedWA = targetWA.startsWith('0') ? '62' + targetWA.slice(1) : targetWA;

            const text = 
`============================
 *INVOICE SERVIS - MANKSIBUKGAK*
============================
*Kode Booking :* ${codeStr}
*Tanggal      :* ${selectedAdminBooking.tanggal}
*Mekanik      :* ${mekanik}

*PELANGGAN :*
${selectedAdminBooking.nama}
${selectedAdminBooking.motor} (${selectedAdminBooking.plat})

--------------------------------
*RINCIAN BIAYA :*
${itemText}--------------------------------
*TOTAL BAYAR  :* Rp ${total.toLocaleString('id-ID')}
============================
*Pembayaran Transfer:*
BCA 7510798427 a.n Mank Sibuk Gak

Terima kasih telah mempercayakan servis kendaraan Anda di *MANKSIBUKGAK*.
Simpan invoice ini sebagai bukti pembayaran yang sah.`;

            window.open(`https://wa.me/${formattedWA}?text=${encodeURIComponent(text)}`, '_blank');
            closeInvoiceModal();
        }

        // VERSI 2: POPUP STRUK BELANJA (THERMAL PRINT)
        function openThermalStrukModal() {
            if(!selectedAdminBooking) return;

            const mekanik = document.getElementById('inv_mekanik').value || '-';
            const codeStr = "#YN-" + String(selectedAdminBooking.id).padStart(4, '0');

            document.getElementById('th-code').innerText = codeStr;
            document.getElementById('th-tanggal').innerText = selectedAdminBooking.tanggal;
            document.getElementById('th-mekanik').innerText = mekanik;
            document.getElementById('th-nama').innerText = selectedAdminBooking.nama;
            document.getElementById('th-motor').innerText = `${selectedAdminBooking.motor} (${selectedAdminBooking.plat})`;

            const descs = document.querySelectorAll('.item-desc');
            const qtys = document.querySelectorAll('.item-qty');
            const prices = document.querySelectorAll('.item-price');

            let container = document.getElementById('th-items-container');
            container.innerHTML = '';
            let grandTotal = 0;

            for(let i=0; i < descs.length; i++) {
                const name = descs[i].value || 'Jasa/Part';
                const q = parseFloat(qtys[i].value) || 0;
                const p = parseFloat(prices[i].value) || 0;
                const sub = q * p;
                grandTotal += sub;

                const row = document.createElement('div');
                row.style.marginBottom = '4px';
                row.innerHTML = `
                    <div>${name}</div>
                    <div style="display:flex; justify-content:space-between; color:#475569;">
                        <span>${q} x Rp ${p.toLocaleString('id-ID')}</span>
                        <span>Rp ${sub.toLocaleString('id-ID')}</span>
                    </div>
                `;
                container.appendChild(row);
            }

            document.getElementById('th-total').innerText = "Rp " + grandTotal.toLocaleString('id-ID');
            document.getElementById('thermalStrukModal').classList.remove('hidden');
        }

        function closeThermalStrukModal() {
            document.getElementById('thermalStrukModal').classList.add('hidden');
        }

        // VERSI 3: DOWNLOAD PDF INVOICE
        function downloadInvoicePDF() {
            if(!selectedAdminBooking) return;
            const mekanik = document.getElementById('inv_mekanik').value || '-';
            const descs = document.querySelectorAll('.item-desc');
            const qtys = document.querySelectorAll('.item-qty');
            const prices = document.querySelectorAll('.item-price');

            let items = [];
            for(let i=0; i < descs.length; i++) {
                items.push({
                    desc: descs[i].value || 'Jasa/Part',
                    qty: parseFloat(qtys[i].value) || 0,
                    price: parseFloat(prices[i].value) || 0
                });
            }

            const payload = {
                id: selectedAdminBooking.id,
                nama: selectedAdminBooking.nama,
                whatsapp: selectedAdminBooking.whatsapp,
                motor: selectedAdminBooking.motor,
                plat: selectedAdminBooking.plat,
                tanggal: selectedAdminBooking.tanggal,
                jam: selectedAdminBooking.jam,
                keluhan: selectedAdminBooking.keluhan,
                mekanik: mekanik,
                items: items
            };

            fetch('/api/admin/generate-invoice-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Invoice_${selectedAdminBooking.nama}_${selectedAdminBooking.id}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            });
        }

        function closeInvoiceModal() {
            document.getElementById('invoiceModal').classList.add('hidden');
        }

        function deleteBooking(id) {
            if(confirm(`Apakah Anda yakin ingin menghapus data booking #YN-${String(id).padStart(4, '0')}?`)) {
                fetch('/api/admin/delete-booking', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: id })
                })
                .then(res => res.json())
                .then(data => {
                    if(data.success) {
                        loadAdminData();
                    } else {
                        alert(data.message);
                    }
                });
            }
        }

        function updateAntreanByAdmin() {
            const sedangDilayani = document.getElementById('admin_sedang_dilayani').value;
            const nomorTerakhir = document.getElementById('admin_nomor_terakhir').value;

            fetch('/api/admin/update-live-status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sedang_dilayani: sedangDilayani,
                    nomor_terakhir: nomorTerakhir
                })
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    alert("Status Antrean Live Berhasil Diperbarui!");
                    fetchLiveStatus();
                }
            });
        }

        function resetAdminData() {
            if(confirm("Apakah Anda yakin ingin mereset seluruh data booking dan antrean?")) {
                fetch('/api/admin/reset', { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        alert(data.message);
                        loadAdminData();
                        fetchLiveStatus();
                    });
            }
        }
    </script>
</body>
</html>
"""

# --- FLASK ROUTES ---

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.route('/api/live-status', methods=['GET'])
def get_live_status():
    return jsonify(antrean_live)

@app.route('/api/get-slots', methods=['GET'])
def get_slots():
    tanggal = request.args.get('tanggal')
    jam_terisi = jam_terisi_db.get(tanggal, [])
    
    slots = []
    for jam in JAM_OPERASIONAL:
        slots.append({
            "jam": jam,
            "is_booked": jam in jam_terisi
        })
    return jsonify({"slots": slots})

@app.route('/api/submit-booking', methods=['POST'])
def submit_booking():
    data = request.json
    tanggal = data.get('tanggal')
    jam = data.get('jam')

    if tanggal not in jam_terisi_db:
        jam_terisi_db[tanggal] = []

    if jam in jam_terisi_db[tanggal]:
        return jsonify({"success": False, "message": "Slot jam tersebut baru saja terisi, silakan pilih jam lain."})

    jam_terisi_db[tanggal].append(jam)
    
    booking_id = len(data_booking_pelanggan) + 1
    data['id'] = booking_id
    data_booking_pelanggan.append(data)
    
    antrean_live['total_antrean'] += 1

    return jsonify({"success": True, "booking_id": booking_id})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    u = data.get('username')
    p = data.get('password')

    if u == ADMIN_CREDENTIALS['username'] and p == ADMIN_CREDENTIALS['password']:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Username atau Password salah!"})

@app.route('/api/admin/bookings', methods=['GET'])
def get_admin_bookings():
    return jsonify(data_booking_pelanggan)

# --- GENERATE PDF INVOICE ROUTE ---
@app.route('/api/admin/generate-invoice-pdf', methods=['POST'])
def generate_invoice_pdf():
    data = request.json
    booking_id = data.get('id', 1)
    nama = data.get('nama', '-')
    wa = data.get('whatsapp', '-')
    motor = data.get('motor', '-')
    plat = data.get('plat', '-')
    tanggal = data.get('tanggal', '-')
    jam = data.get('jam', '-')
    keluhan = data.get('keluhan', '-')
    mekanik = data.get('mekanik', '-')
    items = data.get('items', [])

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=16, leading=18, textColor=colors.HexColor('#0f172a'), alignment=0
    )
    subtitle_style = ParagraphStyle(
        'SubStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#475569')
    )

    # Header Bengkel
    elements.append(Paragraph("<b>MANKSIBUKGAK</b>", title_style))
    elements.append(Paragraph("Specialist Service & Sparepart Motor", ParagraphStyle('Sub', parent=subtitle_style, fontName='Helvetica-Bold')))
    elements.append(Paragraph("Jl. Rasamala Gg. N No.12 8, Jakarta Selatan", subtitle_style))
    elements.append(Spacer(1, 15))

    # Judul Invoice & Info Booking
    code_str = f"BOM-261010-{str(booking_id).zfill(3)}"
    info_data = [
        [Paragraph("<b>INVOICE</b>", ParagraphStyle('Inv', parent=title_style, fontSize=14)), Paragraph(f"<b>Kode Booking:</b> {code_str}", subtitle_style)],
        [Paragraph(f"<b>Tanggal:</b> {tanggal}", subtitle_style), Paragraph(f"<b>Jam:</b> {jam} WIB", subtitle_style)],
        [Paragraph(f"<b>Mekanik:</b> {mekanik}", subtitle_style), Paragraph(f"<b>Keluhan:</b> {keluhan}", subtitle_style)],
    ]
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    # Data Pelanggan
    cust_data = [
        [Paragraph(f"<b>PELANGGAN:</b><br/>{nama}<br/>{wa}<br/>{motor} ({plat})", subtitle_style)]
    ]
    cust_table = Table(cust_data, colWidths=[520])
    cust_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(cust_table)
    elements.append(Spacer(1, 15))

    # Tabel Rincian Biaya
    table_data = [["Keterangan", "Qty", "Harga Satuan", "Total"]]
    grand_total = 0

    for item in items:
        desc = item.get('desc', 'Jasa/Part')
        qty = item.get('qty', 1)
        price = item.get('price', 0)
        sub = qty * price
        grand_total += sub

        table_data.append([
            desc,
            str(qty),
            f"Rp {price:,.0f}".replace(",", "."),
            f"Rp {sub:,.0f}".replace(",", ".")
        ])

    table_data.append(["", "", "Subtotal:", f"Rp {grand_total:,.0f}".replace(",", ".")])
    table_data.append(["", "", "Total Bayar:", f"Rp {grand_total:,.0f}".replace(",", ".")])

    item_table = Table(table_data, colWidths=[260, 50, 105, 105])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-3), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (-2,-2), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (-2,-2), (-1,-1), 1, colors.HexColor('#0f172a')),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 20))

    # Footer Pembayaran
    footer_text = """
    <b>Transfer Pembayaran:</b> BCA 7510798427 a.n Mank Sibuk Gak<br/>
    Terima kasih telah mempercayakan servis kendaraan Anda kepada kami.<br/>
    <i>Simpan invoice ini sebagai bukti pembayaran yang sah.</i>
    """
    elements.append(Paragraph(footer_text, ParagraphStyle('Foot', parent=subtitle_style, alignment=1)))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Invoice_{nama}_{booking_id}.pdf", mimetype='application/pdf')

@app.route('/api/admin/delete-booking', methods=['POST'])
def delete_booking():
    req_data = request.json
    booking_id = req_data.get('id')

    global data_booking_pelanggan, jam_terisi_db
    
    for i, item in enumerate(data_booking_pelanggan):
        if item['id'] == booking_id:
            tgl = item.get('tanggal')
            jam = item.get('jam')
            if tgl in jam_terisi_db and jam in jam_terisi_db[tgl]:
                jam_terisi_db[tgl].remove(jam)

            del data_booking_pelanggan[i]
            
            if antrean_live['total_antrean'] > 0:
                antrean_live['total_antrean'] -= 1
                
            return jsonify({"success": True})
            
    return jsonify({"success": False, "message": "Data booking tidak ditemukan"})

@app.route('/api/admin/update-live-status', methods=['POST'])
def update_live_status():
    data = request.json
    if data.get('sedang_dilayani'):
        antrean_live['sedang_dilayani'] = data.get('sedang_dilayani')
    if data.get('nomor_terakhir'):
        antrean_live['nomor_terakhir'] = int(data.get('nomor_terakhir'))
    return jsonify({"success": True})

@app.route('/api/admin/reset', methods=['POST'])
def reset_admin_data():
    global data_booking_pelanggan, jam_terisi_db, antrean_live
    data_booking_pelanggan = []
    jam_terisi_db = {}
    antrean_live = {
        "total_antrean": 0,
        "sedang_dilayani": "-",
        "nomor_terakhir": 0
    }
    return jsonify({"success": True, "message": "Data berhasil direset!"})

if __name__ == '__main__':
    app.run(debug=True)