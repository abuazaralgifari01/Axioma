import datetime as dt
import os
import re
import textwrap

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Axioma Perpustakaan", layout="wide")

# Folder gambar (opsional). Isi dengan file .png/.jpg sesuai nama di bawah, contoh:
#   logo.png, beranda_1.jpg, beranda_2.jpg, buku_anak.jpg, komik.jpg, sejarah.jpg,
#   seni_budaya.jpg, chairil_anwar.jpg, eka_kurniawan.jpg, dee_lestari.jpg, tere_liye.jpg
# Kalau di Google Colab, ganti ke: "/content/drive/MyDrive/Colab Notebooks/gambar"
IMG_DIR = "gambar"


# -------- SESSION LOGIN --------
if "login" not in st.session_state:
    st.session_state.login = False

# -------- HALAMAN LOGIN MODERN --------
if not st.session_state.login:

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 10% 15%, rgba(255,215,106,.18), transparent 28%),
            linear-gradient(135deg, #10263D, #243B55, #162F49);
        min-height: 100vh;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMain"] .block-container {
        max-width: 1100px;
        padding-top: 5rem;
    }

    .login-brand {
        color: white;
        font-family: Georgia, serif;
        font-size: 68px;
        font-weight: bold;
        letter-spacing: 3px;
        margin-bottom: 15px;
    }

    .login-brand span {
        color: #FFD76A;
    }

    .login-subtitle {
        color: #FFD76A;
        font-size: 13px;
        font-weight: bold;
        letter-spacing: 3px;
        margin-bottom: 20px;
    }

    .login-description {
        color: #E1E8EF;
        font-size: 19px;
        line-height: 1.7;
    }

    .login-footer {
        color: #B8C7D6;
        text-align: center;
        font-size: 12px;
        margin-top: 35px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border-radius: 22px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 20px 60px rgba(0,0,0,.22);
    padding: 15px;
}

    [data-testid="stTextInput"] label {
        color: #243B55 !important;
        font-weight: 600;
    }

    [data-testid="stTextInput"] input {
        background: #F5F7FA !important;
        border: 1px solid #D9E1EA !important;
        border-radius: 10px !important;
        min-height: 45px;
    }

    div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 48px;
        background: #FFD76A !important;
        color: #243B55 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        transition: .3s;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: #F2C94C !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(213,169,40,.3);
    }

    @media (max-width: 700px) {
        [data-testid="stMain"] .block-container {
            padding: 2rem 1rem;
        }

        .login-brand {
            font-size: 48px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Membagi halaman menjadi dua kolom
    kiri, kanan = st.columns([1.1, 0.9], gap="large")

    
    with kiri:
        html_kiri = (
            '<div style="padding-top:55px;">'
            '<div class="login-subtitle">PERPUSTAKAAN DIGITAL</div>'
            '<div class="login-brand">AXIOMA<span>.</span></div>'
            '<div class="login-description">'
            'Gerbang pengetahuan untuk membuka wawasan '
            'dan menemukan inspirasi.'
            '</div>'
            '<div style="color:#FFD76A;margin-top:35px;'
            'font-size:13px;letter-spacing:2px;">'
            'KNOWLEDGE • DISCOVERY • INSPIRATION'
            '</div>'
            '</div>'
        )

        st.markdown(html_kiri, unsafe_allow_html=True)

    
    with kanan:
        with st.container(border=True):

            st.markdown("""
<h2 style="
    color: #243B55 !important;
    background: transparent;
    font-family: Georgia, serif;
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 8px;">
    Selamat Datang
</h2>

<p style="
    color: #64748B !important;
    background: transparent;">
    Silakan login untuk masuk ke AXIOMA
</p>
""", unsafe_allow_html=True)
            with st.form("form_login"):
                username = st.text_input(
                    "Username",
                    placeholder="Masukkan username"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Masukkan password"
                )

                tombol_login = st.form_submit_button(
                    "MASUK KE AXIOMA →",
                    use_container_width=True
                )

                if tombol_login:
                    if username == "admin" and password == "12":
                        st.session_state.login = True
                        st.rerun()
                    else:
                        st.error("Username atau password salah!")

    st.markdown("""
    <div class="login-footer">
        © AXIOMA PERPUSTAKAAN
        · Ruang untuk bertumbuh melalui pengetahuan
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ----------------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------------
JENIS = ["Buku anak", "Komik", "Buku Pelajaran", "Ensiklopedia", "Majalah", "Novel"]
KATEGORI = ["Sejarah", "Pendidikan", "Agama", "Bahasa", "Teknologi", "Sains", "Seni & Budaya", "Sosial"]
PENULIS = ["Chairil Anwar", "Eka Kurniawan", "Dee Lestari", "Tere Liye"]

# (judul, penulis, jenis, kategori, tahun)
BUKU_AWAL = [
    # Buku anak
    ("Si Kancil dan Buaya", "Anonim", "Buku anak", "Seni & Budaya", 2015),
    ("Malin Kundang", "Anonim", "Buku anak", "Seni & Budaya", 2016),
    ("Kumpulan Dongeng Nusantara", "Tim Axioma", "Buku anak", "Seni & Budaya", 2019),
    ("Belajar Huruf dan Angka", "Tim Axioma", "Buku anak", "Pendidikan", 2020),
    ("Kisah Nabi untuk Anak", "Tim Axioma", "Buku anak", "Agama", 2018),
    ("Aku Cinta Sains", "Tim Axioma", "Buku anak", "Sains", 2021),
    # Komik
    ("One Piece Vol. 98", "Eiichiro Oda", "Komik", "Seni & Budaya", 2020),
    ("Si Juki", "Faza Meonk", "Komik", "Seni & Budaya", 2014),
    ("Doraemon Vol. 1", "Fujiko F. Fujio", "Komik", "Seni & Budaya", 2012),
    ("Komik Sejarah: Majapahit", "Tim Axioma", "Komik", "Sejarah", 2017),
    ("Komik Sains: Tata Surya", "Tim Axioma", "Komik", "Sains", 2019),
    # Buku pelajaran
    ("Matematika SMA Kelas XI", "Kemdikbud", "Buku Pelajaran", "Pendidikan", 2022),
    ("Fisika Dasar", "Halliday", "Buku Pelajaran", "Sains", 2018),
    ("Bahasa Indonesia SMP", "Kemdikbud", "Buku Pelajaran", "Bahasa", 2021),
    ("Sejarah Indonesia SMA", "Kemdikbud", "Buku Pelajaran", "Sejarah", 2020),
    ("Pemrograman Dasar Python", "Tim Axioma", "Buku Pelajaran", "Teknologi", 2023),
    ("Sosiologi Kelas X", "Kemdikbud", "Buku Pelajaran", "Sosial", 2021),
    # Ensiklopedia
    ("The World Encyclopedia", "Tim Redaksi", "Ensiklopedia", "Sosial", 2018),
    ("Ensiklopedia Sains", "Tim Redaksi", "Ensiklopedia", "Sains", 2019),
    ("Ensiklopedia Sejarah Dunia", "Tim Redaksi", "Ensiklopedia", "Sejarah", 2017),
    ("Ensiklopedia Teknologi", "Tim Redaksi", "Ensiklopedia", "Teknologi", 2022),
    # Majalah
    ("National Geographic Indonesia", "Redaksi NatGeo", "Majalah", "Sains", 2024),
    ("Tempo", "Redaksi Tempo", "Majalah", "Sosial", 2024),
    ("Intisari", "Redaksi Intisari", "Majalah", "Sosial", 2023),
    ("Tech Review", "Redaksi Tech Review", "Majalah", "Teknologi", 2024),
    # Novel
    ("Bumi Manusia", "Pramoedya Ananta Toer", "Novel", "Sejarah", 1980),
    ("Laskar Pelangi", "Andrea Hirata", "Novel", "Pendidikan", 2005),
    ("Ayat-Ayat Cinta", "Habiburrahman El Shirazy", "Novel", "Agama", 2004),
    ("Deru Campur Debu", "Chairil Anwar", "Novel", "Bahasa", 1949),
    ("Aku Ini Binatang Jalang", "Chairil Anwar", "Novel", "Bahasa", 1986),
    ("Cantik Itu Luka", "Eka Kurniawan", "Novel", "Seni & Budaya", 2002),
    ("Lelaki Harimau", "Eka Kurniawan", "Novel", "Sosial", 2004),
    ("Seperti Dendam, Rindu Harus Dibayar Tuntas", "Eka Kurniawan", "Novel", "Sosial", 2014),
    ("Supernova: Ksatria, Puteri, dan Bintang Jatuh", "Dee Lestari", "Novel", "Sains", 2001),
    ("Perahu Kertas", "Dee Lestari", "Novel", "Seni & Budaya", 2009),
    ("Filosofi Kopi", "Dee Lestari", "Novel", "Seni & Budaya", 2006),
    ("Pulang", "Tere Liye", "Novel", "Sejarah", 2015),
    ("Hujan", "Tere Liye", "Novel", "Teknologi", 2016),
    ("Bumi", "Tere Liye", "Novel", "Sains", 2014),
    ("Negeri Para Bedebah", "Tere Liye", "Novel", "Sosial", 2012),
]

BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
DENDA_PER_HARI = 1500

MENU = ["Beranda", "Panduan", "Jenis Buku", "Kategori Buku", "Arsip Perpustakaan", "Chatbot"]
MENU_ICONS = ["house", "person", "book", "tags", "archive", "chat-dots"]


def fmt(d):
    return f"{d.day:02d} {BULAN[d.month - 1]} {d.year}" if d else "-"


def rupiah(n):
    return f"Rp{n:,}".replace(",", ".")


def init_state():
    if "init" in st.session_state:
        return
    st.session_state.init = True
    st.session_state.menu_index = 0
    st.session_state.detail = None
    st.session_state.pinjam_id = None
    st.session_state.buku = [
        dict(id=i + 1, judul=j, penulis=p, jenis=je, kategori=k, tahun=t, stok=3)
        for i, (j, p, je, k, t) in enumerate(BUKU_AWAL)
    ]
    today = dt.date.today()
    seed = [
        ("Rizky Pratama", "Bumi Manusia", 14, False),
        ("Salsabila Putri", "Laskar Pelangi", 20, False),
        ("Fahri Ramadhan", "One Piece Vol. 98", 3, False),
        ("Dewi Anggraini", "Cantik Itu Luka", 25, False),
        ("Budi Santoso", "Pulang", 30, True),
    ]
    st.session_state.pinjaman = []
    for nama, judul, lalu, kembali in seed:
        b = next(x for x in st.session_state.buku if x["judul"] == judul)
        tgl = today - dt.timedelta(days=lalu)
        rec = dict(
            nama=nama,
            buku_id=b["id"],
            tgl_pinjam=tgl,
            batas=tgl + dt.timedelta(days=14),
            tgl_kembali=(tgl + dt.timedelta(days=10)) if kembali else None,
        )
        if not kembali:
            b["stok"] -= 1
        st.session_state.pinjaman.append(rec)


init_state()


def get_buku(bid):
    return next(b for b in st.session_state.buku if b["id"] == bid)


def status(rec):
    if rec["tgl_kembali"]:
        return "Dikembalikan"
    return "Terlambat" if dt.date.today() > rec["batas"] else "Dipinjam"


def hari_telat(rec):
    akhir = rec["tgl_kembali"] or dt.date.today()
    return max((akhir - rec["batas"]).days, 0)


def loans_df(recs):
    rows = []
    for n, r in enumerate(recs, 1):
        h = hari_telat(r)
        rows.append(
            {
                "No": n,
                "Nama Anggota": r["nama"],
                "Judul Buku": get_buku(r["buku_id"])["judul"],
                "Tanggal Pinjam": fmt(r["tgl_pinjam"]),
                "Batas Pengembalian": fmt(r["batas"]),
                "Tanggal Kembali": fmt(r["tgl_kembali"]),
                "Status": status(r),
                "Denda": rupiah(h * DENDA_PER_HARI) if h else "-",
            }
        )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# NAVIGASI
# ----------------------------------------------------------------------------
def nav(halaman, detail=None, pinjam_id=None):
    st.session_state.menu_index = MENU.index(halaman)
    st.session_state.detail = detail
    if pinjam_id is not None:
        st.session_state.pinjam_id = pinjam_id


def on_menu_change(key):
    st.session_state.menu_index = MENU.index(st.session_state[key])
    st.session_state.detail = None


# ----------------------------------------------------------------------------
# GAYA
# ----------------------------------------------------------------------------
NAVY = "#243B55"
GOLD = "#FFD76A"
st.markdown("""
<style>

/* Warna background utama */
.stApp {
    background-color: #FFFFFF;
}

/* Tombol utama */
.stButton > button {
    background-color: #243D59 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 10px rgba(36, 61, 89, 0.12);
}

/* Hover tombol */
.stButton > button:hover {
    background-color: #18314B !important;
    color: white !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(36, 61, 89, 0.20);
}

/* Tombol saat diklik */
.stButton > button:active {
    transform: scale(0.97);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #C6C6C6;
}

/* Kotak menu sidebar */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.8rem;
}

/* Kartu / container */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
}

/* Gambar */
[data-testid="stImage"] img {
    border-radius: 14px;
}

/* Tampilan teks */
h1, h2, h3 {
    color: #243D59;
}

/* Hilangkan garis pemisah yang tidak perlu */
hr {
    border-color: #E5E7EB;
}

/* JUDUL UTAMA BERANDA */
.hero {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 38px;
    font-weight: bold;
    color: #243B55;
    line-height: 1.4;
    margin-bottom: 10px;
}

/* SUBJUDUL BERANDA */
.hero-subtitle {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 23px;
    font-weight: bold;
    color: #FFD76A;
    margin-bottom: 12px;
}

/* DESKRIPSI BERANDA */
.sub {
    font-size: 16px;
    color: #243B55;
    line-height: 1.7;
}

/* KOTAK GERBANG PENGETAHUAN */
.panel {
    background-color: #D6D6D6;
    padding: 30px;
    border-radius: 16px;
    color: #243B55;
    line-height: 1.9;
    box-shadow: 0 4px 12px rgba(36, 59, 85, 0.08);
}

/* JUDUL GERBANG PENGETAHUAN */
.panel h3 {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 29px;
    font-weight: bold;
    color: #243B55 !important;
    margin-top: 0;
    margin-bottom: 18px;
}

.sub {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 16px;
    color: #FFD76A !important;
    line-height: 1.7;
}

</style>
""", unsafe_allow_html=True)

def slug(teks):
    return re.sub(r"[^a-z0-9]+", "_", teks.lower()).strip("_")


def gambar(nama_file, tinggi=140, teks=""):
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = os.path.join(IMG_DIR, f"{nama_file}.{ext}")

        if os.path.exists(p):
            st.image(p, use_container_width=True)
            return

    st.warning(f"Gambar tidak ditemukan: {nama_file}")


# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    logo_path = next(
        (os.path.join(IMG_DIR, f"logo.{e}") for e in ("png", "jpg", "jpeg")
         if os.path.exists(os.path.join(IMG_DIR, f"logo.{e}"))),
        None,
    )
    if logo_path:
        st.image(logo_path, width=450)
    else:
        st.markdown('<div class="logo">AXIOMA</div>', unsafe_allow_html=True)

    option_menu(
        "Menu",
        MENU,
        icons=MENU_ICONS,
        menu_icon="list",
        manual_select=st.session_state.menu_index,
        key="menu_axioma",
        on_change=on_menu_change,
        styles={
            "container": {"background-color": NAVY, "padding": "8px"},
            "menu-title": {"color": "white", "font-size": "18px"},
            "icon": {"color": "white", "font-size": "16px"},
            "nav-link": {"color": "white", "font-size": "15px", "text-align": "left"},
            "nav-link-selected": {"background-color": "#0f4c9c"},
        },
    )

    st.write("")
    if st.button("Keluar"):
        st.session_state.login = False
        st.rerun()

halaman = MENU[st.session_state.menu_index]


# ----------------------------------------------------------------------------
# DAFTAR BUKU (dipakai Jenis, Kategori, Penulis)
# ----------------------------------------------------------------------------
def daftar_buku(judul_halaman, filter_fn, back_page, back_label, subjudul=""):
    st.button(f"< {back_label}", on_click=nav, args=(back_page,), key="back")
    st.title(judul_halaman)
    if subjudul:
        st.caption(subjudul)
    hasil = [b for b in st.session_state.buku if filter_fn(b)]
    q = st.text_input("Cari judul / penulis", key=f"cari_{judul_halaman}")
    if q:
        hasil = [b for b in hasil if q.lower() in (b["judul"] + b["penulis"]).lower()]
    st.write(f"**{len(hasil)}** buku ditemukan")
    if not hasil:
        st.info("Belum ada buku pada bagian ini.")
    for b in hasil:
        c1, c2, c3 = st.columns([6, 2, 2])
        with c1:
            st.markdown(
                f"<div class='bookcard'><b>{b['judul']}</b><br>"
                f"Penulis: {b['penulis']} &nbsp;|&nbsp; {b['jenis']} &nbsp;|&nbsp; "
                f"{b['kategori']} &nbsp;|&nbsp; {b['tahun']}</div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.write("")
            if b["stok"] > 0:
                st.success(f"Stok: {b['stok']}")
            else:
                st.error("Stok habis")
        with c3:
            st.write("")
            st.button(
                "Pinjam",
                key=f"pinjam_{judul_halaman}_{b['id']}",
                disabled=b["stok"] == 0,
                on_click=nav,
                args=("Arsip Perpustakaan", "pinjam", b["id"]),
            )


# ----------------------------------------------------------------------------
# HALAMAN
# ----------------------------------------------------------------------------
def page_beranda():
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(
            "<div class='hero'>Buka Buku<br>Buka Ilmu dan Pemikiran</div>"
            "<p class='sub'>Temukan berbagai koleksi buku dan wawasanmu bersama AXIOMA</p>",
            unsafe_allow_html=True,
        )
        st.button("Jelajahi Jenis Buku", on_click=nav, args=("Jenis Buku",), key="cta1")
    with c2:
        gambar("perpus", 265, "Letakkan gambar beranda_1 di folder gambar")
    st.write("")
    c1, c2 = st.columns([2, 3])
    with c1:
        gambar("perpus1", 205, "Letakkan gambar beranda_2 di folder gambar")
    with c2:
        st.markdown(
            """<div class='panel'><h3>Gerbang Pengetahuan Tanpa Batas</h3>
Selamat datang di Perpustakaan Axioma, ruang literasi modern yang dirancang untuk menemukan rasa ingin tahu Anda di era digital.
Terinspirasi dari kata "<i>axioma</i>" yang berarti kebenaran dasar yang tak terbantahkan, kami hadir sebagai fondasi utama bagi siapa saja yang ingin memperluas wawasan, mengasah kreativitas, dan menemukan ide-ide baru.<br><br>
Di Axioma, kami percaya bahwa akses terhadap informasi berkualitas adalah hak setiap individu. Melalui platform berbasis web yang cepat dan ramah pengguna,
kami menghubungkan pembaca dengan ribuan koleksi literatur pilihan.</div>""",
            unsafe_allow_html=True,
        )
    st.write("")
    aktif = sum(1 for r in st.session_state.pinjaman if not r["tgl_kembali"])
    m1, m2, m3 = st.columns(3)
    m1.metric("Judul buku", len(st.session_state.buku))
    m2.metric("Sedang dipinjam", aktif)
    m3.metric("Anggota peminjam", len({r["nama"] for r in st.session_state.pinjaman}))





def page_panduan():
    st.markdown("""
    <style>
    .guide-header {
        background: linear-gradient(135deg, #243B55, #355B7D);
        padding: 35px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
        border-bottom: 8px solid #F5D36B;
    }

    .guide-header h1 {
        color: white !important;
        font-size: 35px;
        margin-bottom: 10px;
    }

    .guide-header p {
        color: #F5D36B;
        font-size: 16px;
        margin-bottom: 0;
    }

    .guide-card {
        background: #FFFFFF;
        border: 1px solid #E0E5EC;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(36,59,85,0.06);
        min-height: 230px;
    }

    .guide-card h3 {
        color: #243B55 !important;
        font-size: 22px;
        margin-bottom: 15px;
    }

    .guide-card p {
        color: #555;
        line-height: 1.8;
        font-size: 15px;
    }

    .guide-card li {
        color: #444;
        line-height: 2;
        font-size: 15px;
    }

    .guide-rule {
        background: #243B55;
        padding: 22px;
        border-radius: 14px;
        margin-bottom: 15px;
        border-left: 5px solid #F5D36B;
    }

    .guide-rule h4 {
        color: #F5D36B !important;
        margin-top: 0;
    }

    .guide-rule p {
        color: white;
        line-height: 1.8;
        margin-bottom: 0;
    }

    .guide-highlight {
        background: #ffffff;
        border-radius: 19px;
        padding: 25px;
        text-align: center;
        border: 1px solid #F5D36B;
        margin-top: 10px;
    }

    .guide-highlight h3 {
        color: #243B55 !important;
    }

    .guide-highlight p {
        color: #243B55;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="guide-header">
        <h1>Panduan Perpustakaan AXIOMA</h1>
        <p>Kenali tata cara dan aturan layanan perpustakaan
        untuk pengalaman membaca yang lebih nyaman.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="guide-card">
            <h3>Tata Cara Peminjaman</h3>
            <ol>
                <li>Pilih buku yang ingin dipinjam.</li>
                <li>Isi nama anggota perpustakaan.</li>
                <li>Tentukan lama peminjaman.</li>
                <li>Simpan transaksi peminjaman.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="guide-card">
            <h3>Tata Cara Pengembalian</h3>
            <ol>
                <li>Buka menu Arsip Perpustakaan.</li>
                <li>Pilih Pengembalian Buku.</li>
                <li>Cari transaksi buku yang ingin dikembalikan.</li>
                <li>Klik tombol Kembalikan.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Aturan Perpustakaan")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="guide-rule">
            <h4>Ketentuan Peminjaman</h4>
            <p>
            Buku dapat dipinjam sesuai pilihan durasi yang tersedia.
            Anggota wajib menjaga buku dengan baik dan mengembalikannya
            sesuai batas waktu yang telah ditentukan.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="guide-rule">
            <h4>Ketentuan Keterlambatan</h4>
            <p>
            Buku yang dikembalikan melewati batas waktu akan dikenakan
            denda. Pastikan buku dikembalikan tepat waktu.
            </p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="guide-highlight">
            <h3>14 Hari</h3>
            <p>Lama peminjaman standar</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="guide-highlight">
            <h3>Rp1.500 / Hari</h3>
            <p>Denda keterlambatan per buku</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="guide-card" style="text-align:center; min-height:0;">
        <h3>Jelajahi Koleksi AXIOMA</h3>
        <p>
        Temukan buku favoritmu melalui menu Jenis Buku dan Kategori Buku.
        Gunakan fitur pencarian untuk mempermudah menemukan koleksi
        yang kamu inginkan.
        </p>
    </div>
    """, unsafe_allow_html=True)


def page_jenis():
    d = st.session_state.detail
    if d:
        daftar_buku(
            f"Jenis: {d}", lambda b: b["jenis"] == d, "Jenis Buku",
            "Kembali ke Jenis Buku", f"Semua koleksi {d}",
        )
        return
    st.title("Jenis Buku")
    st.caption("Pilih jenis buku untuk melihat seluruh koleksinya.")
    for row in range(0, len(JENIS), 3):
        cols = st.columns(3)
        for col, nama in zip(cols, JENIS[row : row + 3]):
            jml = sum(1 for b in st.session_state.buku if b["jenis"] == nama)
            with col:
                gambar(slug(nama), 150, nama)
                st.button(
                    f"{nama} ({jml})", key=f"jenis_{nama}", on_click=nav,
                    args=("Jenis Buku", nama), use_container_width=True, type="primary",
                )
        st.write("")


def page_kategori():
    d = st.session_state.detail
    if d:
        tipe, nama = d
        if tipe == "kategori":
            daftar_buku(
                f"Kategori: {nama}", lambda b: b["kategori"] == nama, "Kategori Buku",
                "Kembali ke Kategori Buku", f"Semua buku kategori {nama}",
            )
        else:
            daftar_buku(
                f"Penulis: {nama}", lambda b: b["penulis"] == nama, "Kategori Buku",
                "Kembali ke Kategori Buku", f"Semua buku karya {nama}",
            )
        return
    st.title("Kategori Buku")
    st.caption("Jelajahi koleksi berdasarkan bidang dan tema")
    for row in range(0, len(KATEGORI), 4):
        cols = st.columns(4)
        for col, nama in zip(cols, KATEGORI[row : row + 4]):
            jml = sum(1 for b in st.session_state.buku if b["kategori"] == nama)
            with col:
                gambar(slug(nama), 110, nama)
                st.button(
                    f"{nama} ({jml})", key=f"kat_{nama}", on_click=nav,
                    args=("Kategori Buku", ("kategori", nama)),
                    use_container_width=True, type="primary",
                )
        st.write("")
    st.subheader("Penulis")
    cols = st.columns(4)
    for col, nama in zip(cols, PENULIS):
        jml = sum(1 for b in st.session_state.buku if b["penulis"] == nama)
        with col:
            gambar(slug(nama), 130, nama)
            st.button(
                f"{nama} ({jml})", key=f"pen_{nama}", on_click=nav,
                args=("Kategori Buku", ("penulis", nama)),
                use_container_width=True, type="primary",
            )


def page_arsip():
    d = st.session_state.detail
    pinjaman = st.session_state.pinjaman

    if d:
        st.button("< Kembali ke Arsip Perpustakaan", on_click=nav, args=("Arsip Perpustakaan",), key="back_arsip")

    if d == "pinjam":
        st.title("Peminjaman Buku")
        st.caption("Catat peminjaman buku oleh anggota perpustakaan.")
        tersedia = [b for b in st.session_state.buku if b["stok"] > 0]
        opsi = {f"{b['judul']} - {b['penulis']} (stok {b['stok']})": b["id"] for b in tersedia}
        labels = list(opsi.keys())
        idx = 0
        if st.session_state.pinjam_id:
            for i, lab in enumerate(labels):
                if opsi[lab] == st.session_state.pinjam_id:
                    idx = i
        with st.form("form_pinjam", clear_on_submit=True):
            nama = st.text_input("Nama anggota")
            pilih = st.selectbox("Judul buku", labels, index=idx)
            lama = st.selectbox("Lama pinjam (hari)", [7, 14, 21], index=1)
            kirim = st.form_submit_button("Simpan Peminjaman")
        if kirim:
            if not nama.strip():
                st.error("Nama anggota wajib diisi.")
            else:
                b = get_buku(opsi[pilih])
                b["stok"] -= 1
                today = dt.date.today()
                pinjaman.append(
                    dict(nama=nama.strip(), buku_id=b["id"], tgl_pinjam=today,
                         batas=today + dt.timedelta(days=lama), tgl_kembali=None)
                )
                st.session_state.pinjam_id = None
                st.success(
                    f"'{b['judul']}' dipinjam oleh {nama.strip()}. "
                    f"Batas kembali: {fmt(today + dt.timedelta(days=lama))}."
                )
        return

    if d == "kembali":
        st.title("Pengembalian Buku")
        st.caption("Proses buku yang telah dipinjam.")
        aktif = [(i, r) for i, r in enumerate(pinjaman) if not r["tgl_kembali"]]
        if not aktif:
            st.info("Tidak ada buku yang sedang dipinjam.")
        for i, r in aktif:
            b = get_buku(r["buku_id"])
            h = hari_telat(r)
            c1, c2, c3 = st.columns([5, 3, 2])
            with c1:
                st.markdown(
                    f"<div class='bookcard'><b>{b['judul']}</b><br>"
                    f"Peminjam: {r['nama']} | batas {fmt(r['batas'])}</div>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.write("")
                if h:
                    st.error(f"Terlambat {h} hari | Denda {rupiah(h * DENDA_PER_HARI)}")
                else:
                    st.success("Tepat waktu")
            with c3:
                st.write("")
                if st.button("Kembalikan", key=f"kembali_{i}"):
                    r["tgl_kembali"] = dt.date.today()
                    b["stok"] += 1
                    st.rerun()
        return

    if d == "riwayat":
        st.title("Riwayat Transaksi")
        st.caption("Lihat riwayat peminjaman dan pengembalian buku.")
        f = st.selectbox("Filter status", ["Semua", "Dipinjam", "Terlambat", "Dikembalikan"])
        q = st.text_input("Cari nama anggota / judul buku")
        df = loans_df(pinjaman)
        if f != "Semua":
            df = df[df["Status"] == f]
        if q:
            df = df[df["Nama Anggota"].str.contains(q, case=False) | df["Judul Buku"].str.contains(q, case=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Unduh CSV", df.to_csv(index=False).encode("utf-8"), "riwayat_transaksi.csv", "text/csv")
        return

    if d == "terlambat":
        st.title("Keterlambatan")
        st.caption("Daftar anggota yang terlambat mengembalikan buku.")
        telat = [r for r in pinjaman if status(r) == "Terlambat"]
        if not telat:
            st.success("Tidak ada keterlambatan.")
        else:
            df = loans_df(telat)
            df["Hari Telat"] = [hari_telat(r) for r in telat]
            st.dataframe(df, use_container_width=True, hide_index=True)
            total = sum(hari_telat(r) * DENDA_PER_HARI for r in telat)
            st.metric("Total denda berjalan", rupiah(total))
        return

    # ---- halaman utama arsip
    st.title("Arsip Perpustakaan")
    st.caption("Kelola aktivitas peminjaman dan pengembalian koleksi perpustakaan.")
    cards = [
        ("Peminjaman Buku", "Catat peminjaman buku oleh anggota perpustakaan.", "pinjam"),
        ("Pengembalian Buku", "Proses buku yang telah dipinjam.", "kembali"),
        ("Riwayat Transaksi", "Lihat riwayat peminjaman dan pengembalian buku.", "riwayat"),
        ("Keterlambatan", "Daftar anggota yang terlambat mengembalikan buku.", "terlambat"),
    ]
    for row in range(0, 4, 2):
        cols = st.columns(2)
        for col, (judul, desk, key) in zip(cols, cards[row : row + 2]):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{judul}**")
                    st.caption(desk)
                    st.button("Buka", key=f"arsipcard_{key}", on_click=nav, args=("Arsip Perpustakaan", key))
    st.write("")
    
    h1, h2 = st.columns([5, 1])
    h1.subheader("Aktivitas Terbaru")
    h2.button(
        "Lihat Semua",
        on_click=nav,
        args=("Arsip Perpustakaan", "riwayat"),
        key="lihat_semua"
    )

    terbaru_index = sorted(
        enumerate(pinjaman),
        key=lambda x: x[1]["tgl_pinjam"],
        reverse=True
    )[:5]

    terbaru = [r for i, r in terbaru_index]

    df = loans_df(terbaru)[[
        "No", "Nama Anggota", "Judul Buku",
        "Tanggal Pinjam", "Batas Pengembalian", "Status"
    ]]

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    st.markdown("## Kelola Transaksi")

    if pinjaman:
        opsi_transaksi = {
            f"{r['nama']} - {get_buku(r['buku_id'])['judul']} ({fmt(r['tgl_pinjam'])})": i
            for i, r in enumerate(pinjaman)
        }

        pilihan = st.selectbox(
            "Pilih transaksi yang ingin dikelola",
            list(opsi_transaksi.keys()),
            key="kelola_transaksi"
        )

        index_data = opsi_transaksi[pilihan]
        rec = pinjaman[index_data]
        buku_lama = get_buku(rec["buku_id"])

        st.markdown("### Edit Data Transaksi")

        opsi_buku = {
            f"{b['judul']} - {b['penulis']} (stok {b['stok']})": b["id"]
            for b in st.session_state.buku
        }

        labels_buku = list(opsi_buku.keys())

        idx_buku = next(
            i for i, label in enumerate(labels_buku)
            if opsi_buku[label] == rec["buku_id"]
        )

        with st.form("form_edit_transaksi"):
            nama_edit = st.text_input(
                "Nama anggota",
                value=rec["nama"]
            )

            buku_edit = st.selectbox(
                "Judul buku",
                labels_buku,
                index=idx_buku
            )

            tanggal_pinjam_edit = st.date_input(
                "Tanggal pinjam",
                value=rec["tgl_pinjam"]
            )

            batas_edit = st.date_input(
                "Batas pengembalian",
                value=rec["batas"]
            )

            simpan_edit = st.form_submit_button("Simpan Perubahan")

        if simpan_edit:
            id_buku_baru = opsi_buku[buku_edit]
            buku_baru = get_buku(id_buku_baru)

            if not nama_edit.strip():
                st.error("Nama anggota tidak boleh kosong.")

            elif batas_edit < tanggal_pinjam_edit:
                st.error("Batas pengembalian tidak boleh sebelum tanggal pinjam.")

            elif (
                not rec["tgl_kembali"]
                and id_buku_baru != rec["buku_id"]
                and buku_baru["stok"] <= 0
            ):
                st.error("Stok buku yang dipilih sedang habis.")

            else:
                # Penyesuaian stok jika transaksi masih aktif
                if (
                    not rec["tgl_kembali"]
                    and id_buku_baru != rec["buku_id"]
                ):
                    buku_lama["stok"] += 1
                    buku_baru["stok"] -= 1

                rec["nama"] = nama_edit.strip()
                rec["buku_id"] = id_buku_baru
                rec["tgl_pinjam"] = tanggal_pinjam_edit
                rec["batas"] = batas_edit

                st.success("Data transaksi berhasil diperbarui!")
                st.rerun()

        st.markdown("---")
        st.markdown("### Hapus Transaksi")

        yakin_hapus = st.checkbox(
            "Saya yakin ingin menghapus transaksi yang dipilih",
            key="konfirmasi_hapus"
        )

        if st.button("Hapus Data", disabled=not yakin_hapus):
            # Kembalikan stok jika buku masih dipinjam
            if not rec["tgl_kembali"]:
                buku_lama["stok"] += 1

            pinjaman.pop(index_data)

            st.success("Data transaksi berhasil dihapus!")
            st.rerun()

    else:
        st.info("Belum ada data transaksi.")



# ----------------------------------------------------------------------------
# CHATBOT FAQ AXIOMA
# ----------------------------------------------------------------------------
def jawaban_faq(pertanyaan):
    """Memberikan jawaban otomatis berdasarkan kata kunci FAQ AXIOMA."""
    q = pertanyaan.lower().strip()

    # Data dinamis dari koleksi perpustakaan.
    total_buku = len(st.session_state.buku)
    total_stok = sum(b["stok"] for b in st.session_state.buku)
    jenis_tersedia = ", ".join(JENIS)
    kategori_tersedia = ", ".join(KATEGORI)

    if any(k in q for k in ["halo", "hai", "hello", "assalamualaikum", "selamat pagi", "selamat siang", "selamat malam"]):
        return (
            "Halo! Selamat datang di AXIOMA. 👋\n\n"
            "Saya asisten FAQ perpustakaan. Saya bisa membantu menjawab pertanyaan "
            "tentang koleksi, peminjaman, pengembalian, dan denda."
        )

    if any(k in q for k in ["pinjam", "peminjaman", "meminjam"]):
        return (
            "**Cara meminjam buku di AXIOMA:**\n\n"
            "1. Buka menu **Arsip Perpustakaan**.\n"
            "2. Pilih **Peminjaman Buku**.\n"
            "3. Isi nama anggota.\n"
            "4. Pilih judul buku yang tersedia.\n"
            "5. Pilih lama peminjaman: 7, 14, atau 21 hari.\n"
            "6. Klik **Simpan Peminjaman**.\n\n"
            "Pastikan stok buku masih tersedia sebelum meminjam."
        )

    if any(k in q for k in ["kembali", "pengembalian", "mengembalikan"]):
        return (
            "**Cara mengembalikan buku:**\n\n"
            "1. Buka menu **Arsip Perpustakaan**.\n"
            "2. Pilih **Pengembalian Buku**.\n"
            "3. Temukan transaksi peminjaman yang sesuai.\n"
            "4. Klik tombol **Kembalikan**.\n\n"
            "Setelah dikembalikan, stok buku akan bertambah kembali."
        )

    if any(k in q for k in ["denda", "terlambat", "telat"]):
        return (
            "Denda keterlambatan di AXIOMA adalah **Rp1.500 per hari untuk setiap buku**. "
            "Denda dihitung berdasarkan jumlah hari setelah batas pengembalian.\n\n"
            "Kamu bisa melihat daftar keterlambatan melalui menu "
            "**Arsip Perpustakaan → Keterlambatan**."
        )

    if any(k in q for k in ["berapa hari", "lama pinjam", "durasi", "jangka waktu"]):
        return (
            "Pilihan lama peminjaman buku di AXIOMA adalah **7 hari, 14 hari, atau 21 hari**. "
            "Batas pengembalian dihitung sejak tanggal peminjaman."
        )

    if any(k in q for k in ["jenis buku", "jenis koleksi", "macam buku"]):
        return (
            f"AXIOMA memiliki jenis koleksi berikut:\n\n"
            f"{jenis_tersedia}.\n\n"
            "Buka menu **Jenis Buku** untuk melihat koleksi berdasarkan jenisnya."
        )

    if any(k in q for k in ["kategori", "tema buku", "bidang buku"]):
        return (
            f"Kategori koleksi AXIOMA meliputi:\n\n"
            f"{kategori_tersedia}.\n\n"
            "Buka menu **Kategori Buku** untuk menjelajahi koleksi berdasarkan kategori."
        )

    if any(k in q for k in ["cari buku", "mencari buku", "judul buku", "stok", "tersedia", "koleksi", "jumlah buku"]):
        return (
            f"Saat ini terdapat **{total_buku} judul buku** dalam data koleksi AXIOMA "
            f"dengan total stok tercatat **{total_stok} eksemplar**.\n\n"
            "Untuk mencari judul atau penulis tertentu, buka menu **Jenis Buku** atau "
            "**Kategori Buku**, lalu gunakan kolom pencarian."
        )

    if any(k in q for k in ["riwayat", "transaksi", "arsip"]):
        return (
            "Untuk melihat catatan peminjaman dan pengembalian, buka "
            "**Arsip Perpustakaan → Riwayat Transaksi**. "
            "Kamu juga bisa memfilter status dan mengunduh data dalam format CSV."
        )

    if any(k in q for k in ["panduan", "aturan", "ketentuan", "cara menggunakan"]):
        return (
            "Kamu bisa membaca petunjuk lengkap melalui menu **Panduan**. "
            "Di sana tersedia tata cara peminjaman, pengembalian, ketentuan peminjaman, "
            "dan informasi denda keterlambatan."
        )

    if any(k in q for k in ["terima kasih", "makasih", "thanks"]):
        return "Sama-sama! Semoga AXIOMA membantu perjalanan literasimu. 📚"

    return (
        "Maaf, saya belum menemukan jawaban untuk pertanyaan itu.\n\n"
        "Coba tanyakan tentang **cara meminjam buku**, **pengembalian**, **denda**, "
        "**lama peminjaman**, **jenis buku**, **kategori buku**, atau **riwayat transaksi**."
    )


def page_chatbot():
    st.markdown("""
    <style>
    .chatbot-header {
        background: linear-gradient(135deg, #243B55, #355B7D);
        padding: 25px 28px;
        border-radius: 16px;
        border-bottom: 6px solid #FFD76A;
        margin-bottom: 18px;
        color: white;
    }
    .chatbot-header h2 {
        color: white !important;
        font-family: Georgia, "Times New Roman", serif;
        margin: 0 0 7px 0;
    }
    .chatbot-header p {
        color: #FFD76A;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="chatbot-header">
        <h2>Asisten Perpustakaan AXIOMA</h2>
        <p>Tanyakan apa saja seputar layanan dan koleksi perpustakaan.</p>
    </div>
    """, unsafe_allow_html=True)

    if "chat_axioma" not in st.session_state:
        st.session_state.chat_axioma = [
            {
                "role": "assistant",
                "content": (
                    "Halo! Selamat datang di AXIOMA. 👋\n\n"
                    "Ada yang bisa saya bantu? Kamu bisa bertanya tentang peminjaman, "
                    "pengembalian, denda, atau koleksi buku."
                )
            }
        ]

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Hapus chat", use_container_width=True):
            st.session_state.chat_axioma = [{
                "role": "assistant",
                "content": "Percakapan dibersihkan. Ada yang bisa saya bantu?"
            }]
            st.rerun()

    for pesan in st.session_state.chat_axioma:
        with st.chat_message(pesan["role"]):
            st.markdown(pesan["content"])

    pertanyaan = st.chat_input("Ketik pertanyaan tentang perpustakaan...")
    if pertanyaan:
        st.session_state.chat_axioma.append(
            {"role": "user", "content": pertanyaan}
        )
        jawaban = jawaban_faq(pertanyaan)
        st.session_state.chat_axioma.append(
            {"role": "assistant", "content": jawaban}
        )
        st.rerun()

    st.caption(
        "Catatan: Chatbot ini menggunakan FAQ berbasis kata kunci, "
        "bukan AI generatif. Jawaban tersedia untuk topik-topik FAQ AXIOMA."
    )


PAGES = {
    "Beranda": page_beranda,
    "Panduan": page_panduan,
    "Jenis Buku": page_jenis,
    "Kategori Buku": page_kategori,
    "Arsip Perpustakaan": page_arsip,
    "Chatbot": page_chatbot,
}
PAGES[halaman]()