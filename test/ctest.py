# import server as cshs
# import socket, ssl
# 
# HOST = 'localhost'  # The server's hostname or IP address
# PORT = 8001        # The port used by the server
# 
# #for i in range(102):
# while True:
#     a = eval(input())
#     with ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), ssl_version=ssl.PROTOCOL_TLSv1) as s:
#         s.connect((HOST, PORT))
#         data = cshs.serialize(a)
#         s.sendall(b'CSH' + int.to_bytes(len(data), 4, 'little') + data)
#         s.recv(3)
#         l = int.from_bytes(s.recv(4), 'little')
#         print(cshs.deserialize(s.recv(l))) 
# 

import client as csh
# c = csh.Client(("localhost", 8001), True)
# print(c.status())
# print(c)
# c.login("admin", "2xwwtizu")
# print(c.read('./hello.c'))
# # print(c.exists('hello.c'))
# # c.write('hello.c', b"""#include <stdio.h>
# # int main() {
# #     printf("Hello, world!");
# # }""")
# c.logout()

with csh.Client(("localhost", 8001), True) as client:
    client.status()
    client.login("admin", "2xwwtizu")
    print(client.read('./hello.c'))
# a = csh.AdminClient(("localhost", 8001), "admin", True)
# print(a.status())
# print(a.all_users("2xwwtizu"))
# print(a.get_user("2xwwtizu", "admin"))
# print(a.backup("2xwwtizu", 'backups'))
