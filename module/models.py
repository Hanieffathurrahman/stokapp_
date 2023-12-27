from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

#class Base = Declarative base
class Base(DeclarativeBase):
    pass

class BarangMasuk(Base):
    __tablename__="barang_masuk"
    id = Column(Integer,primary_key=True, autoincrement= True)
    part_number = Column(String(25), nullable=False)
    asal = Column(String)
    item_id= Column(Integer, ForeignKey("item.id"))
    item = relationship("Item",back_populates='barmas')
    no_po = Column(String)
    jumlah = Column(Integer)
    hargaBeli= Column(Integer)
    tanggal = Column(DateTime)
    letak_id= Column(String, ForeignKey('letak.id'))
    letak = relationship("Letak", back_populates='barang_masuk')
    keterangan = Column(String)
    

class BarangKeluar(Base):
    __tablename__="barang_keluar"
    id = Column(Integer,primary_key=True, autoincrement= True)
    part_number = Column(String(25), nullable=False)
    itemNumber = Column(String)
    tujuan = Column(String)
    item_id= Column(Integer, ForeignKey("item.id"))
    item = relationship("Item",back_populates='barkel')
    jumlah = Column(Integer)
    hargaJual = Column(Integer)
    tanggal = Column(DateTime)
    letak_id= Column(String, ForeignKey('letak.id'))
    letak = relationship("Letak", back_populates='barang_keluar')
    no_inv = Column(String)
    no_jalan = Column(String)
    keterangan = Column(String)


class Item(Base):
    __tablename__='item'
    id = Column(Integer, primary_key=True)
    item = Column(String)
    barmas = relationship("BarangMasuk", back_populates='item')
    barkel = relationship("BarangKeluar", back_populates='item')
    
    
class Letak(Base):
    __tablename__='letak'
    id=Column(Integer, primary_key=True)
    nama=Column(String)
    barang_masuk = relationship("BarangMasuk", back_populates='letak')
    barang_keluar = relationship("BarangKeluar", back_populates='letak')

