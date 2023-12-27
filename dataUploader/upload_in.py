import streamlit as st 
import pandas as pd
from sqlalchemy.orm import Session
from module.createdb import engine
from module.models import BarangMasuk, Item, Letak
from datetime import datetime


"""def load_data(file_path):
    data = pd.read_csv(file_path)
    return data
"""
"""def display_data_by_input(datas, variableIn, inputVar):
    inputVar_lower = inputVar.lower() #=> konversi pembanding nama kolom selected jadi lower case
    if variableIn is None:
        st.warning("silahkan upload data")
    else:
        if len(variableIn) == 1:
            selected_column_lower = variableIn[0].lower() #=konversi nama kolom selected jadi lower case
            selected_column = variableIn[0]
            st.write(selected_column)  # Ambil nama kolom dari list variableIn
            if inputVar_lower == selected_column_lower:
                st.write(f"data kolom {inputVar}")
                dt = datas[selected_column]
                
                st.dataframe(dt)
            else:
                st.warning(f"kolom ini harus di isi dengan  {inputVar} bukan {selected_column_lower} ")

        elif len(variableIn) == 0: 
            st.toast(f"harap masukan input data {inputVar_lower} !")
        else:
            st.error("masukan 1 input saja sesuai dengan nama input masing masing !")

    
def data_show(datas,part_number,asal,item,po,jumlah,harga,tanggal,letak,keterangan):
    display_data_by_input(datas,variableIn=part_number,inputVar='part number')
    display_data_by_input(datas,variableIn=asal,inputVar='asal ')
    display_data_by_input(datas,variableIn=item,inputVar='item')
    display_data_by_input(datas,variableIn=po,inputVar='po')
    display_data_by_input(datas,variableIn=jumlah,inputVar='JUMLAH')
    display_data_by_input(datas,variableIn=harga,inputVar='HARGA')
    display_data_by_input(datas,variableIn=tanggal,inputVar='TANGGAL')
    display_data_by_input(datas,variableIn=letak,inputVar='letak')
    display_data_by_input(datas,variableIn=keterangan,inputVar='KETERANGAN')
    if None in [part_number, asal, item, po, jumlah, harga, tanggal, letak, keterangan]:
        st.warning("Data tidak valid")
"""

def inserting_data(file):
    sesi = Session(bind=engine)
    try:
        df = file
        for index, row in df.iterrows():
            #st.write(f"Jumlah dari DataFrame: {row['jumlah']}")
            jumlah_value = row["jumlah"]
            if pd.isna(jumlah_value):
                jumlah_value = 0

            #convert null value into 0
            item_value = str(row["item"]) if not pd.isna(row["item"]) else "0"
            letak_value = str(row["letak"]) if not pd.isna(row["letak"]) else "0"

            #kodisi item and letak is not in database
            if not sesi.query(Item).filter(Item.item == item_value).first() and not sesi.query(Letak.nama == letak_value):
                item_baru = Item(item = item_value)
                letak_baru = Letak(nama = letak_value)
                barmas = BarangMasuk(
                    part_number=row["part number"],   
                    asal=row["asal "],  
                    item_id=item_baru,
                    item=item_baru,
                    no_po=row["po"],  
                    hargaBeli=row["harga"],  
                    jumlah=jumlah_value,  
                    tanggal = datetime.strptime(row["tanggal"], "%m/%d/%Y"), 
                    letak_id=letak_baru,
                    letak=letak_baru,
                    keterangan=row["keterangan"]  
                )
                
                sesi.add_all([item_baru, letak_baru, barmas])

            #kondisi 2 : item == item baru dan letak == letak ==> ketika item tidak ada dalam database sedangkan letak ada dalam database
            elif not sesi.query(Item).filter(Item.item == item_value).first():
                    letak_terpilih = sesi.query(Letak).filter(Letak.nama == letak_value).first()
                    item_baru = Item(item = item_value)       
                    barangMasuk = BarangMasuk(
                        part_number=row["part number"],   
                        asal=row["asal "],  
                        item_id=item_baru,
                        item=item_baru,
                        no_po=row["po"],  
                        hargaBeli=row["harga"],  
                        jumlah=jumlah_value,  
                        tanggal = datetime.strptime(row["tanggal"], "%m/%d/%Y"), 
                        letak_id=letak_terpilih,
                        letak=letak_terpilih,
                        keterangan=row["keterangan"]  
                    )
                    
                    sesi.add_all([item_baru,barangMasuk])
                    sesi.commit()

            elif not sesi.query(Letak).filter(Letak.nama == letak_value).first():
                    item_terpilih = sesi.query(Item).filter(Item.item == item_value).first()
                    letak_baru = Letak(nama = letak_value)
                    barangMasuk = BarangMasuk(
                        part_number=row["part number"],   
                        asal=row["asal "],  
                        item_id=item_terpilih,
                        item=item_terpilih,
                        no_po=row["po"],  
                        hargaBeli=row["harga"],  
                        jumlah=jumlah_value,  
                        tanggal = datetime.strptime(row["tanggal"], "%m/%d/%Y"), 
                        letak_id=letak_baru,
                        letak=letak_baru,
                        keterangan=row["keterangan"]  
                    )
                   
                    sesi.add_all([letak_baru,barangMasuk])
                    sesi.commit()

            #kondisi 4 
            else:
                #add barang masuk if item available in item table
                part_number = row["part number"]
                item_terpilih = sesi.query(Item).filter(Item.item == item_value).first()
                letak_terpilih = sesi.query(Letak).filter(Letak.nama == letak_value).first()
                barangMasuk = BarangMasuk(
                    part_number=row["part number"],   
                    asal=row["asal "],  
                    item_id=item_terpilih,
                    item=item_terpilih,
                    no_po=row["po"],  
                    hargaBeli=row["harga"],  
                    jumlah=jumlah_value,  
                    tanggal = datetime.strptime(row["tanggal"], "%m/%d/%Y"), 
                    letak_id=letak_terpilih,
                    letak=letak_terpilih,
                    keterangan=row["keterangan"]  
                )
                sesi.add(barangMasuk)
                sesi.commit()
          
        sesi.commit()
    except Exception as e:
        st.write(f" Error : {e}")
        import traceback
        traceback.print_exc()

        sesi.rollback()
    finally:
        sesi.close()





    



def main():
    file_in = st.file_uploader("masukan file barang masuk yang sudah ada!")
    """df = pd.DataFrame(file_in)
    df = df.to_sql(name="datas", con=engine, if_exists=)
    with engine.connect() as conn:
        conn.execute(text('select CustomerId from datas')).fetchall()"""

    if file_in:
        datas = pd.read_csv(file_in,sep=';')
        st.session_state.upload = datas
        st.success("data telah ditambah")
        st.dataframe(st.session_state.upload.head())
        
        data = datas.columns.tolist()
        st.write(data)
        col1, col2 = st.columns(2)
        with col1:
            part_number = st.multiselect("pilih data part_number ",datas.columns,key="par_number")
            asal = st.multiselect("pilih data asal",datas.columns, key="asal")
            item = st.multiselect("pilih data item",datas.columns,key="item" )
            po  = st.multiselect("pilih data po",datas.columns,key="po" )
            
        with col2:
            jumlah = st.multiselect("pilih data part_number ",datas.columns,key="jumlah")
            harga = st.multiselect("pilih data part_number ",datas.columns,key="harga")
            tanggal = st.multiselect("pilih data part_number ",datas.columns,key="tanggal")
            letak = st.multiselect("pilih data part_number ",datas.columns,key="letak")
            keterangan = st.multiselect("pilih data part_number ",datas.columns,key="keterangan")
        
        st.divider()
        data_low = datas.rename(columns=lambda x: x.lower())
        inserting_data(data_low)
        st.write(data_low)
        #data_show(datas=datas,part_number=part_number,asal=asal,item=item,po=po,jumlah=jumlah,harga=harga,tanggal=tanggal,letak=letak,keterangan=keterangan)
            


   

        
    """     #st.dataframe(datas[[col]])
    if len(part_number) == 1:
        for col in part_number:
            if set(part_number) == {'PART NUMBER'}:
                st.write(f"data kolom {col}")
                dt = datas[part_number]
                st.dataframe(dt)
            else: 
                st.warning(f"data {col} tidak sesuai untuk input ini ")
    elif len(part_number) == 0: 
        st.warning("harap masukan input data !")
    else:
        st.error("masukan 1 input saja sesuai dengan nama input masing masing !")  """

        


if __name__=="__main__":
    main()   