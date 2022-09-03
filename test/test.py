import server.src as cshs
import ssl

# r = cshs.ReadCommand(cshs.Session(), 'server/ges/abc.txt')
# r.preform()
# print(r.data)
# 
# r = cshs.WriteCommand(cshs.Session(), 'server/ges/abc.txt', b"seg")
# r.preform()
# print(r.data)
# 
# r = cshs.RenameCommand(cshs.Session(), 'abd.txt', 'abs.txt')
# r.preform()
# print(r.data)

# r = cshs.CopyCommand(cshs.Session(), 'abs.txt', 'abd.txt')
# r.preform()
# print(r.data)
# 
# r = cshs.ReadCommand(cshs.Session(), 'server/connection.py')
# r.preform()
# print(r.data)

# r = cshs.CreateDirectoryCommand(cshs.Session(), 'server/ges')
# r.preform()
# print(r.data)

# r = cshs.ListDirectoryCommand(cshs.Session(), '')
# r.preform()
# print(r.data)
# cshs.set_verbose(False)
cshs.set_file_handler("server.log")
a = cshs.CSHServer("d:/", ('localhost', 8001), "users.json", "k", secure=("certificate.pem", 'key.pem', ssl.PROTOCOL_TLSv1), rate_limit=[(cshs.MINUTE, 100)], session_limit=20, session_expiration_delay=10)
a.start_server()
# a.create_user('admin', '2xwwtizu', 'a')
# a.create_user('lily.l.liller', '2xwwtizu', 'r')

# print(cshs.serialize({'command': 'L', 'username': 'admin', 'password': '2xwwtizu'}))

# print(cshs.serialize(r.data))
# print(cshs.deserialize(cshs.serialize(r.data)))

