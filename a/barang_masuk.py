import streamlit as st
from sqlalchemy import func, create_engine, and_, select, insert
from module.models import Base, BarangMasuk, Item, BarangKeluar, Letak
from module.createdb import engine
from sqlalchemy.orm import Session
import pandas as pd
import datetime
from dataUploader.upload_in import inserting_data
from streamlit_option_menu import option_menu
import base64
#create sesi
sesi = Session(bind=engine)


def edit_barang_masuk(id, data):
    # Assuming ids is a list of IDs
    selected_rows = sesi.query(BarangMasuk).filter(BarangMasuk.id.in_(id)).all()

    if selected_rows:
        # Create a list of dictionaries containing the data
        data_list = []
        for row in selected_rows:
            data_dict = {
                'ID': row.id,
                'Part Number': row.part_number,
                'Asal': row.asal,
                'Nama Barang': row.item.item,
                'No PO': row.no_po,
                'Jumlah': row.jumlah,
                'harga beli': row.hargaBeli,
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
                    'Asal': row['Asal'],
                    'Nama Barang': row['Nama Barang'],
                    'No PO': row['No PO'],
                    'Jumlah': row['Jumlah'],
                    'harga beli': row['harga beli'],
                    'Tanggal': row['Tanggal'],
                    'Letak': row['Letak'],
                    'Keterangan': row['Keterangan']
                }
                datas.append(data_dict)
                
            for data_dict in datas:
                id_barang_masuk = data_dict['ID']
                # Ambil objek BarangMasuk berdasarkan ID
                barang_masuk = sesi.query(BarangMasuk).get(id_barang_masuk)

                # Perbarui nilai atribut BarangMasuk
                barang_masuk.part_number = data_dict['Part Number']
                barang_masuk.asal = data_dict['Asal']
                
                #item
                items = data_dict['Nama Barang']
                item = sesi.query(Item).filter_by(item=items).first()
                if not item:
                    item = Item(item=items)
                    sesi.add(item)
                    sesi.commit()
                barang_masuk.item = item

                barang_masuk.no_po = data_dict['No PO']
                barang_masuk.jumlah = data_dict['Jumlah']
                barang_masuk.harga_beli = data_dict['harga beli']
                barang_masuk.tanggal = data_dict['Tanggal']


                #letak
                letak_nama = data_dict['Letak']
                letak = sesi.query(Letak).filter_by(nama=letak_nama).first()
                if not letak:
                    letak = Letak(nama=letak_nama)
                    sesi.add(letak)
                    sesi.commit()
                # Perbarui nilai letak pada BarangMasuk
                barang_masuk.letak = letak
                barang_masuk.keterangan = data_dict['Keterangan']

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

def uploader():
    # file uploader
    with st.sidebar:
        st.subheader("upload files")
        file_upload = st.file_uploader("silakan upload data lama ! ")

        #if not uploaded 
        if file_upload is not None:
            data = pd.read_csv(file_upload, sep=';')
            button = st.button("Submit")

            #submited
            if button:
                #reformating name using lowercase 
                data_lower = data.rename(columns=lambda x:x.lower())
                
                #inserting data to barang masuk
                inserting_data(data_lower)
                st.success("data berhasil ditambah")
        else:
            st.warning("pastikan file excel, csv mengandung kolom yang sesuai dengan input barang masuk")

def deleteItem(id):
    # Mulai sesi transaksi
    with Session() as sesi:
        try:
            # Lakukan penghapusan pada tabel BarangMasuk
            sesi.query(BarangMasuk).filter(BarangMasuk.id.in_(id)).delete(synchronize_session=False)
        except Exception as e:
            # Rollback jika terjadi kesalahan
            sesi.rollback()
            print(f"Error: {e}")

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index = False).encode('utf-8')

def main():
    #uploader in sidebar
    uploader()
    st.header("Barang Masuk")

    menu = option_menu(menu_title=None,options=["data","input","edit","delete"], orientation="horizontal", icons=["database-check","database-add","database-gear","database-dash"], default_index=0)

    #================================================== menu input barang masuk ==============================
    if menu == "input":

        st.write("Masukan data barang !")
        now = datetime.date.today()
        tgl = now.strftime("%Y %m %d")

        col1, col2 = st.columns(2)
        with col1:
            partNumber = st.text_input("Part Number :")
            asal_ = st.text_input("Asal :")
            item = sesi.query(Item).all()
            item_ = st.selectbox("Item : ",[i.item for i in item]+['Tambah baru'])
            if item_ == 'Tambah baru':
                new_item = st.text_input("Masukan Item baru ! :")

            no_po = st.text_input("No PO :")
            hargaBeli = st.number_input("Harga Beli :",0)
        with col2:
            
            jumlahMasuk = st.number_input("Jumlah masuk :",0)
            tanggal = st.date_input("Tanggal :",now)
            
            letak_ = sesi.query(Letak).all()
            letak = st.selectbox("Letak :", [i.nama for i in letak_]+['Tambah letak'])

            if letak == 'Tambah letak':
                letakBaru = st.text_input('Masukan Letak baru  :')
            ket = st.text_area("Keterangan :")

        st.write('\n')
        
        submit = st.button("Submit ")

        if submit and partNumber and (item_ != 'Tambah baru' or new_item)and (letak != 'Tambah letak' or letakBaru):

            #add barang masuk, item and persedian by  item and letak 
            #konsisi 1 : item == item baru dan letak == letak baru ==> ketika item dan letak tidak ada dalam database
            if (item_ == 'Tambah baru' and new_item) and (letak == 'Tambah letak' and letakBaru):
                if not sesi.query(Item).filter(Item.item == new_item).first() and not sesi.query(Letak).filter(Letak.nama==letakBaru).first():
                    item_baru = Item(item = new_item)
                    letak_baru = Letak(nama = letakBaru)        
                    barangMasuk = BarangMasuk(
                        part_number = partNumber,
                        asal = asal_,
                        item_id = item_baru,
                        item = item_baru,
                        no_po = no_po,
                        hargaBeli = hargaBeli,
                        jumlah = jumlahMasuk,
                        tanggal = tanggal,
                        letak_id = letak_baru,
                        letak = letak_baru,
                        keterangan = ket,
                    )
                    
                    sesi.add_all([item_baru,letak_baru,barangMasuk])
                    sesi.commit()
                    st.success("Data berhasil di masukan !")


            #kondisi 2 : item == item baru dan letak == letak ==> ketika item tidak ada dalam database sedangkan letak ada dalam database
            elif (item_ == 'Tambah baru' and new_item):
                if not sesi.query(Item).filter(Item.item == new_item).first():
                    letak_terpilih = sesi.query(Letak).filter(Letak.nama == letak).first()
                    item_baru = Item(item = new_item)       
                    barangMasuk = BarangMasuk(
                        part_number = partNumber,
                        asal = asal_,
                        item_id = item_baru,
                        item = item_baru,
                        no_po = no_po,
                        hargaBeli = hargaBeli,
                        jumlah = jumlahMasuk,
                        tanggal = tanggal,
                        letak_id = letak_terpilih,
                        letak = letak_terpilih,
                        keterangan = ket,
                    )
                   
                    sesi.add_all([item_baru,barangMasuk])
                    sesi.commit()
                    st.success("Data berhasil di masukan !")

            #kondisi 3 : item == item dan letak == letak baru ==>  ketika item ada didatabase dan letak tidak ada dalam database
            elif (letak == 'Tambah letak' and letakBaru):
                if not sesi.query(Letak).filter(Letak.nama ==letakBaru).first():
                    item_terpilih = sesi.query(Item).filter(Item.item == item_).first()
                    letak_baru = Letak(nama = letakBaru)
                    barangMasuk = BarangMasuk(
                        part_number = partNumber,
                        asal = asal_,
                        item_id = item_terpilih,
                        item = item_terpilih,
                        no_po = no_po,
                        hargaBeli = hargaBeli,
                        jumlah = jumlahMasuk,
                        tanggal = tanggal,
                        letak_id = letak_baru,
                        letak = letak_baru,
                        keterangan = ket,
                    )
                    
                    sesi.add_all([letak_baru,barangMasuk])
                    sesi.commit()
                    st.success("Data berhasil di masukan !")

            #kondisi 4 
            else:
                #add barang masuk if item available in item table
                item_terpilih = sesi.query(Item).filter(Item.item == item_).first()
                letak_terpilih = sesi.query(Letak).filter(Letak.nama == letak).first()
                barangMasuk = BarangMasuk(
                    part_number=partNumber,
                    asal=asal_,
                    item_id=item_terpilih,
                    item=item_terpilih,
                    no_po=no_po,
                    jumlah=jumlahMasuk,
                    hargaBeli = hargaBeli,
                    tanggal=tanggal,
                    letak_id = letak_terpilih,
                    letak=letak_terpilih,
                    keterangan=ket,
                )
                sesi.add(barangMasuk)
                sesi.commit()
        elif submit and (not partNumber or not item_):
            st.error('Mohon isi Part Number dan Item sebelum submit.')
        elif submit and (letak is None or (letak == 'Tambah letak' and not letakBaru)):
            st.error('Mohon isi Letak sebelum submit.')  
    if menu == 'data':
        #menampilkan data barang masuk
        query_result = sesi.query(BarangMasuk).join(Item).join(Letak).all()

        # Mengonversi hasil query ke Pandas DataFrame
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

        st.dataframe(df)
        data = convert_df(df=df)
        st.download_button(label="unduh data anda", data=data, file_name="barang_masuk.csv", mime='csv/text')
    if menu == "edit":
        query_result = sesi.query(BarangMasuk).join(Item).join(Letak).all()
        df = pd.DataFrame([(data.id,data.part_number, data.asal, data.item.item, data.no_po, data.jumlah,data.hargaBeli, data.tanggal, data.letak.nama, data.keterangan) for data in query_result],
                        columns=['ID','Part Number', 'Asal', 'Nama Barang', 'No PO', 'Jumlah','harga beli', 'Tanggal', 'Letak', 'Keterangan'])
       
        id_ = df['ID']
        Id = st.multiselect("Silakan pilih data yang ingin kamu edit berdasarkan ID : ", id_)
        
        if Id is not None:
            edit_barang_masuk(id=Id, data=df)
    if menu == "delete":
        
        #menampilkan data barang masuk
        query_result = sesi.query(BarangMasuk).join(Item).join(Letak).all()
        
                

        # Mengonversi hasil query ke Pandas DataFrame
        df = pd.DataFrame([(data.id,data.part_number, data.asal, data.item.item, data.no_po, data.jumlah,data.hargaBeli, data.tanggal, data.letak.nama, data.keterangan) for data in query_result],
                        columns=['ID','Part Number', 'Asal', 'Nama Barang', 'No PO', 'Jumlah','harga beli', 'Tanggal', 'Letak', 'Keterangan'])

       
        col1,col2 = st.columns([9,1])
        with col1:
            id_ = df['ID']
            Id = st.multiselect("Silakan pilih data yang ingin kamu hapus berdasarkan ID : ", id_)
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
            sesi.query(BarangMasuk).filter(BarangMasuk.id.in_(Id)).delete(synchronize_session=False) 
            deleteItem(id=Id)
            sesi.commit()
            st.success("data telah dihapus")
        else:
            df.set_index(df.index + 1, inplace=True)
            st.write(df)
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