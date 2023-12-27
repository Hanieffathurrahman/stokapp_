from createdb import engine
from models import Base, BarangMasuk, BarangKeluar,  Item

print("creating table on database")
Base.metadata.create_all(bind=engine)