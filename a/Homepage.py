import streamlit as st
from sqlalchemy import func, create_engine, and_, select, insert, event
from module.models import Base, BarangMasuk, Item, BarangKeluar, Letak
from module.createdb import engine
from sqlalchemy.orm import Session
import pandas as pd
import datetime
from a.persediaan import stok


#create sesi
sesi = Session(bind=engine)

def main():
    
    # HEADER HOME PAGE
    now = datetime.date.today()
    with st.container():
        st.markdown('<div style="text-align: center; margin-top:0px;"><h1>Selamat Datang !</h1></div>', unsafe_allow_html=True)
        st.write(now.strftime("%A, %B %d, %Y"))
    st.divider()

    #jumlah barang by masuk, keluar, persediaan
    st.markdown(
        """
        <style>
            div[data-testid="column"]
            {
                border:1px solid white;
                border-radius : 50px 10px 50px 10px;
                padding : 25px;          
            } 
        
        
        </style>
        """,unsafe_allow_html=True
    )

    # ikhtisar jumlah data
    col1, col2, col3 = st.columns(3)
    barang_masukQty = sesi.query(func.sum(BarangMasuk.jumlah)).scalar() or 0
    barang_keluarQty = sesi.query(func.sum(BarangKeluar.jumlah)).scalar() or 0
    persediaanQty = barang_masukQty - barang_keluarQty
    with col1:
        st.write(f"### Barang Masuk\nTotal: {barang_masukQty}" if barang_masukQty is not None else "### Barang Masuk\nTotal: 0")
    with col2:
        st.write(f"### Barang Keluar\nTotal: {barang_keluarQty}" if barang_keluarQty is not None else "### Barang Keluar\nTotal: 0")
    with col3:
        st.write(f"### Persediaan\nTotal: {persediaanQty}" if persediaanQty is not None else "### Persediaan\nTotal: 0")
    st.divider()

    st.subheader("Barang Masuk")
    # barang masuk
    query_result = sesi.query(BarangMasuk).join(Item).join(Letak).all()
    df = pd.DataFrame([(data.part_number, data.asal, data.item.item, data.no_po, data.jumlah,data.hargaBeli, data.tanggal, data.letak.nama, data.keterangan) for data in query_result],
                    columns=['Part Number', 'Asal', 'Kategori', 'No PO', 'Jumlah','harga beli', 'Tanggal', 'Letak', 'Keterangan'])

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

 
    filtered_df = df.set_index("Part Number")
    st.write(filtered_df.tail())
        


    # barang keluar  
    st.divider()
    st.subheader("Barang Keluar")

    barangKeluar = sesi.query(BarangKeluar).join(Item).join(Letak).all()

    dkel = pd.DataFrame([(data.part_number, data.itemNumber, data.item.item, data.tujuan, data.jumlah, data.hargaJual, data.no_jalan, data.no_inv, data.tanggal, data.letak.nama, data.keterangan)for data in barangKeluar],
                        columns = ['Part Number','Item Number','Nama Barang','Tujuan','jumlah keluar','harga jual','No. Surat Jalan','No. Invoice','tanggal','letak','keterangan'])

    dkel = dkel.set_index("Part Number")
    st.write(dkel)

    st.divider()
    st.subheader("Persediaan")
    Stok = stok()
    st.write(Stok)



if __name__=="__main__":
    main()
