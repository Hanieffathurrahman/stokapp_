import streamlit as st
from streamlit_option_menu import option_menu
import datetime
from sqlalchemy import func, create_engine, and_, select, insert
from module.models import Base, BarangMasuk, Item, BarangKeluar, Letak
from module.createdb import engine
from sqlalchemy.orm import Session, make_transient
import pandas as pd

#create sesi
sesi = Session(bind=engine)


def stok():
    #get data from barang masuk dan barang keluar convert to data frame
    barmas = sesi.query(BarangMasuk).join(Item).join(Letak).all()
    barkel = sesi.query(BarangKeluar).join(Item).join(Letak).all()

    #convert data to dataframe
    df_masuk = pd.DataFrame([(data.part_number, data.asal, data.item.item, data.no_po, data.jumlah, data.hargaBeli, data.tanggal, data.letak.nama, data.keterangan) for data in barmas],
                                  columns=['Part Number', 'Asal', 'Kategori', 'No PO', 'jumlah_masuk', 'harga beli', 'Tanggal', 'Letak', 'Keterangan'])
    df_keluar = pd.DataFrame([(data.part_number, data.itemNumber,data.tujuan,data.no_jalan, data.no_inv, data.item.item, data.jumlah, data.hargaJual, data.tanggal, data.letak.nama, data.keterangan) for data in barkel],
                                  columns=['Part Number', 'Item Number','Tujuan','No invoice','No surat jalan', 'Kategori', 'jumlah_keluar', 'harga jual', 'Tanggal', 'Letak', 'Keterangan'])
    df_masuk_grouped = df_masuk.groupby(['Part Number', 'Kategori', 'Letak']).agg({
    'Asal':'first',
    'jumlah_masuk': 'sum',
    'harga beli': 'first',  # Ambil nilai pertama karena semuanya sama dalam satu kelompok
    }).reset_index()

    # Mengelompokkan dan menjumlahkan barang keluar
    df_keluar_grouped = df_keluar.groupby(['Part Number', 'Kategori', 'Letak']).agg({
        'Tujuan' : 'first',
        'jumlah_keluar': 'sum',
        'harga jual': 'first',  # Ambil nilai pertama karena semuanya sama dalam satu kelompok
    }).reset_index()

    # Merge DataFrame df_masuk_grouped dan df_keluar_grouped
    merged_df = pd.merge(df_masuk_grouped, df_keluar_grouped, on=['Part Number', 'Kategori', 'Letak'], how='outer')

    # Isi nilai NaN dengan 0 untuk menghindari kesalahan dalam perhitungan
    merged_df['jumlah_masuk'].fillna(0, inplace=True)
    merged_df['jumlah_keluar'].fillna(0, inplace=True)

    merged_df['jumlah'] = merged_df['jumlah_masuk'] - merged_df['jumlah_keluar']
    merged_df = merged_df[['Part Number', 'Kategori', 'Asal', 'Tujuan', 'jumlah', 'jumlah_masuk', 'jumlah_keluar', 'harga beli', 'harga jual', 'Letak']]

    return merged_df

def filtering_stok(merg_df, itemSelect, letakSelect):
    if not itemSelect and not letakSelect:
        return merg_df
    elif itemSelect:
        return merg_df[merg_df['Kategori'].isin(itemSelect)]
    elif letakSelect:
        return merg_df[merg_df['Letak'].isin(letakSelect)]
    else:
        return merg_df[(merg_df['Kategori'].isin(itemSelect)) & (merg_df['Letak'].isin(letakSelect))]
def main():
    merg_df = stok()
    
    st.header("Persediaan")
     
    st.markdown(
        """
        <style>
            div[data-testid="stDataFrame"]{
                width: 100%;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


    #fitur select item

    col1, col2 = st.columns(2)

    with col1:
        filtering_item = merg_df["Kategori"]
        items = filtering_item.unique()
        itemSelect = st.multiselect("Pilih Item yang ingin kamu tampilkan:", items)

    with col2:
        filtering_letak = merg_df['Letak']
        letak = filtering_letak.unique()
        letakSelect = st.multiselect('Pilih letak barang yang ingin kamu tampilkan:', letak)

    stok_df = filtering_stok(merg_df, itemSelect, letakSelect)

    st.write("Data Stok Persediaan")
    st.write(stok_df)

    for index, row in stok_df.iterrows():
        if row['jumlah'] > 2:
            part_num = row['Part Number']
            st.warning(f"Jumlah barang {part_num} melebihi batas minimal")


    
if __name__=="__main__":
    main()