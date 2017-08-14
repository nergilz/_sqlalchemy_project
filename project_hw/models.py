#import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError
from socket import socket, AF_INET, SOCK_STREAM
import hmac
import os
import sys

Base = declarative_base()

class Supplier(Base):
    """class Supplier создание талицы поставщиков"""
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    def __str__(self):
        return self.name

    def __eq__(self, test):
        return self.name == test.name and self.email == test.email


class Product(Base):
    """class Supplier создание талицы товаров"""
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    count = Column(Integer)
    link_id = Column(ForeignKey('supplier.id'))

    def __str__(self):
        return self.name


class Foodstuff(Base):
    """class Supplier создание талицы продуктов"""
    __tablename__ = 'foodstuff'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    count = Column(Integer)
    country = Column(String)
    shelf_life = Column(String)
    link_id = Column(ForeignKey('supplier.id'))

    def __str__(self):
        return self.name


class WrongObjectError(UnmappedInstanceError):
    """класс Исключение, вызовем когда из базы пытаемся получить то, чего в ней нет"""
    def __str__(self):
        return '*класс "Shop" может работать только с фирмами, товарами и продуктами*'

class ObjectNotInLibrary(Exception):
    """класс Исключение. Когда хотим изменить или удалить объект, которого нет в базе"""
    def __str__(self):
        return 'объект не принадлежит базе'


class Shop:
    """class Shop: интерфейс для работы с БД магазина \shop_base.db\ """
    def __init__(self, name):
        """создание магазина"""
        self.engine = create_engine('sqlite:///{}'.format(name), echo=False)
        self._get_session()
        #self.create_new()

    def _get_session(self):
        """создание сессии с БД"""
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def _del_model(self, session, model_for_del):
        """удаление данных о модели"""
        model = session.query(model_for_del).order_by(model_for_del.id)
        for mod in model:
            session.delete(mod)
        session.commit()
        session.close()

    def create_new(self):
        """создание новой библеотеки, удаление данных из БД"""
        Base.metadata.create_all(self.engine)
        session = self._get_session()
        self._del_model(session, Supplier)
        self._del_model(session, Product)
        self._del_model(session, Foodstuff)
        session.close()

    def add_supplier(self, name_new, email_new):
        """добавление данных о поставщике"""
        session = self._get_session()
        new_supplier = Supplier(name=name_new, email=email_new)
        session.add(new_supplier)
        session.commit()
        session.close()

    def add_product(self, name, price, count, link_id):
        """добавление данных о товаре"""
        session = self._get_session()
        new_product = Product(name=name, price=price, count=count, link_id=link_id)
        session.add(new_product)
        session.commit()
        session.close()

    def add_foodstuff(self, name, price, count, country, shelf_life, link_id):
        """добавление данных о продукте"""
        session = self._get_session()
        new_foodstuff = Foodstuff(name=name, price=price, count=count,
                                  country=country, shelf_life=shelf_life, link_id=link_id)
        session.add(new_foodstuff)
        session.commit()
        session.close()

    def get_supplier(self):
        """все поставщики"""
        session = self._get_session()
        supp = session.query(Supplier.name, Supplier.email).\
                             order_by(Supplier.id)
        session.commit()
        session.close()
        return supp

    def get_product(self):
        """все товары"""
        session = self._get_session()
        prod = session.query(Product.name, Product.price, Product.count, Product.link_id).\
                             order_by(Product.id)
        session.commit()
        session.close()
        return prod

    def get_foodstuff(self):
        """все продукты"""
        session = self._get_session()
        foods = session.query(Foodstuff.name, Foodstuff.country, Foodstuff.count, Foodstuff.price, Foodstuff.shelf_life, Foodstuff.link_id).\
                              order_by(Foodstuff.id)
        session.commit()
        session.close()
        return foods

    def get_country(self, _query):
        """показывает все данные о продукте из одной таблици по названию страны"""
        session = self._get_session()
        q = session.query(Foodstuff.name, Foodstuff.country, Foodstuff.count, Foodstuff.price, Foodstuff.shelf_life, Foodstuff.link_id).\
                          filter(_query == Foodstuff.country).all()
        session.commit()
        session.close()
        return q

    def get_supp(self, firm):
        """показывает данные о фирме-поставщике по названию"""
        session = self._get_session()
        q = session.query(Supplier.name, Supplier.email).filter(firm == Supplier.name).all()
        session.commit()
        session.close()
        return q

    def get_supp_prod(self):
        """все данные поставщик -> товар"""
        session = self._get_session()
        q = session.query(Supplier.name, Product.name, Product.price, Product.count).\
                          join(Product, Supplier.id==Product.link_id).all()
        session.commit()
        session.close()
        return q

    def get_supp_all(self, firm):
        """все данные поставщик -> товары, продукты, по названию фирмы"""
        session = self._get_session()
        q = session.query(Supplier.name, Product.name, Product.price, Product.count,
                          Foodstuff.name, Foodstuff.price, Foodstuff.count, Foodstuff.country, Foodstuff.shelf_life).\
                          filter(firm == Supplier.name).order_by(Supplier.id).\
                          join(Product, Supplier.id == Product.link_id).\
                          join(Foodstuff, Supplier.id == Foodstuff.link_id).all()
        session.commit()
        session.close()
        return q

    def server_mode(self):
        """запускает режим сервера"""
        secret_key = b'secret_key'

        def server_authenticate(connection, secret_key):
            message = os.urandom(32)
            connection.send(message)
            hash = hmac.new(secret_key, message)
            digest = hash.digest()
            response = connection.recv(len(digest))
            return hmac.compare_digest(digest, response)

        def echo_handler(client_sock):
            if not server_authenticate(client_sock, secret_key):
                client_sock.close()
                return
            while True:
                msg = client_sock.recv(16384)
                if not msg:
                    break
                else:
                    request = msg.decode()
                    req = request[0]
                    request = request[1:]
                    if req == '1':
                        query = self.get_country(request)
                    if req == '2':
                        query = self.get_supp_all(request)
                    s = ''
                    for i in query:
                        i = str(i)
                        s = s + i
                    sb = bytes(s, encoding='utf-8')
                    client_sock.sendall(sb)

        def echo_server(address):
            sock = socket(AF_INET, SOCK_STREAM)
            sock.bind(address)
            sock.listen(5)
            while True:
                conn, addr = sock.accept()
                echo_handler(conn)
            
        echo_server(('', 9999))

