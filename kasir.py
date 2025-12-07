import streamlit as st
import datetime
import pandas as pd
from pathlib import Path
import plotly.express as px

# ================== KONFIG & DATA ================== = {
ITEMS = {
    "PANCONG": {
        "Pancong Polos": 10_000,
        "Pancong Meses Susu": 12_000,
        "Pancong Milo": 15_000,
        "Pancong Strawberry": 12_000,
        "Pancong Ovaltine": 12_000,
        "Pancong Kacang": 13_000,
        "Pancong Keju Susu": 15_000,
        "Pancong Greentea": 13_000,
        "Pancong Tiramisu": 13_000,
        "Pancong Taro": 13_000,
        "Pancong Oreo": 13_000,
        "Pancong Choco Crunchy": 16_000,
        "Pancong Redvelvet": 13_000,
    },
    # kategori lain nanti tinggal ditambah di sini


     
}

st.set_page_config(page_title="Warkop Pancong", layout="wide")

def get_log_file(cabang: str) -> Path:
    return Path(f"kasir_log_{cabang.lower().replace(' ', '_')}.txt")
st.title("🏪 KASIR Warkop Pancong MULTI-CABANG")
st.markdown("**Bogor | Kalimulya | GDC | Sawangan**")

# ================== SIDEBAR ==================

st.sidebar.title("🏪 Pilih Cabang Warkop")
cabang_options = ["Bogor", "Kalimulya", "GDC", "Sawangan"]
CABANG = st.sidebar.selectbox("Cabang:", cabang_options, index=0)
LOG_FILE = get_log_file(CABANG)

st.sidebar.success(f"📍 {CABANG}")
st.sidebar.markdown("---")

st.sidebar.subheader("🛠 Menu Admin")
admin_pass_input = st.sidebar.text_input("Password admin", type="password")
is_admin = admin_pass_input == "adminrumah"   # ganti sesuai selera

if is_admin:
    if st.sidebar.button("🗑️ Hapus Log Cabang Ini"):
        LOG_FILE.unlink(missing_ok=True)
        st.sidebar.success(f"Log transaksi {CABANG} sudah dihapus.")
        st.rerun()
else:
    st.sidebar.caption("Masukkan password admin untuk akses hapus log.")

# ================== INPUT TRANSAKSI ==================

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"### 💰 Cabang: **{CABANG}**")
with col_head2:
    st.metric("Status", "🟢 Online")

col1, col2, col3, col4 = st.columns(4)

with col1:
    kategori = st.selectbox("📂 Kategori", list(ITEMS.keys()))

with col2:
    nama = st.selectbox("🛒 Pilih Barang", list(ITEMS[kategori].keys()))

with col3:
    qty = st.number_input("📦 Qty", min_value=1, step=1)

with col4:
    metode = st.selectbox("💳 Metode Bayar", ["Tunai", "QRIS"])
    harga = float(ITEMS[kategori][nama])
    st.metric("💵 Harga/item", f"Rp {harga:,.0f}")


# ================== PROSES BAYAR ==================

if st.button(f"✅ PROSES TRANSAKSI ({CABANG})", type="primary", use_container_width=True):
    if nama and qty > 0 and harga > 0:
        total = qty * harga
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.balloons()
        st.success(
            f"""
            ### 🧾 STRUK TRANSAKSI
            **Cabang : {CABANG}**  
            **Waktu  : {timestamp}**
            
            | Barang | Qty | Harga | Total |
            |--------|-----|-------|-------|
            | **{nama}** | {qty} | Rp {harga:,.0f} | **Rp {total:,.0f}** |
            **Metode Bayar: {metode}**
            """
        )

        # format log: waktu|cabang|barang|qty|harga|total|metode
        log_line = f"{timestamp}|{CABANG}|{nama}|{qty}|{harga}|{total}|{metode}\n"
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
        for line in lines:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 7:
                waktu, cabang_log, barang, qty_log, harga_log, total_log, metode_log = parts[:7]
                qty_num = int(qty_log)
                harga_num = float(harga_log)
                total_num = float(total_log)
                rows.append(
                    [
                        waktu,
                        barang,
                        qty_num,
                        harga_num,
                        total_num,
                        metode_log,
                    ]
                )

        if rows:
            df = pd.DataFrame(
                rows,
                columns=["Waktu", "Barang", "Qty", "HargaNum", "TotalNum", "Metode"],
            )
            df["Harga"] = df["HargaNum"].map(lambda x: f"Rp {x:,.0f}")
            df["Total"] = df["TotalNum"].map(lambda x: f"Rp {x:,.0f}")

            st.dataframe(
                df[["Waktu", "Barang", "Qty", "Harga", "Total", "Metode"]],
                use_container_width=True,
                hide_index=True,
            )

            # summary tunai vs qris
            rekap_metode = df.groupby("Metode")["TotalNum"].sum().reset_index()
            grand_total = df["TotalNum"].sum()

            c1, c2, c3 = st.columns(3)
            tunai_total = rekap_metode.loc[rekap_metode["Metode"] == "Tunai", "TotalNum"].sum()
            qris_total = rekap_metode.loc[rekap_metode["Metode"] == "QRIS", "TotalNum"].sum()
            c1.metric("💵 Tunai", f"Rp {tunai_total:,.0f}")
            c2.metric("💎 Total Penjualan Cabang", f"Rp {grand_total:,.0f}")
            c3.metric("📱 QRIS", f"Rp {qris_total:,.0f}")

            # Rekap harian per cabang
            with st.expander("📅 Rekap Harian per Metode"):
                df["Tanggal"] = df["Waktu"].str.split(" ").str[0]
                rekap_harian = (
                    df.groupby(["Tanggal", "Metode"])["TotalNum"].sum().reset_index()
                )
                pivot = rekap_harian.pivot(
                    index="Tanggal", columns="Metode", values="TotalNum"
                ).fillna(0)
                pivot["Total"] = pivot.sum(axis=1)
                tampil = pivot.applymap(lambda x: f"Rp {x:,.0f}")
                st.dataframe(tampil, use_container_width=True)

                fig = px.bar(
                    rekap_harian,
                    x="Tanggal",
                    y="TotalNum",
                    color="Metode",
                    barmode="group",
                    title=f"Rekap Harian {CABANG} per Metode",
                )
                st.plotly_chart(fig, use_container_width=True)

            # download csv
            csv = df[["Waktu", "Barang", "Qty", "HargaNum", "TotalNum", "Metode"]].to_csv(
                index=False
            ).encode("utf-8")
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
