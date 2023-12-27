import streamlit as st
from sqlalchemy.orm import Session
from datetime import datetime
from module.createdb import engine
from module.models import BarangKeluar, Item, Letak, BarangMasuk
import pandas as pd
sesi = Session(bind=engine)
def inserting_data_out(file):
    sesi = Session(bind=engine)
    try: 
        if file is not None:
            df = file
            for index, row in df.iterrows():
                #part_select = sesi.query(BarangMasuk).filter(BarangMasuk.part_number == row["part number"])
                item_selected = sesi.query(Item).filter(Item.item == row["item"]).first()
                letak_selected = sesi.query(Letak).filter(Letak.nama == row["letak"]).first()
                
                # Periksa keberadaan data sebelum insert
                existing_data = (
                    sesi.query(BarangMasuk)
                    .filter_by(
                        part_number=row["part number"],
                        item=item_selected,
                        letak=letak_selected
                    )
                    .first()
                )
                
                if existing_data:
                    barkel = BarangKeluar(
                        part_number=row["part number"],
                        itemNumber=row["item number"],
                        tujuan=row["tujuan"],
                        item_id=item_selected.id,
                        item=item_selected,
                        jumlah=row["jumlah keluar"],
                        hargaJual=row["harga"],
                        tanggal=datetime.strptime(row["tanggal"], "%m/%d/%y"),
                        letak_id=letak_selected.id,
                        letak=letak_selected,
                        no_inv=row["no. invoice"],
                        no_jalan=row["no. surat jalan"],
                        keterangan=row["keterangan"]
                    ) 
                    sesi.add(barkel)
                    sesi.commit()
                else:
                    st.error(f"Data tidak ditemukan untuk part number :{row['part number']}, item: {row['item']},letak: {row['letak']} pastikan barang telah di input pada barang masuk")
        else:
            # ketika file None
            st.warning("File yang diupload tidak valid. Pastikan Anda sudah memilih file.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")


#upload file     
def upload_file():
    with st.sidebar:
        st.subheader("upload files")
        data = st.file_uploader("Silakan masukkan file di sini")
    
        if data is not None:
            separator = r";|,"
            df = pd.read_csv(data, sep=separator, engine='python')
            data_lower = df.rename(columns=lambda x: x.lower())
                        
            button = st.button("Submit")
            
            if button:
                
                #data_lower = data_lower.dropna(subset=['tanggal'])
                inserting_data_out(data_lower)
                st.success("Data berhasil ditambahkan!")

        else:
            st.warning("pastikan file excel, csv mengandung kolom yang sesuai dengan input barang masuk")

def main():
    upload_file()
    
    
if __name__=="__main__":
    main()