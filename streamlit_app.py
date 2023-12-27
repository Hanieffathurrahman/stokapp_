import streamlit as st
from streamlit_option_menu import option_menu
st.set_page_config(layout="wide",page_title="Nito. Aplikasi Stok",page_icon="📦")


with st.sidebar:
    selected = option_menu(menu_title=None,
                        options=["Homepage","Barang Masuk", "Barang Keluar", "Persediaan","Perhatian ⚠️"],
                        icons=["house","box-arrow-in-right","box-arrow-right","boxes","exclamation-triangle-fill"],
                        menu_icon="cast",
                        orientation="vertikal",
                        styles={
                                "container": {"padding": "0!important", "background-color": "#0000"},
                                "icon": {"color": "white", "font-size": "15px"},
                                "nav-link": {
                                    "font-size": "15 px",
                                    "text-align": "left",
                                    "margin": "5px",
                                    "--hover-color": "#4c5154",
                                },
                                "nav-link-selected": {"background-color": "#3c3f45"},
            },)
    
#---------------------Homepage------------------------------
if selected == 'Homepage':
    from a.Homepage import main
    main()


#---------------------BARANG MASUK-----------------------------
if selected == 'Barang Masuk':
    from a.barang_masuk import main
    main()

#---------------------BARANG KELUAR----------------------------
if selected == 'Barang Keluar':
    from a.barang_keluar import main
    main()

#--------------------------------------------------------PERSEDIAAN BARANG---------------------------------------------------

if selected == 'Persediaan':
    from a.persediaan import main
    main()

if selected == 'Perhatian ⚠️':
    
    from a.tes import main
    main()