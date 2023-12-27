import streamlit as st
from streamlit_option_menu import option_menu
from module.models import Base, BarangMasuk, Item, BarangKeluar, Letak
from module.createdb import engine
from sqlalchemy.orm import Session
import pandas as pd
from dataUploader.upload_out import upload_file

#create sesi
sesi = Session(bind=engine)
def edit_barang_keluar(id, data):
    # Assuming ids is a list of IDs
    selected_rows = sesi.query(BarangKeluar).filter(BarangKeluar.id.in_(id)).all()

    if selected_rows:
        # Create a list of dictionaries containing the data
        data_list = []
        for row in selected_rows:
            data_dict = {
                'ID': row.id,
                'Part Number': row.part_number,
                'Item Number': row.itemNumber,
                'Nama Barang': row.item.item,
                'Tujuan': row.tujuan,
                'Jumlah': row.jumlah,
                'harga jual': row.hargaJual,
                'No Surat Jalan':row.no_jalan,
                'No invoice':row.no_inv,
                'Tanggal': row.tanggal,
                'Letak': row.letak.nama,
                'Keterangan': row.keterangan
            }
            data_list.append(data_dict)

        # Create a Pandas DataFrame from the list of dictionaries
        df = pd.DataFrame(data_list)
        df.set_index(df.index + 1, inplace=True)
        # Display the data
        data = st.data_editor(df, key="edited")
        data
        button = st.button("submit")
        if data is not None and button:
            # Ubah data editor menjadi Pandas DataFrame
            df = pd.DataFrame(data)
            
            # Tampilkan DataFrame yang telah diubah
            st.write(df)

            # Simpan data ke dalam list
            datas = []
            for index, row in df.iterrows():
                data_dict = {
                    'ID': row['ID'],
                    'Part Number': row['Part Number'],
                    'Item Number': row['Item Number'],
                    'Nama Barang': row['Nama Barang'],
                    'Tujuan': row['Tujuan'],
                    'Jumlah': row['Jumlah'],
                    'harga jual': row['harga jual'],
                    'No Surat Jalan':row['No Surat Jalan'],
                    'No invoice':row['No invoice'],
                    'Tanggal': row['Tanggal'],
                    'Letak': row['Letak'],
                    'Keterangan': row['Keterangan']
                }
                datas.append(data_dict)
                
            for data_dict in datas:
                id_barang_keluar = data_dict['ID']
                # Ambil objek BarangMasuk berdasarkan ID
                barang_keluar = sesi.query(BarangKeluar).get(id_barang_keluar)

                # Perbarui nilai atribut BarangMasuk
                barang_keluar.part_number = data_dict['Part Number']
                barang_keluar.itemNumber = data_dict['Item Number']
                barang_keluar.tujuan = data_dict['Tujuan']
                
                #item
                items = data_dict['Nama Barang']
                item = sesi.query(Item).filter_by(item=items).first()
            
                barang_keluar.item = item
                barang_keluar.jumlah = data_dict['Jumlah']
                barang_keluar.hargaJual = data_dict['harga jual']
                barang_keluar.tanggal = data_dict['Tanggal']
                barang_keluar.no_inv = data_dict['No invoice']
                barang_keluar.no_jalan = data_dict['No Surat Jalan']


                #letak
                letak_nama = data_dict['Letak']
                letak = sesi.query(Letak).filter_by(nama=letak_nama).first()
                
                
                barang_keluar.letak = letak
                barang_keluar.keterangan = data_dict['Keterangan']

                # Commit perubahan ke dalam database
                sesi.commit()
                st.success("data telah di update")

            # Tampilkan data yang telah disimpan
            #st.write(datas)

    
    else:
        data.set_index(data.index + 1, inplace=True)
        st.write(data)
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

def main():
    upload_file()
   
    st.header("Barang Keluar")

    menu = menu = option_menu(menu_title=None,options=["data","input","edit","delete"], orientation="horizontal", icons=["database-check","database-add","database-gear","database-dash"], default_index=0)
    

    if menu == "input":
        st.write("Masukan data barang !")
        col1, col2 = st.columns(2)
        with col1:
            pN = sesi.query(BarangMasuk.part_number).distinct().all()
            partNumber = st.selectbox("Part_number: ",[i.part_number for i in pN]) #==> dropdown menu
            itemNum = st.text_input("Item Number :")
            tujuan = st.text_input("Tujuan :")
            no_jalan = st.text_input("No. Surat Jalan : ")
            no_inv = st.text_input("No. Invoice :")
            
            

        with col2:    
            item = sesi.query(Item).all()
            item_ = st.selectbox("Item : ",[i.item for i in item])
            jumlahKeluar= st.number_input("Jumlah Keluar :")
            hargaJual = st.number_input("Harga Jual :")
            tanggal = st.date_input("Tanggal :")
            let = sesi.query(Letak).all()
            letak = st.selectbox("Letak :", [i.nama for i in let])
            ket = st.text_input("Keterangan :")


        button = st.button("Submit ")

        if button and partNumber and item_ and letak:
            item_terpilih = sesi.query(Item).filter(Item.item == item_).first()
            letak_terpilih = sesi.query(Letak).filter(Letak.nama == letak).first()
            persediaan = sesi.query(BarangMasuk).filter_by(part_number =partNumber, item=item_terpilih).first()
            if not persediaan:
                barang = BarangKeluar(
                    part_number = partNumber,
                    itemNumber = itemNum,
                    tujuan = tujuan,
                    item_id = item_terpilih,
                    item = item_terpilih,
                    jumlah = jumlahKeluar,
                    hargaJual = hargaJual,
                    tanggal = tanggal,
                    letak_id = letak_terpilih,
                    letak = letak_terpilih,
                    no_inv = no_inv,
                    no_jalan = no_jalan,
                    keterangan = ket
                )
            
                sesi.add(barang)
                sesi.commit()
                st.warning("pastikan input data sesuai dengan yang ada di database!")
            else:
                
                #item_terpilih = sesi.query(Item).filter(Item.item == item_).first()
                barang = BarangKeluar(
                    part_number = partNumber,
                    itemNumber = itemNum,
                    tujuan = tujuan,
                    item_id = item_terpilih,
                    item = item_terpilih,
                    jumlah = jumlahKeluar,
                    hargaJual = hargaJual,
                    tanggal = tanggal,
                    letak_id = letak_terpilih,
                    letak = letak_terpilih,
                    no_inv = no_inv,
                    no_jalan = no_jalan,
                    keterangan = ket
                )
            
                sesi.add(barang)
                sesi.commit()

                st.success("Barang berhasil di Update")
                
        elif button and (not partNumber or not item_):
            st.error('Mohon isi Part Number dan Item sebelum submit.')
        elif button and (letak is None ):
            st.error('Mohon isi Letak sebelum submit.')     
    if menu == "data":
        
        barangKeluar = sesi.query(BarangKeluar).join(Item).join(Letak).all()
        dkel = pd.DataFrame([(data.part_number, data.itemNumber, data.item.item, data.tujuan, data.jumlah, data.hargaJual, data.tanggal, data.letak.nama,data.no_jalan, data.no_inv, data.keterangan)for data in barangKeluar],
                            columns = ['Part Number','Item Number','Nama Barang','Tujuan','jumlah keluar','harga jual','No. Surat Jalan','No. Invoice','tanggal','letak','keterangan'])
        st.write(dkel)
    if menu == "edit":
        st.write("allo")
        barangKeluar = sesi.query(BarangKeluar).join(Item).join(Letak).all()
        dkel = pd.DataFrame([(data.id,data.part_number, data.itemNumber, data.item.item, data.tujuan, data.jumlah, data.hargaJual, data.no_jalan, data.no_inv, data.tanggal, data.letak.nama, data.keterangan)for data in barangKeluar],
                            columns = ['ID','Part Number','Item Number','Nama Barang','Tujuan','jumlah keluar','harga jual','No. Surat Jalan','No. Invoice','tanggal','letak','keterangan'])
        id_ = dkel['ID']
        ID = st.multiselect("Silakan pilih data yang ingin kamu hapus berdasarkan ID : ", id_)
        if ID is not None:
            edit_barang_keluar(id=ID, data=dkel)

    if menu == "delete":
        barangKeluar = sesi.query(BarangKeluar).join(Item).join(Letak).all()
        dkel = pd.DataFrame([(data.id,data.part_number, data.itemNumber, data.item.item, data.tujuan, data.jumlah, data.hargaJual, data.no_jalan, data.no_inv, data.tanggal, data.letak.nama, data.keterangan)for data in barangKeluar],
                            columns = ['ID','Part Number','Item Number','Nama Barang','Tujuan','jumlah keluar','harga jual','No. Surat Jalan','No. Invoice','tanggal','letak','keterangan'])
    
        #delete item in dataframe 
        col1,col2 = st.columns([9,1])
               
        with col1:
            id_ = dkel['ID']
            ID = st.multiselect("Silakan pilih data yang ingin kamu hapus berdasarkan ID : ", id_)
        with col2:
            hapus = st.button("Hapus")
            st.markdown(
                """
                <style>
                    div[data-testid="column"].st-emotion-cache-ytkq5y{
                        color : red;
                        padding-top : 28px;
                        padding-left : 10px;
                      
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )
        if hapus:
            sesi.query(BarangKeluar).filter(BarangKeluar.id.in_(ID)).delete(synchronize_session=False)    
            sesi.commit()
            st.success("data telah dihapus")
        else: 
            dkel.set_index(dkel.index + 1, inplace=True)
            st.dataframe(dkel)
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

if __name__ == "__main__":
    main()