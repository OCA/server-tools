"""Basic example script you can use to test your own models for real."""

from xmlrpc import client

HOST = "127.0.0.1"
PORT = 8069
DB_NAME = "odoodb"

url = "http://%s:%d/xmlrpc/2/" % (HOST, PORT)
xmlrpc_common = client.ServerProxy(url + "common")
xmlrpc_db = client.ServerProxy(url + "db")
xmlrpc_object = client.ServerProxy(url + "object")

uid = xmlrpc_common.login(DB_NAME, "admin", "admin")
res = xmlrpc_object.execute(DB_NAME, uid, "admin", "res.partner", "search", [])
