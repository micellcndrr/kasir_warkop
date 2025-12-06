import streamlit as st
import datetime
import pandas as pd
from pathlib import Path
import plotly.express as px

ITEMS = {
    "Es Teh Manis": 8000,
    "Kopi Susu": 12000,
    "Teh Manis": 6000,
    "Roti Bakar": 15000,
    "Indomie Goreng": 10000,
}


# Konfigurasi halaman
st.set_page_config(page_title="Warkop Pancong ", layout="wide")

# Fungsi dapatkan nama file log per cabang
def get_log_file(cabang: str) -> Path:
    return Path(f"kasir_log_{cabang.lower().replace(' ', '_')}.txt")

st.title("🏪 KASIR Warkop MULTI-CABANG")
st.markdown("**Bogor | Kalimulya | GDC | Sawangan**")

# ================== SIDEBAR ==================
st.sidebar.title("🏪 Pilih Cabang Warkop")
cabang_options = ["Bogor", "Kalimulya", "GDC", "Sawangan"]
CABANG = st.sidebar.selectbox("Cabang:", cabang_options, index=0)
LOG_FILE = get_log_file(CABANG)

st.sidebar.success(f"📍 {CABANG}")
st.sidebar.markdown("---")

# ================== INPUT TRANSAKSI ==================
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"### 💰 Cabang: **{CABANG}**")
with col_head2:
    st.metric("Status", "🟢 Online")

col1, col2, col3 = st.columns(3)
with col1:
    nama = st.selectbox("🛒 Pilih Barang", options=list(ITEMS.keys()))
with col2:
    qty = st.number_input("📦 Qty", min_value=1, step=1)
with col3:
    # harga otomatis dari ITEMS, TIDAK bisa diubah user
    harga = float(ITEMS[nama])
    st.metric("💵 Harga/item", f"Rp {harga:,.0f}")


# ================== PROSES BAYAR ==================
if st.button(f"✅ PROSES TRANSAKSI ({CABANG})", type="primary", use_container_width=True):
    if nama and qty > 0 and harga > 0:
        total = qty * harga
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Tampilkan struk
        st.balloons()
        st.success(
            f"""
            ### 🧾 STRUK TRANSAKSI
            **Cabang : {CABANG}**  
            **Waktu  : {timestamp}**
            
            | Barang | Qty | Harga | Total |
            |--------|-----|-------|-------|
            | **{nama}** | {qty} | Rp {harga:,.0f} | **Rp {total:,.0f}** |
            """
        )

        # Simpan ke file log cabang
        log_line = f"{timestamp} | {CABANG} | {nama} | {qty} | {harga} | {total}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)

        st.rerun()
    else:
        st.error("❌ Lengkapi semua field dengan benar!")

# ================== RIWAYAT TRANSAKSI CABANG ==================
st.markdown("---")
st.subheader(f"📊 Riwayat Transaksi - {CABANG}")

if LOG_FILE.exists():
    raw = LOG_FILE.read_text(encoding="utf-8").strip()
    if raw:
        lines = raw.split("\n")
        rows = []
        grand_total = 0.0

        for line in lines:
            parts = line.split("|")
            if len(parts) >= 6:
                waktu, cabang_log, barang, qty_log, harga_log, total_log = parts[:6]
                harga_num = float(harga_log)
                total_num = float(total_log)
                rows.append(
                    [
                        waktu,
                        barang,
                        int(qty_log),
                        f"Rp {harga_num:,.0f}",
                        f"Rp {total_num:,.0f}",
                    ]
                )
                grand_total += total_num

        if rows:
            df = pd.DataFrame(rows, columns=["Waktu", "Barang", "Qty", "Harga", "Total"])
            st.dataframe(df, use_container_width=True, hide_index=True)

            c1, c2, c3 = st.columns(3)
            c2.metric("💎 Total Penjualan Cabang", f"Rp {grand_total:,.0f}")

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                f"📥 Download CSV {CABANG}",
                data=csv,
                file_name=f"{CABANG}_transaksi.csv",
                mime="text/csv",
            )
        else:
            st.info(f"📝 {CABANG}: Belum ada transaksi tersimpan.")
    else:
        st.info(f"📝 {CABANG}: Belum ada transaksi.")
else:
    st.info(f"📝 {CABANG}: File log belum dibuat.")

# Hapus log caban

# ==================
