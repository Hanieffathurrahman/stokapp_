from sqlalchemy.orm import Session
import streamlit as st
from module.createdb import engine
import pandas as pd
sesi = Session(bind=engine)
from a.persediaan import stok

def main():
    st.warning("Harap dibaca")
    st.markdown(
        """-----------------------------------------------------------------------------------------------------------------------
            hai kembali bertemu ! \n
           Aplikasi yang sekarang ini belum fix yak masih tahap uji coba fitur uploaded data di barang masuk. 
           -----------------------------------------------------------------------------------------------------------------------
           cara kerja nya: 
           siapin file csv yang berisikan data barang masuk, pastikan nama dan urutan kolom sesuai dengan formatnya. 
           berikut format urutan dan nama kolom 
           1. part number       | 5. jumlah         | 9. keterangan
           2. asal              | 6. harga
           3. item              | 7. tanggal
           4. po                | 8. letak

           setelah filenya berbentuk csv dan format tablenya sesuai tinggal upload dan submit. secara otomatis data barang masuk 
           akan di update 

           ## roadmap apps
           ----------> uploader data masuk -----------> get data from barang masuk and barang keluar to persediaan -------->
           |________> uploader data keluar -----------> delete data functional for data masuk and barang keluar ---> edit fiture 

           what is done ? 
           --> uploader data masuk [Done]     [(>=_=>)]
           --> barang masuk to persediaan [Done]  [(>=_=>)]
           --> tampilkan semua barang yg ada di persediaan [Done]   [(>=_=>)]
           --> tampilkan data masuk [Done]   [(>=_=>)]
           --> uploader data keluar [Done]   [(>=_=>)]
           --> tampilkan data keluar [Done]   [(>=_=>)]

                                                            `[ DONE ] C(=_=)D +
                                                                      /\   /\/
                                                                      \ | |  
                                                                      * / \\ 
           ---------------------------------------------------------------
           
        """
    )
    
    
if __name__ == "__main__":
    main()
