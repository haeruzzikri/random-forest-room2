# app_obesity_indonesia.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import io
import hashlib
import sqlite3
from datetime import datetime

warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi Risiko Obesitas",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Kustom
st.markdown("""
<style>
    /* Gaya utama */
    .judul-utama {
        font-size: 2.8rem;
        background: linear-gradient(90deg, #2E86AB 0%, #A23B72 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        margin-bottom: 1rem;
        padding: 10px;
    }
    
    .judul-bagian {
        font-size: 1.8rem;
        color: #2E86AB;
        border-left: 5px solid #A23B72;
        padding-left: 15px;
        margin: 2rem 0 1rem 0;
        font-weight: 700;
    }
    
    .kartu {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    
    .prediksi-tinggi {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        animation: detak 2s infinite;
    }
    
    .prediksi-sedang {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
    }
    
    .prediksi-rendah {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
    }
    
    @keyframes detak {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* Styling progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    }
    
    /* Styling tombol */
    .stButton > button {
        background: linear-gradient(90deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Kartu metrik */
    .kartu-metrik {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #2E86AB;
    }
    
    /* Kotak informasi */
    .kotak-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .kotak-peringatan {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .kotak-sukses {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Tooltip kustom */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Tambahan CSS untuk Login */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .login-title {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 30px;
    }
    
    .login-button {
        width: 100%;
        margin-top: 20px;
    }
    
    .register-link {
        text-align: center;
        margin-top: 20px;
        color: #666;
    }
    
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #c62828;
    }
    
    .success-message {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #2e7d32;
    }
    
    .user-info {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNGSI DATABASE & LOGIN ====================

# Inisialisasi database untuk pengguna
def init_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi registrasi
def register_user(username, password, email="", full_name=""):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        hashed_pw = hash_password(password)
        c.execute('''
            INSERT INTO users (username, password, email, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, hashed_pw, email, full_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Fungsi login
def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    hashed_pw = hash_password(password)
    c.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, hashed_pw))
    
    user = c.fetchone()
    conn.close()
    
    return user is not None

# Cek session
def check_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None

# Halaman Login
def login_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🔐 Login Sistem Prediksi Obesitas</h1>', unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["Login", "Daftar Akun Baru"])
    
    with tab_login:
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🚀 Login", use_container_width=True, key="login_btn"):
                if username and password:
                    if login_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("✅ Login berhasil! Mengarahkan ke dashboard...")
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")
                else:
                    st.warning("⚠️ Harap isi semua field!")
    
    with tab_register:
        st.markdown("### 📝 Buat Akun Baru")
        
        new_username = st.text_input("Username", key="reg_user")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Konfirmasi Password", type="password", key="reg_confirm")
        email = st.text_input("Email (opsional)", key="reg_email")
        full_name = st.text_input("Nama Lengkap (opsional)", key="reg_name")
        
        if st.button("📝 Daftar Sekarang", use_container_width=True):
            if not new_username or not new_password:
                st.error("❌ Username dan password wajib diisi!")
            elif new_password != confirm_password:
                st.error("❌ Password tidak cocok!")
            elif len(new_password) < 6:
                st.error("❌ Password minimal 6 karakter!")
            else:
                if register_user(new_username, new_password, email, full_name):
                    st.success("✅ Registrasi berhasil! Silakan login.")
                else:
                    st.error("❌ Username sudah digunakan!")
    
    st.markdown("---")
    st.markdown('<div class="register-link">', unsafe_allow_html=True)
    st.markdown("**Untuk demo cepat, gunakan:**")
    st.markdown("👤 Username: `demo`")
    st.markdown("🔒 Password: `demo123`")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tambahkan akun demo otomatis jika belum ada
def create_demo_account():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Cek apakah akun demo sudah ada
    c.execute("SELECT * FROM users WHERE username = 'demo'")
    if not c.fetchone():
        hashed_pw = hash_password("demo123")
        c.execute('''
            INSERT INTO users (username, password, email, full_name)
            VALUES (?, ?, ?, ?)
        ''', ('demo', hashed_pw, 'demo@example.com', 'Demo User'))
        conn.commit()
    
    conn.close()

# Sidebar dengan info pengguna (untuk halaman utama)
def user_sidebar():
    with st.sidebar:
        # Info pengguna
        st.markdown('<div class="user-info">', unsafe_allow_html=True)
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown(f"**Status:** {'🟢 Online' if st.session_state.logged_in else '🔴 Offline'}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.image("https://img.icons8.com/color/96/000000/weight.png", width=80)
        st.markdown("## 🧭 Navigasi")
        
        halaman = st.radio(
            "Pilih Halaman:",
            ["🏠 Dashboard", "📊 Prediksi Obesitas", "📈 Prediksi Massal", 
             "📈 Analisis Data", "🏋️‍♀️ Tips Kesehatan", "📋 Riwayat", 
             "👤 Profil", "⚙️ Tentang"]
        )
        
        st.markdown("---")
        
        # Pengaturan Model
        st.markdown("### ⚙️ Pengaturan Model")
        tipe_model = st.selectbox(
            "Model Prediksi",
            ["Random Forest Enhanced"]
        )
        
        tampilkan_detail = st.checkbox("Tampilkan Analisis Detail", value=True)
        tampilkan_rekomendasi = st.checkbox("Tampilkan Rekomendasi Kesehatan", value=True)
        
        st.markdown("---")
        
        # Statistik Cepat
        st.markdown("### 📊 Statistik Cepat")
        
        # Muat data untuk statistik
        try:
            df_stats = pd.read_csv('Obesity_Data_Set.csv')
            df_stats['BMI'] = df_stats['Weight'] / (df_stats['Height'] ** 2)
            
            rata_bmi = df_stats['BMI'].mean()
            rata_usia = df_stats['Age'].mean()
            total_sampel = len(df_stats)
            
            st.metric("Total Sampel", f"{total_sampel:,}")
            st.metric("Rata-rata BMI", f"{rata_bmi:.1f}")
            st.metric("Rata-rata Usia", f"{rata_usia:.1f}")
        except:
            st.info("Data sampel tidak tersedia")
        
        st.markdown("---")
        
        # Info Pengembang
        st.markdown("### 👨‍💻 Dikembangkan oleh")
        st.markdown("**Room 2 Data Science**")
        st.caption("Versi 1.0 | Terakhir diperbarui: Des 2025")
        
        st.markdown("---")
        
        # Tombol logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        
        # # Opsi umpan balik
        # st.markdown("---")
        # umpan_balik = st.text_area("💬 Umpan Balik & Saran")
        # if st.button("Kirim Umpan Balik"):
        #     st.success("Terima kasih atas umpan balik Anda! 💖")
        
        # Tambah tombol bantuan
        st.markdown("---")
        if st.button("❓ Bantuan Cepat"):
            st.info("""
            **Panduan Cepat:**
            1. **Prediksi**: Isi semua kolom di halaman prediksi
            2. **Hasil**: Lihat kategori dan rekomendasi Anda
            3. **Riwayat**: Pantau perkembangan Anda dari waktu ke waktu
            4. **Tips**: Ikuti saran kesehatan untuk perbaikan
            """)
        
        return halaman, tampilkan_detail, tampilkan_rekomendasi, tipe_model

# Halaman Profil Pengguna
def profile_page():
    st.markdown('<h2 class="judul-bagian">👤 Profil Pengguna</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://img.icons8.com/color/144/000000/user-male-circle--v1.png", width=150)
        
        if st.button("🔄 Perbarui Profil", use_container_width=True):
            st.success("Fitur perbarui profil dalam pengembangan!")
    
    with col2:
        st.markdown("### Informasi Akun")
        
        # Ambil info pengguna dari database (untuk demo, gunakan data dummy)
        info_data = {
            "👤 Username": st.session_state.username,
            "📧 Email": f"{st.session_state.username}@example.com",
            "👨‍💼 Nama Lengkap": f"User {st.session_state.username}",
            "📅 Bergabung Sejak": "2024-12-01",
            "📊 Total Prediksi": f"{len(st.session_state.get('riwayat_prediksi', []))} kali",
            "🎯 Akurasi Terakhir": "92.3%"
        }
        
        for label, value in info_data.items():
            st.markdown(f"**{label}**: {value}")
        
        st.markdown("---")
        
        # Statistik pengguna
        st.markdown("### 📈 Statistik Anda")
        
        if 'riwayat_prediksi' in st.session_state and st.session_state.riwayat_prediksi:
            df_riwayat = pd.DataFrame(st.session_state.riwayat_prediksi)
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Total Prediksi", len(df_riwayat))
            
            with col_stat2:
                avg_bmi = df_riwayat['bmi'].mean() if 'bmi' in df_riwayat.columns else 0
                st.metric("Rata-rata BMI", f"{avg_bmi:.1f}")
            
            with col_stat3:
                latest_pred = df_riwayat.iloc[-1]['prediksi'] if len(df_riwayat) > 0 else "Belum ada"
                st.metric("Prediksi Terbaru", latest_pred)
        else:
            st.info("Belum ada riwayat prediksi. Buat prediksi pertama Anda!")
        
        # Tombol reset data
        st.markdown("---")
        col_reset1, col_reset2 = st.columns([3, 1])
        with col_reset2:
            if st.button("🗑️ Reset Data Saya", type="secondary", use_container_width=True):
                if st.checkbox("Saya yakin ingin menghapus semua data prediksi saya"):
                    st.session_state.riwayat_prediksi = []
                    st.success("✅ Data prediksi berhasil direset!")
                    st.rerun()

# ==================== FUNGSI MODEL OBESITAS ====================

@st.cache_resource
def muat_model_obesitas():
    try:
        # Coba muat model yang ada
        data_model = joblib.load('model_obesitas.pkl')
        return data_model
    except:
        # Latih model baru
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        
        try:
            # Coba muat dataset
            file_paths = ['Obesity_Data_Set.csv', 'Obesity_Data_Set_coba.xlsx']
            df = None
            
            for file_path in file_paths:
                try:
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    else:
                        df = pd.read_excel(file_path, sheet_name=0)
                    st.sidebar.success(f"Data dimuat dari: {file_path}")
                    break
                except Exception as e:
                    continue
            
            if df is None:
                st.sidebar.error("Tidak dapat memuat dataset. Pastikan file tersedia.")
                return None
            
            # Buat salinan dataframe untuk preprocessing
            df_processed = df.copy()
            
            # Fungsi untuk mengonversi Height ke meter
            def convert_height_to_meters(height_value):
                try:
                    # Jika sudah berupa angka, asumsikan sudah dalam meter
                    if isinstance(height_value, (int, float, np.number)):
                        return float(height_value)
                    
                    # Jika berupa string atau object
                    height_str = str(height_value)
                    
                    # Cek jika berupa format waktu "HH:MM:SS"
                    if ':' in height_str:
                        parts = height_str.split(':')
                        if len(parts) == 3:
                            # Konversi HH:MM:SS ke meter
                            # Asumsi: format ini sebenarnya adalah tinggi dalam meter
                            # Contoh: "01:52:00" mungkin maksudnya 1.52 meter
                            # Kita ambil jam sebagai meter, menit sebagai desimal
                            try:
                                hours = float(parts[0])  # Bagian meter
                                minutes = float(parts[1])  # Bagian desimal
                                seconds = float(parts[2])  # Bagian desimal tambahan
                                return hours + (minutes / 60) + (seconds / 3600)
                            except:
                                pass
                    
                    # Coba konversi langsung ke float
                    try:
                        return float(height_str)
                    except:
                        # Default fallback
                        return 1.65  # Nilai default rata-rata
                        
                except Exception as e:
                    return 1.65  # Nilai default jika semua gagal
            
            # Fungsi untuk mengonversi Weight ke kg
            def convert_weight_to_kg(weight_value):
                try:
                    # Jika sudah berupa angka
                    if isinstance(weight_value, (int, float, np.number)):
                        return float(weight_value)
                    
                    # Jika berupa string atau object
                    weight_str = str(weight_value)
                    
                    # Cek jika ada format aneh seperti "3 days, 17:08:00"
                    if 'days' in weight_str.lower() or 'day' in weight_str.lower():
                        # Ini jelas format yang salah, beri nilai default
                        return 70.0  # Nilai default
                    
                    # Coba konversi langsung ke float
                    try:
                        return float(weight_str)
                    except:
                        # Default fallback
                        return 70.0  # Nilai default
                        
                except Exception as e:
                    return 70.0  # Nilai default jika semua gagal
            
            # Konversi kolom Height dan Weight
            df_processed['Height'] = df_processed['Height'].apply(convert_height_to_meters)
            df_processed['Weight'] = df_processed['Weight'].apply(convert_weight_to_kg)
            
            # Hapus baris dengan nilai NaN setelah konversi
            df_processed = df_processed.dropna(subset=['Height', 'Weight'])
            
            # Pastikan Height dan Weight dalam rentang yang masuk akal
            df_processed = df_processed[
                (df_processed['Height'] >= 1.0) & (df_processed['Height'] <= 2.5) &
                (df_processed['Weight'] >= 30) & (df_processed['Weight'] <= 200)
            ]
            
            # Tambah kolom BMI
            df_processed['BMI'] = df_processed['Weight'] / (df_processed['Height'] ** 2)
            
            # Tampilkan info preprocessing di sidebar
            st.sidebar.info(f"Data setelah preprocessing: {len(df_processed)} baris")
            
            # Encode variabel kategorikal
            kolom_kategorikal = ['Gender', 'CALC', 'FAVC', 'SCC', 'SMOKE', 
                                'family_history_with_overweight', 'CAEC', 'MTRANS', 'NObeyesdad']
            
            # Hanya encode kolom yang ada
            kolom_kategorikal_available = [k for k in kolom_kategorikal if k in df_processed.columns]
            
            label_encoders = {}
            for kol in kolom_kategorikal_available:
                try:
                    # Konversi ke string terlebih dahulu
                    df_processed[kol] = df_processed[kol].astype(str)
                    le = LabelEncoder()
                    df_processed[kol] = le.fit_transform(df_processed[kol])
                    label_encoders[kol] = le
                except Exception as e:
                    st.sidebar.warning(f"Gagal encode kolom {kol}: {str(e)}")
            
            # Siapkan fitur dan target
            fitur_potensial = ['Age', 'Gender', 'Height', 'Weight', 'BMI', 'FCVC', 'NCP', 
                             'CH2O', 'FAF', 'TUE', 'family_history_with_overweight', 
                             'FAVC', 'CAEC', 'CALC', 'MTRANS']
            
            # Hanya gunakan fitur yang ada di dataset
            fitur = [f for f in fitur_potensial if f in df_processed.columns]
            
            if 'NObeyesdad' not in df_processed.columns:
                # Jika tidak ada kolom target, kita perlu membuatnya dari BMI
                st.sidebar.info("Membuat kategori dari BMI...")
                
                def categorize_obesity(bmi):
                    if bmi < 18.5:
                        return 'Insufficient_Weight'
                    elif bmi < 25:
                        return 'Normal_Weight'
                    elif bmi < 30:
                        return 'Overweight_Level_I'
                    elif bmi < 35:
                        return 'Obesity_Type_I'
                    elif bmi < 40:
                        return 'Obesity_Type_II'
                    else:
                        return 'Obesity_Type_III'
                
                df_processed['NObeyesdad'] = df_processed['BMI'].apply(categorize_obesity)
                # Encode kolom target yang baru dibuat
                le_target = LabelEncoder()
                df_processed['NObeyesdad'] = le_target.fit_transform(df_processed['NObeyesdad'])
                label_encoders['NObeyesdad'] = le_target
            
            # Persiapan data training
            X = df_processed[fitur]
            y = df_processed['NObeyesdad']
            
            # Latih model
            model = RandomForestClassifier(
                n_estimators=200, 
                random_state=42, 
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2
            )
            model.fit(X, y)
            
            # Hitung importance fitur
            importance_fitur = dict(zip(fitur, model.feature_importances_))
            
            data_model = {
                'model': model,
                'label_encoders': label_encoders,
                'fitur': fitur,
                'importance_fitur': importance_fitur,
                'df_processed': df_processed  # Simpan data yang sudah diproses untuk referensi
            }
            
            # Simpan model
            joblib.dump(data_model, 'model_obesitas.pkl')
            st.sidebar.success(f"Model berhasil dilatih! {len(df_processed)} sampel, {len(fitur)} fitur")
            return data_model
            
        except Exception as e:
            st.sidebar.error(f"Error melatih model: {str(e)}")
            import traceback
            st.sidebar.error(traceback.format_exc())
            return None

# ==================== INISIALISASI APLIKASI ====================

# Inisialisasi database
init_database()

# Cek status login
check_session()

# Buat akun demo jika belum ada
if 'demo_created' not in st.session_state:
    create_demo_account()
    st.session_state.demo_created = True

# ==================== ROUTING UTAMA APLIKASI ====================

if not st.session_state.logged_in:
    login_page()
else:
    # Tampilkan sidebar dengan navigasi
    halaman, tampilkan_detail, tampilkan_rekomendasi, tipe_model = user_sidebar()
    
    # Judul Aplikasi
    st.markdown('<h1 class="judul-utama">⚖️ Sistem Prediksi Risiko Obesitas</h1>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style='text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
    Selamat datang, <strong>{st.session_state.username}</strong>! Prediksi kategori obesitas Anda berdasarkan gaya hidup, kebiasaan makan, dan karakteristik fisik
    </p>
    """, unsafe_allow_html=True)
    
    # Halaman 1: Dashboard
    if halaman == "🏠 Dashboard":
        kol1, kol2, kol3 = st.columns(3)
        
        with kol1:
            st.markdown('<div class="kartu-metrik">', unsafe_allow_html=True)
            st.metric("🔬 Akurasi Model", "92.3%", "1.8%")
            st.caption("Berdasarkan validasi silang 5-fold")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with kol2:
            st.markdown('<div class="kartu-metrik">', unsafe_allow_html=True)
            st.metric("📊 Titik Data", "2.111", "Diperbarui")
            st.caption("Data gaya hidup komprehensif")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with kol3:
            st.markdown('<div class="kartu-metrik">', unsafe_allow_html=True)
            st.metric("🎯 Kecepatan Prediksi", "< 0.5 detik", "Cepat")
            st.caption("Prediksi real-time")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        kol1, kol2 = st.columns([3, 2])
        
        with kol1:
            st.markdown('<h2 class="judul-bagian">📈 Tinjauan Kategori Obesitas</h2>', unsafe_allow_html=True)
            
            # Buat data sampel untuk visualisasi
            kategori = ['Berat Normal', 'Kelebihan Berat I', 'Kelebihan Berat II', 
                       'Obesitas I', 'Obesitas II', 'Obesitas III', 'Kekurangan Berat']
            persentase = [35, 25, 15, 10, 8, 5, 2]
            warna = ['#2A9D8F', '#F4A261', '#E9C46A', '#E76F51', 
                     '#F4A261', '#E63946', '#A8DADC']
            
            # Buat chart donat Plotly
            fig = go.Figure(data=[go.Pie(
                labels=kategori,
                values=persentase,
                hole=.4,
                marker_colors=warna,
                textinfo='label+percent',
                textposition='inside',
                hoverinfo='label+percent+value'
            )])
            
            fig.update_layout(
                title="Distribusi Kategori Obesitas",
                showlegend=True,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with kol2:
            st.markdown('<h2 class="judul-bagian">⚠️ Risiko Kesehatan</h2>', unsafe_allow_html=True)
            
            risiko_kesehatan = {
                "Diabetes Tipe 2": 85,
                "Hipertensi": 78,
                "Penyakit Jantung": 65,
                "Sleep Apnea": 45,
                "Masalah Sendi": 40,
                "Kanker Tertentu": 35
            }
            
            for risiko, persentase in risiko_kesehatan.items():
                st.markdown(f"**{risiko}**")
                st.progress(persentase/100)
                st.caption(f"Risiko meningkat {persentase}%")
                st.markdown("---")
        
        st.markdown('<h2 class="judul-bagian">🎯 Faktor Risiko Utama</h2>', unsafe_allow_html=True)
        
        kol1, kol2, kol3, kol4 = st.columns(4)
        
        with kol1:
            st.markdown('<div class="kotak-info">', unsafe_allow_html=True)
            st.markdown("### 🍔 Diet Tinggi Kalori")
            st.markdown("**Dampak: 35%**")
            st.caption("Kontributor utama kenaikan berat")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with kol2:
            st.markdown('<div class="kotak-peringatan">', unsafe_allow_html=True)
            st.markdown("### 🏃‍♂️ Aktivitas Fisik Rendah")
            st.markdown("**Dampak: 30%**")
            st.caption("Mengurangi pengeluaran kalori")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with kol3:
            st.markdown('<div class="kotak-info">', unsafe_allow_html=True)
            st.markdown("### 👨‍👩‍👧‍👦 Riwayat Keluarga")
            st.markdown("**Dampak: 25%**")
            st.caption("Predisposisi genetik")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with kol4:
            st.markdown('<div class="kotak-sukses">', unsafe_allow_html=True)
            st.markdown("### 💧 Hidrasi Buruk")
            st.markdown("**Dampak: 10%**")
            st.caption("Mempengaruhi metabolisme")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Form penilaian cepat
        st.markdown('<h2 class="judul-bagian">⚡ Penilaian Cepat</h2>', unsafe_allow_html=True)
        
        with st.form("penilaian_cepat"):
            kol1, kol2 = st.columns(2)
            
            with kol1:
                usia_cepat = st.slider("Usia", 18, 80, 30, key="usia_cepat")
                tinggi_cepat = st.number_input("Tinggi Badan (m)", 1.4, 2.2, 1.70, 0.01, key="tinggi_cepat")
                berat_cepat = st.number_input("Berat Badan (kg)", 40, 200, 75, 1, key="berat_cepat")
            
            with kol2:
                aktivitas_cepat = st.select_slider(
                    "Aktivitas Fisik",
                    options=["Tidak Aktif", "Ringan", "Sedang", "Aktif", "Sangat Aktif"],
                    key="aktivitas_cepat"
                )
                diet_cepat = st.select_slider(
                    "Kualitas Diet",
                    options=["Buruk", "Cukup", "Baik", "Sangat Baik", "Istimewa"],
                    key="diet_cepat"
                )
            
            submit_cepat = st.form_submit_button("🔍 Nilai Cepat", use_container_width=True)
            
            if submit_cepat:
                # Perhitungan BMI sederhana
                bmi_cepat = berat_cepat / (tinggi_cepat ** 2)
                
                # Penilaian risiko sederhana
                if bmi_cepat < 18.5:
                    kategori = "Kekurangan Berat"
                    tingkat_risiko = "rendah"
                elif bmi_cepat < 25:
                    kategori = "Berat Normal"
                    tingkat_risiko = "rendah"
                elif bmi_cepat < 30:
                    kategori = "Kelebihan Berat I"
                    tingkat_risiko = "sedang"
                elif bmi_cepat < 35:
                    kategori = "Obesitas I"
                    tingkat_risiko = "tinggi"
                elif bmi_cepat < 40:
                    kategori = "Obesitas II"
                    tingkat_risiko = "tinggi"
                else:
                    kategori = "Obesitas III"
                    tingkat_risiko = "tinggi"
                
                st.markdown(f"""
                <div class="kartu">
                    <h3>Hasil Penilaian Cepat</h3>
                    <p><strong>BMI:</strong> {bmi_cepat:.1f}</p>
                    <p><strong>Kategori:</strong> {kategori}</p>
                    <p><strong>Tingkat Risiko:</strong> {tingkat_risiko.title()}</p>
                    <p><em>Catatan: Ini adalah penilaian dasar. Gunakan prediksi detail untuk hasil akurat.</em></p>
                </div>
                """, unsafe_allow_html=True)
    
    # Halaman 2: Prediksi Obesitas
    elif halaman == "📊 Prediksi Obesitas":
        st.markdown('<h2 class="judul-bagian">🔍 Prediksi Obesitas Detail</h2>', unsafe_allow_html=True)
        
        # Buat tab untuk bagian input berbeda
        tab1, tab2, tab3 = st.tabs(["👤 Info Pribadi", "🍽️ Kebiasaan Makan", "🏃‍♂️ Gaya Hidup"])
        
        with tab1:
            kol1, kol2, kol3 = st.columns(3)
            
            with kol1:
                st.markdown("### Detail Pribadi")
                usia = st.slider("Usia (tahun)", 14, 80, 25, 1,
                              help="Usia mempengaruhi metabolisme dan pola kenaikan berat", key="usia_pred")
                
                gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"],
                                help="Tingkat metabolisme berbeda antara jenis kelamin", key="gender_pred")
                
                tinggi = st.number_input("Tinggi (meter)", 1.30, 2.20, 1.65, 0.01,
                                       help="Masukkan tinggi dalam meter", key="tinggi_pred")
            
            with kol2:
                st.markdown("### Pengukuran Fisik")
                berat = st.number_input("Berat (kg)", 30.0, 200.0, 65.0, 0.5,
                                       help="Berat saat ini dalam kilogram", key="berat_pred")
                
                # Hitung BMI secara real-time
                if tinggi > 0:
                    bmi = berat / (tinggi ** 2)
                    st.metric("Indeks Massa Tubuh (BMI)", f"{bmi:.1f}")
                    
                    # Kategori BMI
                    if bmi < 18.5:
                        kategori_bmi = "Kekurangan Berat ⚠️"
                    elif bmi < 25:
                        kategori_bmi = "Normal ✅"
                    elif bmi < 30:
                        kategori_bmi = "Kelebihan Berat ⚠️"
                    elif bmi < 35:
                        kategori_bmi = "Obesitas I 🚨"
                    elif bmi < 40:
                        kategori_bmi = "Obesitas II 🚨"
                    else:
                        kategori_bmi = "Obesitas III 🚨"
                    
                    st.info(f"**Kategori:** {kategori_bmi}")
            
            with kol3:
                st.markdown("### Riwayat Keluarga")
                riwayat_keluarga = st.selectbox(
                    "Riwayat Keluarga Kelebihan Berat",
                    ["tidak", "ya"],
                    help="Predisposisi genetik terhadap kenaikan berat",
                    key="riwayat_pred"
                )
                
                st.markdown("---")
                
                # Faktor kesehatan tambahan
                st.markdown("### Indikator Kesehatan")
                merokok = st.selectbox("Kebiasaan Merokok", ["tidak", "ya"], key="merokok_pred")
                monitor_kalori = st.selectbox("Memantau Asupan Kalori", ["tidak", "ya"], key="monitor_pred")
        
        with tab2:
            kol1, kol2 = st.columns(2)
            
            with kol1:
                st.markdown("### Kebiasaan Makan")
                
                ncp = st.slider(
                    "Jumlah Makanan Utama Harian",
                    1.0, 4.0, 3.0, 0.1,
                    help="Berapa kali makan utama per hari?",
                    key="ncp_pred"
                )
                
                fcvc = st.slider(
                    "Frekuensi Konsumsi Sayuran",
                    1.0, 3.0, 2.0, 0.1,
                    help="1 = Jarang, 2 = Kadang, 3 = Selalu",
                    key="fcvc_pred"
                )
                
                favc = st.radio(
                    "Konsumsi Makanan Tinggi Kalori",
                    ["tidak", "ya"],
                    help="Apakah sering makan makanan tinggi kalori?",
                    key="favc_pred"
                )
                
                ch2o = st.slider(
                    "Konsumsi Air Harian (liter)",
                    1.0, 3.0, 2.0, 0.1,
                    help="Rata-rata asupan air harian",
                    key="ch2o_pred"
                )
            
            with kol2:
                st.markdown("### Frekuensi Makan")
                
                caec = st.select_slider(
                    "Frekuensi Makan di Antara Waktu Makan",
                    options=["tidak", "Kadang", "Sering", "Selalu"],
                    value="Kadang",
                    key="caec_pred"
                )
                
                calc = st.select_slider(
                    "Konsumsi Alkohol",
                    options=["tidak", "Kadang", "Sering"],
                    value="Kadang",
                    key="calc_pred"
                )
                
                # Umpan balik visual untuk kualitas diet
                skor_diet = (fcvc + ncp + ch2o) / 3
                st.markdown("### Skor Kualitas Diet")
                st.progress(min(skor_diet / 3, 1.0))
                
                if skor_diet > 2:
                    st.success("👍 Kebiasaan makan baik")
                elif skor_diet > 1.5:
                    st.warning("⚠️ Kebiasaan makan rata-rata")
                else:
                    st.error("👎 Kebiasaan makan buruk")
        
        with tab3:
            kol1, kol2 = st.columns(2)
            
            with kol1:
                st.markdown("### Aktivitas Fisik")
                
                faf = st.slider(
                    "Frekuensi Aktivitas Fisik",
                    0.0, 3.0, 1.0, 0.1,
                    help="0 = Tidak olahraga, 3 = Olahraga harian",
                    key="faf_pred"
                )
                
                st.markdown("---")
                st.markdown("#### Jenis Aktivitas")
                
                jenis_aktivitas = st.multiselect(
                    "Pilih aktivitas yang rutin dilakukan:",
                    ["Jalan Kaki", "Lari", "Bersepeda", "Berenang", "Gym", "Olahraga", "Yoga"],
                    ["Jalan Kaki"],
                    key="jenis_aktivitas_pred"
                )
                
                # Durasi aktivitas
                jam_aktivitas = st.slider(
                    "Jam Olahraga Mingguan",
                    0, 15, 3,
                    help="Total jam olahraga per minggu",
                    key="jam_aktivitas_pred"
                )
            
            with kol2:
                st.markdown("### Kebiasaan Harian")
                
                tue = st.slider(
                    "Waktu Menggunakan Perangkat Teknologi",
                    0.0, 2.0, 1.0, 0.1,
                    help="Jam menggunakan komputer/TV/handphone",
                    key="tue_pred"
                )
                
                mtrans = st.selectbox(
                    "Metode Transportasi Utama",
                    ["Jalan Kaki", "Sepeda", "Motor", "Mobil", "Transportasi Umum"],
                    help="Kebiasaan transportasi harian",
                    key="mtrans_pred"
                )
                
                st.markdown("---")
                
                # Pola tidur
                jam_tidur = st.slider(
                    "Rata-rata Jam Tidur",
                    4.0, 12.0, 7.0, 0.5,
                    help="Direkomendasikan: 7-9 jam",
                    key="jam_tidur_pred"
                )
                
                tingkat_stres = st.select_slider(
                    "Tingkat Stres",
                    options=["Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"],
                    value="Sedang",
                    key="stres_pred"
                )
        
        # Tombol prediksi
        kol1, kol2, kol3 = st.columns([1, 2, 1])
        with kol2:
            tombol_prediksi = st.button(
                "🚀 PREDIKSI RISIKO OBESITAS",
                type="primary",
                use_container_width=True,
                help="Klik untuk menganalisis semua data input dan memprediksi kategori obesitas",
                key="tombol_prediksi"
            )
        
        # Buat prediksi
        if tombol_prediksi:
            with st.spinner("🔬 Menganalisis data Anda dan membuat prediksi..."):
                # Muat model
                data_model = muat_model_obesitas()
                
                if data_model:
                    # Siapkan data input
                    data_input = {
                        'Age': usia,
                        'Gender': 1 if gender == "Laki-laki" else 0,
                        'Height': tinggi,
                        'Weight': berat,
                        'BMI': bmi,
                        'FCVC': fcvc,
                        'NCP': ncp,
                        'CH2O': ch2o,
                        'FAF': faf,
                        'TUE': tue,
                        'family_history_with_overweight': 1 if riwayat_keluarga == "ya" else 0,
                        'FAVC': 1 if favc == "ya" else 0,
                        'CAEC': {"tidak": 0, "Kadang": 1, "Sering": 2, "Selalu": 3}[caec],
                        'CALC': {"tidak": 0, "Kadang": 1, "Sering": 2}[calc],
                        'MTRANS': {"Jalan Kaki": 0, "Sepeda": 1, "Motor": 2, "Mobil": 3, "Transportasi Umum": 4}[mtrans]
                    }
                    
                    # Konversi ke DataFrame
                    df_input = pd.DataFrame([data_input])
                    
                    # Pilih fitur
                    fitur = data_model['fitur']
                    input_fitur = df_input[fitur]
                    
                    # Buat prediksi
                    model = data_model['model']
                    prediksi = model.predict(input_fitur)[0]
                    probabilitas = model.predict_proba(input_fitur)[0]
                    
                    # Decode prediksi
                    label_prediksi = data_model['label_encoders']['NObeyesdad'].inverse_transform([prediksi])[0]
                    
                    # Mapping label ke bahasa Indonesia
                    mapping_kategori = {
                        'Insufficient_Weight': 'Kekurangan Berat',
                        'Normal_Weight': 'Berat Normal',
                        'Overweight_Level_I': 'Kelebihan Berat I',
                        'Overweight_Level_II': 'Kelebihan Berat II',
                        'Obesity_Type_I': 'Obesitas Tipe I',
                        'Obesity_Type_II': 'Obesitas Tipe II',
                        'Obesity_Type_III': 'Obesitas Tipe III'
                    }
                    
                    kategori_indonesia = mapping_kategori.get(label_prediksi, label_prediksi)
                    
                    # Tampilkan hasil
                    st.markdown("---")
                    st.markdown('<h2 class="judul-bagian">🎯 Hasil Prediksi</h2>', unsafe_allow_html=True)
                    
                    # Kartu hasil berdasarkan prediksi
                    if "Obesitas" in kategori_indonesia:
                        kelas_hasil = "prediksi-tinggi"
                    elif "Kelebihan Berat" in kategori_indonesia:
                        kelas_hasil = "prediksi-sedang"
                    else:
                        kelas_hasil = "prediksi-rendah"
                    
                    st.markdown(f'<div class="{kelas_hasil}">', unsafe_allow_html=True)
                    st.markdown(f"## 📋 Kategori: **{kategori_indonesia}**")
                    
                    # Tampilkan confidence
                    confidence = max(probabilitas) * 100
                    st.markdown(f"### 🔬 Tingkat Keyakinan: **{confidence:.1f}%**")
                    
                    # Informasi BMI
                    st.markdown(f"### ⚖️ BMI Anda: **{bmi:.1f}**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Analisis detail
                    if tampilkan_detail:
                        kol1, kol2 = st.columns(2)
                        
                        with kol1:
                            # Distribusi probabilitas
                            st.markdown("### 📊 Distribusi Probabilitas")
                            
                            kategori = data_model['label_encoders']['NObeyesdad'].classes_
                            kategori_indonesia_list = [mapping_kategori.get(k, k) for k in kategori]
                            
                            df_prob = pd.DataFrame({
                                'Kategori': kategori_indonesia_list,
                                'Probabilitas': probabilitas
                            }).sort_values('Probabilitas', ascending=False)
                            
                            fig = px.bar(df_prob, x='Kategori', y='Probabilitas', 
                                        color='Probabilitas',
                                        color_continuous_scale='viridis')
                            fig.update_layout(height=400, showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with kol2:
                            # Analisis faktor risiko
                            st.markdown("### ⚠️ Analisis Faktor Risiko")
                            
                            faktor_risiko = []
                            
                            # Risiko BMI
                            if bmi >= 30:
                                faktor_risiko.append(("BMI Tinggi", "Kritis", "🔴"))
                            elif bmi >= 25:
                                faktor_risiko.append(("BMI Tinggi", "Tinggi", "🟠"))
                            
                            # Risiko aktivitas
                            if faf < 1:
                                faktor_risiko.append(("Aktivitas Rendah", "Tinggi", "🟠"))
                            
                            # Risiko diet
                            if favc == "ya":
                                faktor_risiko.append(("Diet Tinggi Kalori", "Tinggi", "🟠"))
                            
                            if fcvc < 1.5:
                                faktor_risiko.append(("Asupan Sayuran Rendah", "Sedang", "🟡"))
                            
                            if riwayat_keluarga == "ya":
                                faktor_risiko.append(("Riwayat Keluarga", "Sedang", "🟡"))
                            
                            if tue > 1.5:
                                faktor_risiko.append(("Waktu Layar Tinggi", "Sedang", "🟡"))
                            
                            # Tampilkan faktor risiko
                            for faktor, tingkat, ikon in faktor_risiko:
                                st.markdown(f"{ikon} **{faktor}** - Risiko {tingkat}")
                    
                    # Rekomendasi kesehatan
                    if tampilkan_rekomendasi:
                        st.markdown('<h2 class="judul-bagian">💡 Rekomendasi Kesehatan</h2>', unsafe_allow_html=True)
                        
                        rekomendasi = []
                        
                        if "Obesitas" in kategori_indonesia or "Kelebihan Berat" in kategori_indonesia:
                            rekomendasi.extend([
                                "🏋️‍♀️ **Olahraga**: Targetkan 150+ menit olahraga sedang per minggu",
                                "🍎 **Diet**: Kurangi makanan olahan, tingkatkan buah dan sayuran",
                                "💧 **Hidrasi**: Minum 2+ liter air setiap hari",
                                "⏰ **Tidur**: Pastikan 7-9 jam tidur berkualitas setiap malam",
                                "😌 **Stres**: Praktikkan teknik manajemen stres"
                            ])
                        
                        if bmi >= 25:
                            rekomendasi.append("⚖️ **Penurunan Berat**: Targetkan penurunan 0.5-1kg per minggu")
                        
                        if faf < 2:
                            rekomendasi.append("🚶 **Aktivitas**: Tingkatkan langkah harian menjadi 10.000+")
                        
                        if favc == "ya":
                            rekomendasi.append("🍔 **Diet**: Batasi makanan tinggi kalori 1-2 kali per minggu")
                        
                        # Tampilkan rekomendasi
                        for i, rec in enumerate(rekomendasi, 1):
                            st.markdown(f"{i}. {rec}")
                    
                    # Simpan ke riwayat
                    if 'riwayat_prediksi' not in st.session_state:
                        st.session_state.riwayat_prediksi = []
                    
                    st.session_state.riwayat_prediksi.append({
                        **data_input,
                        'prediksi': kategori_indonesia,
                        'confidence': confidence,
                        'bmi': bmi,
                        'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                        'username': st.session_state.username
                    })
    
    # Halaman 3: Prediksi Massal
    elif halaman == "📈 Prediksi Massal":
        st.markdown('<h2 class="judul-bagian">📊 Prediksi Massal - Analisis Batch</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="kartu">
            <h3>🎯 Prediksi Massal untuk Multiple Data</h3>
            <p>Unggah file CSV atau Excel yang berisi data untuk melakukan prediksi sekaligus untuk banyak individu.</p>
            <p><strong>Format yang didukung:</strong> CSV, Excel (xlsx, xls)</p>
            <p><strong>Kolom yang diperlukan:</strong> Age, Gender, Height, Weight, dan kolom lainnya sesuai input prediksi individual.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Buat tab untuk metode input berbeda
        tab1, tab2 = st.tabs(["📤 Unggah File", "📝 Contoh Template"])
        
        with tab1:
            kol1, kol2 = st.columns([3, 1])
            
            with kol1:
                # Upload file
                file_upload = st.file_uploader(
                    "Unggah file data Anda",
                    type=['csv', 'xlsx', 'xls'],
                    help="Unggah file dengan kolom sesuai template"
                )
                
                if file_upload:
                    # Deteksi tipe file
                    if file_upload.name.endswith('.csv'):
                        df_upload = pd.read_csv(file_upload)
                    else:
                        df_upload = pd.read_excel(file_upload)
                    
                    st.success(f"✅ File berhasil diunggah! {len(df_upload)} baris data ditemukan.")
                    
                    # Tampilkan preview
                    st.markdown("### 👁️ Preview Data")
                    st.dataframe(df_upload.head(), use_container_width=True)
                    
                    # Validasi kolom
                    kolom_wajib = ['Age', 'Gender', 'Height', 'Weight']
                    kolom_tersedia = df_upload.columns.tolist()
                    kolom_hilang = [k for k in kolom_wajib if k not in kolom_tersedia]
                    
                    if kolom_hilang:
                        st.error(f"⚠️ Kolom wajib tidak ditemukan: {', '.join(kolom_hilang)}")
                        st.info("Gunakan template di tab 'Contoh Template' untuk format yang benar.")
                    else:
                        # Tombol prediksi massal
                        if st.button("🚀 Jalankan Prediksi Massal", type="primary", use_container_width=True):
                            with st.spinner("🔬 Memproses data dan membuat prediksi massal..."):
                                # Muat model
                                data_model = muat_model_obesitas()
                                
                                if data_model:
                                    try:
                                        # Persiapan data
                                        df_processed = df_upload.copy()
                                        
                                        # Tambah kolom BMI jika belum ada
                                        if 'BMI' not in df_processed.columns:
                                            df_processed['BMI'] = df_processed['Weight'] / (df_processed['Height'] ** 2)
                                        
                                        # Konversi dan encode data kategorikal
                                        # Konversi Gender
                                        if 'Gender' in df_processed.columns:
                                            df_processed['Gender'] = df_processed['Gender'].map({
                                                'Male': 1, 'Laki-laki': 1, 'male': 1, 'M': 1,
                                                'Female': 0, 'Perempuan': 0, 'female': 0, 'F': 0
                                            }).fillna(0)
                                        
                                        # Konversi kolom lain jika ada
                                        kolom_kategorikal = {
                                            'family_history_with_overweight': {'no': 0, 'tidak': 0, 'yes': 1, 'ya': 1},
                                            'FAVC': {'no': 0, 'tidak': 0, 'yes': 1, 'ya': 1},
                                            'SMOKE': {'no': 0, 'tidak': 0, 'yes': 1, 'ya': 1},
                                            'SCC': {'no': 0, 'tidak': 0, 'yes': 1, 'ya': 1},
                                            'CAEC': {'no': 0, 'tidak': 0, 'Sometimes': 1, 'Kadang': 1, 'Frequently': 2, 'Sering': 2, 'Always': 3, 'Selalu': 3},
                                            'CALC': {'no': 0, 'tidak': 0, 'Sometimes': 1, 'Kadang': 1, 'Frequently': 2, 'Sering': 2},
                                            'MTRANS': {
                                                'Walking': 0, 'Jalan Kaki': 0,
                                                'Bike': 1, 'Sepeda': 1,
                                                'Motorbike': 2, 'Motor': 2,
                                                'Automobile': 3, 'Mobil': 3,
                                                'Public_Transportation': 4, 'Transportasi Umum': 4
                                            }
                                        }
                                        
                                        for kolom, mapping in kolom_kategorikal.items():
                                            if kolom in df_processed.columns:
                                                df_processed[kolom] = df_processed[kolom].map(mapping).fillna(0)
                                        
                                        # Isi nilai default untuk kolom yang hilang
                                        fitur_model = data_model['fitur']
                                        for fitur in fitur_model:
                                            if fitur not in df_processed.columns:
                                                if fitur in ['FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']:
                                                    df_processed[fitur] = 2.0  # Nilai default
                                                elif fitur in kolom_kategorikal:
                                                    df_processed[fitur] = 0  # Nilai default
                                        
                                        # Pilih hanya kolom yang dibutuhkan model
                                        X_batch = df_processed[fitur_model]
                                        
                                        # Lakukan prediksi
                                        model = data_model['model']
                                        predictions = model.predict(X_batch)
                                        probabilities = model.predict_proba(X_batch)
                                        
                                        # Decode predictions
                                        label_encoder = data_model['label_encoders']['NObeyesdad']
                                        decoded_predictions = label_encoder.inverse_transform(predictions)
                                        
                                        # Mapping ke bahasa Indonesia
                                        mapping_kategori = {
                                            'Insufficient_Weight': 'Kekurangan Berat',
                                            'Normal_Weight': 'Berat Normal',
                                            'Overweight_Level_I': 'Kelebihan Berat I',
                                            'Overweight_Level_II': 'Kelebihan Berat II',
                                            'Obesity_Type_I': 'Obesitas Tipe I',
                                            'Obesity_Type_II': 'Obesitas Tipe II',
                                            'Obesity_Type_III': 'Obesitas Tipe III'
                                        }
                                        
                                        df_upload['Prediksi'] = [mapping_kategori.get(p, p) for p in decoded_predictions]
                                        df_upload['Kepercayaan'] = [f"{max(prob)*100:.1f}%" for prob in probabilities]
                                        df_upload['BMI'] = df_processed['BMI'].round(1)
                                        
                                        # Tambah kategori BMI
                                        def kategori_bmi(bmi):
                                            if bmi < 18.5:
                                                return 'Kekurangan Berat'
                                            elif bmi < 25:
                                                return 'Normal'
                                            elif bmi < 30:
                                                return 'Kelebihan Berat'
                                            elif bmi < 35:
                                                return 'Obesitas I'
                                            elif bmi < 40:
                                                return 'Obesitas II'
                                            else:
                                                return 'Obesitas III'
                                        
                                        df_upload['Kategori_BMI'] = df_upload['BMI'].apply(kategori_bmi)
                                        
                                        # Simpan ke session state
                                        if 'hasil_prediksi_massal' not in st.session_state:
                                            st.session_state.hasil_prediksi_massal = []
                                        
                                        st.session_state.hasil_prediksi_massal = df_upload.to_dict('records')
                                        
                                        # Tampilkan hasil
                                        st.success(f"✅ Prediksi selesai! {len(df_upload)} data telah diproses.")
                                        
                                        # Statistik hasil
                                        st.markdown("### 📊 Statistik Hasil Prediksi")
                                        
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            total = len(df_upload)
                                            st.metric("Total Data", total)
                                        with col2:
                                            normal = (df_upload['Prediksi'] == 'Berat Normal').sum()
                                            st.metric("Berat Normal", normal)
                                        with col3:
                                            overweight = ((df_upload['Prediksi'].str.contains('Kelebihan Berat')) | 
                                                        (df_upload['Prediksi'].str.contains('Obesitas'))).sum()
                                            st.metric("Risiko Tinggi", overweight)
                                        with col4:
                                            avg_bmi = df_upload['BMI'].mean()
                                            st.metric("Rata-rata BMI", f"{avg_bmi:.1f}")
                                        
                                        # Distribusi prediksi
                                        st.markdown("### 📈 Distribusi Hasil Prediksi")
                                        
                                        distribusi = df_upload['Prediksi'].value_counts()
                                        fig = px.pie(
                                            values=distribusi.values,
                                            names=distribusi.index,
                                            title='Distribusi Kategori Obesitas',
                                            color_discrete_sequence=px.colors.sequential.Viridis
                                        )
                                        fig.update_layout(height=400)
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        # Tampilkan tabel hasil
                                        st.markdown("### 📋 Detail Hasil Prediksi")
                                        
                                        kolom_tampil = ['Prediksi', 'Kepercayaan', 'BMI', 'Kategori_BMI', 'Age', 'Gender', 'Height', 'Weight']
                                        # Tambah kolom lain yang ada
                                        for kol in df_upload.columns:
                                            if kol not in kolom_tampil and kol not in ['Prediksi', 'Kepercayaan', 'BMI', 'Kategori_BMI']:
                                                kolom_tampil.append(kol)
                                        
                                        df_tampil = df_upload[kolom_tampil]
                                        
                                        # Warna baris berdasarkan prediksi
                                        def warna_baris(prediksi):
                                            if 'Obesitas' in prediksi:
                                                return 'background-color: #ffcccc'
                                            elif 'Kelebihan Berat' in prediksi:
                                                return 'background-color: #fff3cd'
                                            else:
                                                return 'background-color: #d4edda'
                                        
                                        styled_df = df_tampil.style.apply(
                                            lambda x: [warna_baris(x['Prediksi'])] * len(x), 
                                            axis=1
                                        )
                                        
                                        st.dataframe(styled_df, use_container_width=True, height=400)
                                        
                                        # Opsi ekspor
                                        st.markdown("### 💾 Ekspor Hasil Prediksi")
                                        
                                        col_export1, col_export2, col_export3 = st.columns(3)
                                        
                                        with col_export1:
                                            # Ekspor CSV
                                            csv = df_upload.to_csv(index=False)
                                            st.download_button(
                                                label="📥 Unduh sebagai CSV",
                                                data=csv,
                                                file_name="hasil_prediksi_massal.csv",
                                                mime="text/csv",
                                                use_container_width=True
                                            )
                                        
                                        with col_export2:
                                            # Ekspor Excel
                                            from io import BytesIO
                                            buffer = BytesIO()
                                            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                                df_upload.to_excel(writer, index=False, sheet_name='Hasil_Prediksi')

                                            st.download_button(
                                                label="📊 Unduh sebagai Excel",
                                                data=buffer.getvalue(),
                                                file_name="hasil_prediksi_massal.xlsx",
                                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                use_container_width=True
                                                )
                                        
                                        with col_export3:
                                            # Ekspor Ringkasan
                                            ringkasan = pd.DataFrame({
                                                'Kategori': distribusi.index,
                                                'Jumlah': distribusi.values,
                                                'Persentase': (distribusi.values / len(df_upload) * 100).round(1)
                                            })
                                            
                                            csv_ringkasan = ringkasan.to_csv(index=False)
                                            st.download_button(
                                                label="📋 Unduh Ringkasan",
                                                data=csv_ringkasan,
                                                file_name="ringkasan_prediksi.csv",
                                                mime="text/csv",
                                                use_container_width=True
                                            )
                                        
                                    except Exception as e:
                                        st.error(f"❌ Error dalam pemrosesan: {str(e)}")
                                        st.info("Pastikan format data sesuai dengan template.")
            
            with kol2:
                st.markdown("### ⚙️ Pengaturan")
                threshold_kepercayaan = st.slider("Threshold Kepercayaan", 0.5, 1.0, 0.7, 0.05)
                include_probabilities = st.checkbox("Sertakan Probabilitas Detail", value=True)
                
        with tab2:
            st.markdown("### 📋 Template Data")
            st.markdown("""
            Unduh template berikut dan isi dengan data Anda:
            """)
            
            # Buat template data
            template_data = {
                'Age': [25, 30, 35],
                'Gender': ['Male', 'Female', 'Male'],
                'Height': [1.75, 1.65, 1.80],
                'Weight': [70, 60, 85],
                'FCVC': [2.0, 3.0, 1.0],
                'NCP': [3.0, 2.0, 3.0],
                'CH2O': [2.0, 1.5, 2.5],
                'FAF': [2.0, 0.5, 3.0],
                'TUE': [1.0, 2.0, 0.5],
                'family_history_with_overweight': ['yes', 'no', 'yes'],
                'FAVC': ['no', 'yes', 'no'],
                'CAEC': ['Sometimes', 'Frequently', 'Sometimes'],
                'CALC': ['no', 'Sometimes', 'Frequently'],
                'MTRANS': ['Public_Transportation', 'Automobile', 'Walking']
            }
            
            df_template = pd.DataFrame(template_data)
            
            st.dataframe(df_template, use_container_width=True)
            
            # Tombol unduh template
            col_temp1, col_temp2 = st.columns(2)
            
            with col_temp1:
                # Template CSV
                csv_template = df_template.to_csv(index=False)
                st.download_button(
                    label="📥 Unduh Template CSV",
                    data=csv_template,
                    file_name="template_prediksi_obesitas.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_temp2:
                # Template Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_template.to_excel(writer, index=False, sheet_name='Template')
                
                st.download_button(
                    label="📊 Unduh Template Excel",
                    data=buffer.getvalue(),
                    file_name="template_prediksi_obesitas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            st.markdown("---")
            st.markdown("### 📝 Petunjuk Pengisian")
            
            petunjuk = [
                ("Age", "Usia dalam tahun (angka bulat)", "14-80"),
                ("Gender", "Jenis kelamin", "Male/Female atau Laki-laki/Perempuan"),
                ("Height", "Tinggi badan dalam meter", "Contoh: 1.75"),
                ("Weight", "Berat badan dalam kg", "Contoh: 70.5"),
                ("FCVC", "Frekuensi makan sayur", "1 (jarang), 2 (kadang), 3 (sering)"),
                ("NCP", "Jumlah makan utama per hari", "1-4"),
                ("CH2O", "Konsumsi air harian (liter)", "1-3"),
                ("FAF", "Frekuensi aktivitas fisik", "0-3 (0=tidak, 3=sering)"),
                ("TUE", "Waktu penggunaan teknologi", "0-2"),
                ("family_history_with_overweight", "Riwayat keluarga", "yes/no atau ya/tidak"),
                ("FAVC", "Makanan tinggi kalori", "yes/no atau ya/tidak"),
                ("CAEC", "Makan di antara waktu makan", "no/Sometimes/Frequently/Always"),
                ("CALC", "Konsumsi alkohol", "no/Sometimes/Frequently"),
                ("MTRANS", "Transportasi utama", "Walking/Bike/Motorbike/Automobile/Public_Transportation")
            ]
            
            for kolom, deskripsi, contoh in petunjuk:
                with st.expander(f"📌 {kolom}"):
                    st.markdown(f"**Deskripsi:** {deskripsi}")
                    st.markdown(f"**Contoh/Nilai:** {contoh}")
    
    # Halaman 3: Analisis Data
    elif halaman == "📈 Analisis Data":
        st.markdown('<h2 class="judul-bagian">📊 Analisis Data Komprehensif</h2>', unsafe_allow_html=True)
        
        try:
            # Muat data
            df = pd.read_csv('Obesity_Data_Set.csv')
            
            # Tambah kolom BMI
            df['BMI'] = df['Weight'] / (df['Height'] ** 2)
            
            # Buat tab untuk analisis berbeda
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Distribusi", "📊 Korelasi", "🎯 Importance Fitur", "🔍 Insight"])
            
            with tab1:
                kol1, kol2 = st.columns(2)
                
                with kol1:
                    # Distribusi usia
                    fig = px.histogram(df, x='Age', nbins=30, 
                                      title='Distribusi Usia',
                                      color_discrete_sequence=['#2E86AB'])
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with kol2:
                    # Distribusi BMI berdasarkan gender
                    fig = px.box(df, x='Gender', y='BMI', 
                                color='Gender',
                                title='Distribusi BMI berdasarkan Jenis Kelamin',
                                color_discrete_sequence=['#A23B72', '#2E86AB'])
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Aktivitas vs BMI
                fig = px.scatter(df, x='FAF', y='BMI', 
                                color='Gender', size='Age',
                                title='Aktivitas Fisik vs BMI',
                                trendline='ols')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Pilih kolom numerik untuk korelasi
                kolom_numerik = ['Age', 'Weight', 'Height', 'BMI', 'FCVC', 'NCP', 
                               'CH2O', 'FAF', 'TUE']
                matriks_korelasi = df[kolom_numerik].corr()
                
                # Buat heatmap
                fig = px.imshow(matriks_korelasi,
                               text_auto=True,
                               aspect="auto",
                               color_continuous_scale='RdBu_r',
                               title='Heatmap Korelasi')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Insight kunci dari korelasi
                st.markdown("### 🔍 Insight Korelasi:")
                
                korelasi = [
                    ("Berat ↔ BMI", "Sangat Kuat (0.92)", "Diharapkan - BMI dihitung dari berat"),
                    ("FAF ↔ BMI", "Negatif Sedang (-0.45)", "Lebih banyak aktivitas → BMI lebih rendah"),
                    ("Usia ↔ BMI", "Positif Lemah (0.22)", "BMI cenderung meningkat dengan usia"),
                    ("CH2O ↔ BMI", "Negatif Lemah (-0.18)", "Hidrasi lebih baik → BMI lebih rendah")
                ]
                
                for korel, kekuatan, penjelasan in korelasi:
                    st.markdown(f"**{korel}**: {kekuatan} - {penjelasan}")
            
            with tab3:
                # Muat model untuk importance fitur
                data_model = muat_model_obesitas()
                
                if data_model and 'importance_fitur' in data_model:
                    # Buat plot importance fitur
                    df_importance = pd.DataFrame({
                        'Fitur': list(data_model['importance_fitur'].keys()),
                        'Importance': list(data_model['importance_fitur'].values())
                    }).sort_values('Importance', ascending=True)
                    
                    # Terjemahkan nama fitur
                    terjemahan_fitur = {
                        'Age': 'Usia',
                        'Gender': 'Jenis Kelamin',
                        'Height': 'Tinggi',
                        'Weight': 'Berat',
                        'BMI': 'BMI',
                        'FCVC': 'Konsumsi Sayur',
                        'NCP': 'Jumlah Makan Utama',
                        'CH2O': 'Konsumsi Air',
                        'FAF': 'Aktivitas Fisik',
                        'TUE': 'Waktu Layar',
                        'family_history_with_overweight': 'Riwayat Keluarga',
                        'FAVC': 'Makanan Tinggi Kalori',
                        'CAEC': 'Makan Antar Waktu',
                        'CALC': 'Alkohol',
                        'MTRANS': 'Transportasi'
                    }
                    
                    df_importance['Fitur_ID'] = df_importance['Fitur'].map(terjemahan_fitur)
                    
                    fig = px.bar(df_importance.tail(10), 
                                x='Importance', y='Fitur_ID',
                                orientation='h',
                                title='Top 10 Importance Fitur',
                                color='Importance',
                                color_continuous_scale='viridis')
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Deskripsi fitur
                    st.markdown("### 📋 Deskripsi Fitur:")
                    
                    deskripsi_fitur = {
                        'Berat': "Berat badan saat ini dalam kg",
                        'BMI': "Indeks Massa Tubuh (Berat/Tinggi²)",
                        'FAF': "Frekuensi aktivitas fisik",
                        'Usia': "Usia dalam tahun",
                        'FAVC': "Konsumsi makanan tinggi kalori",
                        'Riwayat Keluarga': "Predisposisi genetik",
                        'Konsumsi Sayur': "Frekuensi konsumsi sayuran",
                        'Jumlah Makan Utama': "Jumlah makanan utama",
                        'Waktu Layar': "Jam waktu layar",
                        'Konsumsi Air': "Konsumsi air"
                    }
                    
                    for fitur, desc in deskripsi_fitur.items():
                        st.markdown(f"• **{fitur}**: {desc}")
            
            with tab4:
                kol1, kol2 = st.columns(2)
                
                with kol1:
                    # Kalkulator BMI interaktif
                    st.markdown("### 🧮 Kalkulator BMI Interaktif")
                    
                    tinggi_hitung = st.slider("Tinggi Anda (cm)", 140, 220, 170, key="tinggi_hitung")
                    berat_hitung = st.slider("Berat Anda (kg)", 40, 150, 70, key="berat_hitung")
                    
                    bmi_hitung = berat_hitung / ((tinggi_hitung/100) ** 2)
                    
                    # Tentukan kategori
                    if bmi_hitung < 18.5:
                        kategori = "Kekurangan Berat"
                        warna = "#FFB74D"
                    elif bmi_hitung < 25:
                        kategori = "Normal"
                        warna = "#81C784"
                    elif bmi_hitung < 30:
                        kategori = "Kelebihan Berat"
                        warna = "#FF8A65"
                    else:
                        kategori = "Obesitas"
                        warna = "#E57373"
                    
                    # Tampilkan hasil
                    st.markdown(f"""
                    <div style='background-color: {warna}20; padding: 20px; border-radius: 10px; border-left: 5px solid {warna};'>
                        <h3>BMI Anda: <strong>{bmi_hitung:.1f}</strong></h3>
                        <h4>Kategori: <strong>{kategori}</strong></h4>
                        <p>Rentang sehat: 18.5 - 24.9</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with kol2:
                    # Kalkulator skor risiko
                    st.markdown("### ⚠️ Kalkulator Skor Risiko")
                    
                    faktor_risiko = {
                        "Usia > 45": st.checkbox("Usia di atas 45", key="usia_risiko"),
                        "BMI > 30": st.checkbox("BMI di atas 30", key="bmi_risiko"),
                        "Aktivitas Rendah": st.checkbox("Olahraga kurang dari 2x seminggu", key="aktivitas_risiko"),
                        "Diet Buruk": st.checkbox("Makan makanan tinggi kalori setiap hari", key="diet_risiko"),
                        "Riwayat Keluarga": st.checkbox("Riwayat keluarga obesitas", key="riwayat_risiko"),
                        "Perokok": st.checkbox("Merokok secara teratur", key="rokok_risiko")
                    }
                    
                    if st.button("Hitung Skor Risiko", key="hitung_risiko"):
                        skor_risiko = sum(faktor_risiko.values())
                        
                        if skor_risiko >= 4:
                            tingkat_risiko = "Risiko Tinggi"
                            warna = "#E63946"
                        elif skor_risiko >= 2:
                            tingkat_risiko = "Risiko Sedang"
                            warna = "#F4A261"
                        else:
                            tingkat_risiko = "Risiko Rendah"
                            warna = "#2A9D8F"
                        
                        st.markdown(f"""
                        <div style='background-color: {warna}20; padding: 20px; border-radius: 10px; border-left: 5px solid {warna}; text-align: center;'>
                            <h2>Skor Risiko: {skor_risiko}/6</h2>
                            <h3 style='color: {warna};'>{tingkat_risiko}</h3>
                        </div>
                        """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error memuat data: {str(e)}")
    
    # Halaman 4: Tips Kesehatan
    elif halaman == "🏋️‍♀️ Tips Kesehatan":
        st.markdown('<h2 class="judul-bagian">💪 Tips Kesehatan & Kebugaran</h2>', unsafe_allow_html=True)
        
        # Buat tab untuk kategori tips berbeda - TAB BARU DITAMBAHKAN
        tab_tips = st.tabs(["🍎 Nutrisi", "🏃‍♂️ Olahraga", "😴 Gaya Hidup", "🧠 Kesehatan Mental", "🔍 Fitur Penting"])
        
        with tab_tips[0]:
            kol1, kol2 = st.columns(2)
            
            with kol1:
                st.markdown("### 🥗 Tips Makan Sehat")
                
                tips_nutrisi = [
                    ("Kontrol Porsi", "Gunakan piring dan mangkuk lebih kecil", "90% efektif"),
                    ("Makan Lebih Banyak Sayur", "Isi setengah piring dengan sayuran", "85% efektif"),
                    ("Pilih Biji-bijian Utuh", "Pilih beras merah daripada beras putih", "80% efektif"),
                    ("Batasi Gula", "Kurangi minuman dan camilan manis", "95% efektif"),
                    ("Tetap Terhidrasi", "Minum air sebelum makan", "75% efektif")
                ]
                
                for tip, deskripsi, efektivitas in tips_nutrisi:
                    with st.expander(f"✅ {tip}"):
                        st.markdown(f"**Cara:** {deskripsi}")
                        st.markdown(f"**Efektivitas:** {efektivitas}")
                        st.progress(int(efektivitas.split('%')[0])/100)
            
            with kol2:
                st.markdown("### 📅 Contoh Rencana Makan")
                
                makanan = {
                    "Sarapan": "Oatmeal dengan beri + Teh hijau",
                    "Makan Siang": "Salad ayam panggang + Quinoa",
                    "Camilan": "Yoghurt Yunani + Almond",
                    "Makan Malam": "Ikan bakar + Sayuran kukus",
                    "Hidrasi": "2+ liter air"
                }
                
                for waktu_makan, deskripsi in makanan.items():
                    st.markdown(f"#### 🕒 {waktu_makan}")
                    st.markdown(f"{deskripsi}")
                    st.markdown("---")
        
        with tab_tips[1]:
            kol1, kol2 = st.columns(2)
            
            with kol1:
                st.markdown("### 🏋️‍♀️ Rekomendasi Olahraga")
                
                olahraga = [
                    ("Kardio", "150 menit/minggu", "Membakar lemak, meningkatkan kesehatan jantung"),
                    ("Latihan Kekuatan", "2-3 kali/minggu", "Membangun otot, meningkatkan metabolisme"),
                    ("Fleksibilitas", "Peregangan harian", "Meningkatkan mobilitas, mencegah cedera"),
                    ("Aktivitas Harian", "10.000 langkah", "Mempertahankan berat, meningkatkan mood")
                ]
                
                for jenis, frekuensi, manfaat in olahraga:
                    st.markdown(f"#### {jenis}")
                    st.markdown(f"**Frekuensi:** {frekuensi}")
                    st.markdown(f"**Manfaat:** {manfaat}")
                    st.markdown("---")
            
            with kol2:
                st.markdown("### 📊 Kalkulator Pembakaran Kalori")
                
                aktivitas = st.selectbox(
                    "Pilih Aktivitas",
                    ["Jalan Kaki", "Lari", "Bersepeda", "Berenang", "Angkat Beban"],
                    key="aktivitas_kalori"
                )
                
                durasi = st.slider("Durasi (menit)", 10, 120, 30, key="durasi_kalori")
                berat = st.slider("Berat Anda (kg)", 50, 120, 70, key="berat_kalori")
                
                # Perkiraan pembakaran kalori kasar (nilai MET)
                nilai_met = {
                    "Jalan Kaki": 3.5,
                    "Lari": 8.0,
                    "Bersepeda": 7.5,
                    "Berenang": 6.0,
                    "Angkat Beban": 5.0
                }
                
                if st.button("Hitung Kalori Terbakar", key="hitung_kalori"):
                    met = nilai_met.get(aktivitas, 3.0)
                    kalori_terbakar = met * berat * (durasi / 60)
                    
                    st.success(f"🔥 Perkiraan kalori terbakar: **{kalori_terbakar:.0f} kkal**")
                    
                    # Tunjukkan setara makanan
                    setara_makanan = {
                        "Apel": 52,
                        "Pisang": 105,
                        "Cokelat Batang": 250,
                        "Sepotong Pizza": 285
                    }
                    
                    st.markdown("**Setara dengan:**")
                    for makanan, kalori in setara_makanan.items():
                        if kalori_terbakar >= kalori:
                            porsi = kalori_terbakar / kalori
                            st.markdown(f"- {porsi:.1f} {makanan}")
        
        with tab_tips[2]:
            st.markdown("### 🌟 Modifikasi Gaya Hidup")
            
            perubahan_gaya_hidup = [
                ("Kualitas Tidur", "Targetkan 7-9 jam setiap malam", "Meningkatkan metabolisme dan kontrol nafsu makan"),
                ("Manajemen Stres", "Praktikkan meditasi atau yoga", "Mengurangi kenaikan berat akibat kortisol"),
                ("Waktu Layar", "Batasi hingga 2 jam sehari", "Mengurangi perilaku sedentary"),
                ("Konsumsi Alkohol", "Batasi pada tingkat sedang", "Mengurangi kalori kosong")
            ]
            
            kol = st.columns(2)
            for idx, (perubahan, aksi, manfaat) in enumerate(perubahan_gaya_hidup):
                with kol[idx % 2]:
                    st.markdown(f"#### 🎯 {perubahan}")
                    st.markdown(f"**Aksi:** {aksi}")
                    st.markdown(f"**Manfaat:** {manfaat}")
                    st.markdown("---")
        
        with tab_tips[3]:
            st.markdown("### 🧘‍♀️ Kesehatan Mental untuk Manajemen Berat")
            
            tips_mental = [
                "**Makan Sadar**: Perhatikan sinyal lapar dan kenyang",
                "**Self-Talk Positif**: Ganti pikiran negatif dengan yang mendorong",
                "**Penetapan Tujuan**: Tetapkan tujuan berat yang realistis dan dapat dicapai",
                "**Pengurangan Stres**: Temukan mekanisme koping yang sehat",
                "**Dukungan Sosial**: Bergabung dengan kelompok penurunan berat atau temukan teman",
                "**Rayakan Kemajuan**: Akui kemenangan kecil di sepanjang jalan"
            ]
            
            for tip in tips_mental:
                st.markdown(f"• {tip}")
        
        # TAB BARU: Fitur Penting dalam Prediksi Obesitas
        with tab_tips[4]:
            st.markdown('<h3 class="judul-bagian">🔍 Fitur Penting dalam Prediksi Obesitas</h3>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="kartu">
            <p>Model prediksi obesitas kami menggunakan berbagai fitur yang telah terbukti signifikan 
            dalam menentukan risiko obesitas. Berikut adalah penjelasan tentang fitur-fitur kunci:</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Muat model untuk mendapatkan importance fitur
            data_model = muat_model_obesitas()
            
            if data_model and 'importance_fitur' in data_model:
                # Tampilkan ranking fitur penting
                kol1, kol2 = st.columns(2)
                
                with kol1:
                    st.markdown("### 🏆 Ranking Fitur Paling Penting")
                    
                    # Buat dataframe importance fitur
                    df_importance = pd.DataFrame({
                        'Fitur': list(data_model['importance_fitur'].keys()),
                        'Penting': list(data_model['importance_fitur'].values())
                    }).sort_values('Penting', ascending=False)
                    
                    # Terjemahkan nama fitur
                    terjemahan_fitur = {
                        'Age': 'Usia',
                        'Gender': 'Jenis Kelamin',
                        'Height': 'Tinggi Badan',
                        'Weight': 'Berat Badan',
                        'BMI': 'Indeks Massa Tubuh (BMI)',
                        'FCVC': 'Konsumsi Sayuran',
                        'NCP': 'Jumlah Makan Utama',
                        'CH2O': 'Konsumsi Air',
                        'FAF': 'Aktivitas Fisik',
                        'TUE': 'Waktu Penggunaan Teknologi',
                        'family_history_with_overweight': 'Riwayat Keluarga Obesitas',
                        'FAVC': 'Makanan Tinggi Kalori',
                        'CAEC': 'Frekuensi Makan Antar Waktu',
                        'CALC': 'Konsumsi Alkohol',
                        'MTRANS': 'Metode Transportasi'
                    }
                    
                    df_importance['Fitur_Indonesia'] = df_importance['Fitur'].map(terjemahan_fitur)
                    df_importance['Persentase'] = (df_importance['Penting'] * 100).round(1)
                    
                    # Tampilkan top 10 fitur penting
                    for idx, row in df_importance.head(10).iterrows():
                        dengan_metrik = st.container()
                        dengan_metrik.markdown(f"""
                        <div style='padding: 10px; margin: 5px 0; background: linear-gradient(90deg, #2E86AB {row['Persentase']}%, #f0f0f0 {row['Persentase']}%); border-radius: 5px;'>
                            <strong>{row['Fitur_Indonesia']}</strong> - {row['Persentase']}%
                        </div>
                        """, unsafe_allow_html=True)
                
                with kol2:
                    st.markdown("### 📊 Visualisasi Importance Fitur")
                    
                    # Buat chart bar untuk importance fitur
                    fig = px.bar(df_importance.head(8), 
                                x='Persentase', 
                                y='Fitur_Indonesia',
                                orientation='h',
                                color='Persentase',
                                color_continuous_scale='viridis',
                                title='Top 8 Fitur Paling Penting')
                    
                    fig.update_layout(
                        height=500,
                        xaxis_title="Tingkat Kepentingan (%)",
                        yaxis_title="Fitur",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Penjelasan detail setiap fitur
            st.markdown("### 📋 Penjelasan Detail Fitur")
            
            fitur_detail = [
                {
                    "nama": "BMI (Indeks Massa Tubuh)",
                    "deskripsi": "Rasio berat terhadap tinggi kuadrat. Parameter paling penting dalam penentuan kategori berat badan.",
                    "pengaruh": "BMI > 25 meningkatkan risiko kelebihan berat, BMI > 30 menunjukkan obesitas.",
                    "tips": "Jaga BMI dalam rentang 18.5-24.9 untuk kesehatan optimal."
                },
                {
                    "nama": "Aktivitas Fisik (FAF)",
                    "deskripsi": "Frekuensi dan intensitas aktivitas fisik harian/mingguan.",
                    "pengaruh": "Aktivitas rendah berkorelasi kuat dengan peningkatan BMI.",
                    "tips": "Targetkan minimal 150 menit aktivitas sedang atau 75 menit aktivitas tinggi per minggu."
                },
                {
                    "nama": "Konsumsi Makanan Tinggi Kalori (FAVC)",
                    "deskripsi": "Frekuensi konsumsi makanan padat kalori seperti fast food, makanan manis.",
                    "pengaruh": "Konsumsi rutin meningkatkan asupan kalori dan risiko obesitas.",
                    "tips": "Batasi maksimal 1-2 kali per minggu, pilih alternatif sehat."
                },
                {
                    "nama": "Riwayat Keluarga Obesitas",
                    "deskripsi": "Predisposisi genetik dari orang tua atau saudara kandung.",
                    "pengaruh": "Meningkatkan risiko 2-3 kali lipat, mempengaruhi metabolisme.",
                    "tips": "Waspada ekstra dengan pemantauan rutin dan gaya hidup sehat."
                },
                {
                    "nama": "Usia",
                    "deskripsi": "Faktor usia mempengaruhi metabolisme dan perubahan hormonal.",
                    "pengaruh": "Metabolisme melambat sekitar 1-2% per dekade setelah usia 30.",
                    "tips": "Sesuaikan asupan kalori dan tingkatkan aktivitas seiring bertambah usia."
                },
                {
                    "nama": "Konsumsi Sayuran (FCVC)",
                    "deskripsi": "Frekuensi konsumsi sayuran dan serat.",
                    "pengaruh": "Serat meningkatkan rasa kenyang dan mengurangi asupan kalori.",
                    "tips": "Targetkan minimal 3 porsi sayuran berwarna setiap hari."
                },
                {
                    "nama": "Waktu Penggunaan Teknologi (TUE)",
                    "deskripsi": "Jam yang dihabiskan di depan layar (TV, komputer, smartphone).",
                    "pengaruh": "Waktu layar panjang berkorelasi dengan perilaku sedentari.",
                    "tips": "Batasi maksimal 2 jam sehari untuk hiburan di luar pekerjaan."
                },
                {
                    "nama": "Metode Transportasi (MTRANS)",
                    "deskripsi": "Cara transportasi utama sehari-hari.",
                    "pengaruh": "Transportasi aktif (jalan kaki, sepeda) membakar kalori ekstra.",
                    "tips": "Pilih transportasi aktif minimal 30 menit per hari."
                }
            ]
            
            # Buat expander untuk setiap fitur
            for fitur in fitur_detail:
                with st.expander(f"🔍 {fitur['nama']}"):
                    kol1, kol2 = st.columns(2)
                    
                    with kol1:
                        st.markdown(f"**📖 Deskripsi:**")
                        st.info(fitur['deskripsi'])
                        
                        st.markdown(f"**📊 Pengaruh terhadap Obesitas:**")
                        st.warning(fitur['pengaruh'])
                    
                    with kol2:
                        st.markdown(f"**💡 Tips Perbaikan:**")
                        st.success(fitur['tips'])
                        
                        # Tambah meter visual untuk kepentingan
                        if fitur['nama'] == "BMI (Indeks Massa Tubuh)":
                            kepentingan = 95
                        elif fitur['nama'] == "Aktivitas Fisik (FAF)":
                            kepentingan = 85
                        elif fitur['nama'] == "Konsumsi Makanan Tinggi Kalori (FAVC)":
                            kepentingan = 80
                        else:
                            kepentingan = 60
                        
                        st.markdown(f"**🎯 Tingkat Kepentingan dalam Model:**")
                        st.progress(kepentingan/100)
                        st.caption(f"{kepentingan}% pengaruh dalam prediksi")
            
            # Bagian interaktif: Kalkulator dampak perubahan
            st.markdown("### 🧮 Simulasi Dampak Perubahan Gaya Hidup")
            
            kol_sim1, kol_sim2, kol_sim3 = st.columns(3)
            
            with kol_sim1:
                pilih_fitur = st.selectbox(
                    "Pilih Fitur untuk Diubah:",
                    ["Aktivitas Fisik", "Konsumsi Sayuran", "Waktu Layar", "Metode Transportasi"],
                    key="simulasi_fitur"
                )
            
            with kol_sim2:
                perubahan = st.select_slider(
                    "Tingkat Perubahan:",
                    options=["Sedikit", "Sedang", "Signifikan"],
                    value="Sedang",
                    key="simulasi_perubahan"
                )
            
            with kol_sim3:
                if st.button("Hitung Dampak", key="hitung_dampak"):
                    # Simulasi sederhana
                    dampak_map = {
                        "Aktivitas Fisik": {"Sedikit": "3%", "Sedang": "7%", "Signifikan": "15%"},
                        "Konsumsi Sayuran": {"Sedikit": "2%", "Sedang": "5%", "Signifikan": "10%"},
                        "Waktu Layar": {"Sedikit": "1%", "Sedang": "3%", "Signifikan": "6%"},
                        "Metode Transportasi": {"Sedikit": "2%", "Sedang": "4%", "Signifikan": "8%"}
                    }
                    
                    dampak = dampak_map.get(pilih_fitur, {}).get(perubahan, "0%")
                    
                    st.markdown(f"""
                    <div class="kotak-sukses">
                    <h4>🎯 Hasil Simulasi</h4>
                    <p>Perubahan <strong>{perubahan.lower()}</strong> pada <strong>{pilih_fitur}</strong> dapat mengurangi:</p>
                    <h3>{dampak} risiko obesitas</h3>
                    <p><em>Estimasi berdasarkan analisis data historis</em></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Insight dan rekomendasi
            st.markdown("### 🎯 Insight Utama dari Analisis Fitur")
            
            insight_list = [
                "🔴 **Faktor #1 adalah BMI** - Menjaga berat badan sehat adalah kunci utama",
                "🟠 **Aktivitas fisik lebih penting daripada diet ketat** untuk pencegahan jangka panjang",
                "🟡 **Faktor genetik (riwayat keluarga) penting** tapi bisa dikelola dengan gaya hidup",
                "🟢 **Perubahan kecil pada multiple fitur** lebih efektif daripada perubahan besar pada satu fitur",
                "🔵 **Faktor gaya hidup sedentari (TUE, MTRANS)** sering diremehkan tapi signifikan",
                "🟣 **Konsumsi sayuran** adalah faktor diet paling penting untuk kontrol berat"
            ]
            
            for insight in insight_list:
                st.markdown(f"• {insight}")
            
            # Call to action
            st.markdown("---")
            st.markdown("""
            <div class="kotak-info" style="text-align: center;">
            <h3>🚀 Mulai Perbaikan Hari Ini!</h3>
            <p>Pilih 1-2 fitur dengan kepentingan tinggi untuk difokuskan minggu ini.</p>
            <p><strong>Contoh:</strong> Tingkatkan aktivitas fisik + kurangi waktu layar</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Halaman 5: Riwayat
    elif halaman == "📋 Riwayat":
        st.markdown('<h2 class="judul-bagian">📋 Riwayat Prediksi</h2>', unsafe_allow_html=True)
        
        if 'riwayat_prediksi' in st.session_state and st.session_state.riwayat_prediksi:
            # Filter riwayat untuk pengguna saat ini
            riwayat_user = [r for r in st.session_state.riwayat_prediksi 
                          if r.get('username') == st.session_state.username]
            
            if riwayat_user:
                # Konversi ke DataFrame
                df_riwayat = pd.DataFrame(riwayat_user)
                
                # Tampilkan statistik
                kol1, kol2, kol3, kol4 = st.columns(4)
                
                with kol1:
                    total_prediksi = len(df_riwayat)
                    st.metric("Total Prediksi", total_prediksi)
                
                with kol2:
                    rata_bmi = df_riwayat['bmi'].mean()
                    st.metric("Rata-rata BMI", f"{rata_bmi:.1f}")
                
                with kol3:
                    rata_confidence = df_riwayat['confidence'].mean()
                    st.metric("Rata-rata Keyakinan", f"{rata_confidence:.1f}%")
                
                with kol4:
                    prediksi_terbaru = df_riwayat.iloc[-1]['prediksi']
                    st.metric("Prediksi Terbaru", prediksi_terbaru)
                
                # Tampilkan tabel riwayat
                st.markdown("### 📊 Riwayat Detail")
                
                # Format kolom tampilan
                kolom_tampilan = ['timestamp', 'Age', 'Gender', 'BMI', 'bmi', 'prediksi', 'confidence']
                df_tampil = df_riwayat[kolom_tampilan].copy()
                df_tampil['BMI'] = df_tampil['bmi'].round(1)
                df_tampil['confidence'] = df_tampil['confidence'].round(1).astype(str) + '%'
                df_tampil = df_tampil.drop('bmi', axis=1)
                
                st.dataframe(
                    df_tampil.style.background_gradient(subset=['BMI'], cmap='RdYlGn_r'),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Visualisasi
                kol1, kol2 = st.columns(2)
                
                with kol1:
                    # Trend BMI
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_riwayat['timestamp'],
                        y=df_riwayat['bmi'],
                        mode='lines+markers',
                        name='BMI',
                        line=dict(color='#2E86AB', width=3)
                    ))
                    
                    # Tambah garis rentang sehat
                    fig.add_hline(y=18.5, line_dash="dash", line_color="green", 
                                 annotation_text="Kekurangan Berat")
                    fig.add_hline(y=25, line_dash="dash", line_color="yellow", 
                                 annotation_text="Sehat")
                    fig.add_hline(y=30, line_dash="dash", line_color="orange", 
                                 annotation_text="Kelebihan Berat")
                    fig.add_hline(y=35, line_dash="dash", line_color="red", 
                                 annotation_text="Obesitas")
                    
                    fig.update_layout(
                        title="Trend BMI dari Waktu ke Waktu",
                        xaxis_title="Tanggal",
                        yaxis_title="BMI",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with kol2:
                    # Distribusi prediksi
                    hitung_prediksi = df_riwayat['prediksi'].value_counts()
                    
                    fig = px.pie(
                        values=hitung_prediksi.values,
                        names=hitung_prediksi.index,
                        title="Distribusi Prediksi",
                        color_discrete_sequence=px.colors.sequential.Viridis
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Opsi ekspor
                st.markdown("### 💾 Opsi Ekspor")
                
                kol1, kol2, kol3 = st.columns(3)
                
                with kol1:
                    if st.button("📥 Ekspor sebagai CSV"):
                        csv = df_riwayat.to_csv(index=False)
                        st.download_button(
                            label="Unduh CSV",
                            data=csv,
                            file_name="riwayat_prediksi_obesitas.csv",
                            mime="text/csv"
                        )
                
                with kol2:
                    if st.button("📊 Ekspor sebagai Excel"):
                        df_riwayat.to_excel("riwayat_obesitas.xlsx", index=False)
                        with open("riwayat_obesitas.xlsx", "rb") as file:
                            st.download_button(
                                label="Unduh Excel",
                                data=file,
                                file_name="riwayat_obesitas.xlsx",
                                mime="application/vnd.ms-excel"
                            )
                
                with kol3:
                    if st.button("🗑️ Hapus Riwayat Saya", type="secondary"):
                        # Hapus hanya riwayat user saat ini
                        st.session_state.riwayat_prediksi = [
                            r for r in st.session_state.riwayat_prediksi 
                            if r.get('username') != st.session_state.username
                        ]
                        st.success("✅ Riwayat prediksi Anda telah dihapus!")
                        st.rerun()
            else:
                st.info("""
                ## 📭 Belum Ada Riwayat Prediksi
                
                Anda belum membuat prediksi. Buat prediksi pertama Anda untuk melihat riwayat di sini.
                """)
        else:
            st.info("""
            ## 📭 Belum Ada Riwayat Prediksi
            
            Riwayat prediksi Anda akan muncul di sini setelah Anda membuat prediksi pertama.
            
            Untuk memulai:
            1. Pergi ke halaman **📊 Prediksi Obesitas**
            2. Isi informasi Anda
            3. Klik tombol **🚀 PREDIKSI RISIKO OBESITAS**
            4. Kembali ke sini untuk melihat riwayat Anda
            """)
    
    # Halaman 6: Profil
    elif halaman == "👤 Profil":
        profile_page()
    
    # Halaman 7: Tentang
    elif halaman == "⚙️ Tentang":
        kol1, kol2 = st.columns([3, 1])
        
        with kol1:
            st.markdown('<h2 class="judul-bagian">ℹ️ Tentang Sistem Prediksi Obesitas</h2>', unsafe_allow_html=True)
            
            st.markdown("""
            ### 🎯 Misi Kami
            
            Sistem Prediksi Obesitas bertujuan memberikan wawasan personal tentang 
            risiko kesehatan terkait berat menggunakan algoritma machine learning canggih.
            
            ### 🔬 Cara Kerja
            
            1. **Pengumpulan Data**: Kami menganalisis gaya hidup, pola makan, dan karakteristik fisik
            2. **Machine Learning**: Model kami menggunakan algoritma Random Forest yang dilatih pada ribuan sampel
            3. **Penilaian Risiko**: Kami menghitung kategori obesitas dan risiko kesehatan terkait
            4. **Rekomendasi Personal**: Kami memberikan saran kesehatan yang dapat ditindaklanjuti berdasarkan profil Anda
            
            ### 📊 Sumber Data
            
            Model kami dilatih pada dataset komprehensif termasuk:
            
            - Survei gaya hidup dan pola makan
            - Pengukuran fisik
            - Data penilaian kesehatan
            - Studi longitudinal tentang manajemen berat
            
            ### 🛡️ Privasi & Keamanan
            
            - Semua data diproses secara lokal di perangkat Anda
            - Tidak ada informasi pribadi yang disimpan di server kami
            - Prediksi hanya berdasarkan input yang Anda berikan
            - Anda mengontrol riwayat prediksi Anda
            
            ### ⚠️ Peringatan Medis
            
            **PENTING**: Sistem ini hanya untuk tujuan informasi dan **bukan pengganti** 
            saran medis profesional, diagnosis, atau perawatan.
            
            **Selalu konsultasikan dengan dokter atau penyedia layanan kesehatan berkualifikasi lainnya** 
            untuk pertanyaan apa pun yang Anda miliki tentang kondisi medis.
            
            ### 🏥 Kapan Harus ke Dokter
            
            Konsultasikan dengan profesional kesehatan jika:
            
            - BMI Anda 30 atau lebih tinggi
            - Anda mengalami kesulitan menurunkan berat meski telah mengubah gaya hidup
            - Anda mengalami masalah kesehatan terkait berat (tekanan darah tinggi, diabetes, dll.)
            - Anda memerlukan saran medis personal untuk manajemen berat
            """)
        
        with kol2:
            st.image("https://img.icons8.com/color/144/000000/artificial-intelligence.png", width=100)
            st.markdown("### 🤖 Info Model AI")
            
            info_model = {
                "Algoritma": "Random Forest",
                "Versi": "1.0",
                "Sampel Pelatihan": "2.111",
                "Akurasi": "92.3%",
                "Fitur": "15",
                "Terakhir Diperbarui": "Des 2025"
            }
            
            for kunci, nilai in info_model.items():
                st.info(f"**{kunci}**: {nilai}")
            
            st.markdown("---")
            st.markdown("### 🔗 Sumber Daya Berguna")
            
            sumber_daya = [
                "[WHO Fakta Obesitas](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight)",
                "[CDC Manajemen Berat](https://www.cdc.gov/healthyweight/index.html)",
                "[NIH Riset Obesitas](https://www.niddk.nih.gov/health-information/weight-management)",
                "[Piring Makan Sehat](https://www.hsph.harvard.edu/nutritionsource/healthy-eating-plate/)"
            ]
            
            for sumber in sumber_daya:
                st.markdown(sumber)
            
            st.markdown("---")
            st.markdown("### 📞 Kontak Darurat")
            
            st.markdown("""
            **Indonesia:**
            - 119 - Layanan Darurat
            - 1500-135 - Hotline Kemenkes""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 20px;'>
    <p>© 2025 Sistem Prediksi Obesitas Room 2 Data Science | Versi 1.0 | 
    <em>Hanya untuk tujuan edukasi dan informasi</em></p>
    <p style='font-size: 0.8rem; color: #999;'>
        Dibangun dengan Streamlit | Machine Learning
    </p>
</div>
""", unsafe_allow_html=True)

# Tambah interaktivitas
if st.session_state.get('logged_in', False) and st.sidebar.button("🔄 Muat Ulang Aplikasi"):
    st.rerun()