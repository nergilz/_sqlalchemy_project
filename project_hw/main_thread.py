#  запись результата запросов потоками в .txt файлы и запуск сервера
from models import Shop
from fill_db import fill_db
import os
import json
import threading
import sys

DIR = 'save_query_files'
shop = Shop('shop_base.db')  # имя бд sqlite
shop.create_new()
fill_db('shop_base.db')  # автозаполнение бд


class WriteStream(threading.Thread):
    def __init__(self, name_file, query):
        super().__init__()
        self.name_file = name_file
        self.query = query

    def run(self):
        result = []
        for i in self.query:
            result.append(i)
        with open(os.path.join(DIR, self.name_file), 'w', encoding='UTF-8') as f:
                json.dump(result, f)


class ReadStream(threading.Thread):
    def __init__(self, name_file):
        super().__init__()
        self.name_file = name_file

    def run(self):
        with open(os.path.join(DIR, self.name_file), 'r', encoding='UTF-8') as f:
            read_data = json.load(f)
        for i in read_data:
            print(i)


#  запросы в базу данных
query1 = shop.get_supplier()   # все поставщики
query2 = shop.get_product()    # все товары
query3 = shop.get_foodstuff()  # все продукты
query4 = shop.get_country('chili')  # запрос: страна -> все продукты из этой страны
query5 = shop.get_supp_all('jungle')  # запрос: поставщик -> информация из всех таблиц
#  потоки через классы -> запись
stream1 = WriteStream('get_supplier.json', query1)
stream2 = WriteStream('get_product.json', query2)
stream3 = WriteStream('get_foodstuff.json', query3)
stream4 = WriteStream('get_country.json', query4)
stream5 = WriteStream('get_supp_all.json', query5)
#  потоки через классы -> чтение
stream6 = ReadStream('get_supplier.json')
stream7 = ReadStream('get_product.json')
stream8 = ReadStream('get_foodstuff.json')
stream9 = ReadStream('get_country.json')
stream10 = ReadStream('get_supp_all.json')
# запуск потоков
stream1.start()
stream2.start()
stream3.start()
stream4.start()
stream5.start()
#  чтение с ожиданием
stream6.start()
stream6.join()
stream7.start()
stream7.join()
stream8.start()
stream8.join()
stream9.start()
stream9.join()
stream10.start()
stream10.join()

#  запуск сервера, для работы с сервером запустить client.py
server = Shop('shop_base.db')
server.server_mode()

sys.exit(0)
raise SystemExit(0)
