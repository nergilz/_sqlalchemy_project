#  Внимание!!! при создании клиента нет проверок на корректный ввод
#  падает при несуществующем запросе, дополнить!
from socket import socket, AF_INET, SOCK_STREAM
import hmac

secret_key = b'secret_key'

def client_authenticate(connection, secret_key):
    message = connection.recv(32)
    hash = hmac.new(secret_key, message)
    digest = hash.digest()
    connection.send(digest)

def call_server(request):
    query = bytes(request, encoding='utf-8')
    sock.send(query)
    resp = sock.recv(16384)
    print('ответ сервера: ', resp.decode())
    sock.close()

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 9999))
client_authenticate(sock, secret_key)
print('начало работы client.py:')

while True:
    print('запрос данных по названию страны [1], запрос всех данных по фирме [2]:')
    req = input('>>>')
    req = str(req)
    if req == '1':
        request = input('введите название страны: ')
        request = '1'+request
        call_server(request)
    if req == '2':
        request = input('введите название фирмы-поставщика: ')
        request = '2'+request
        call_server(request)
    if req!='1' or req!='2': break
