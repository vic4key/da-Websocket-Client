import certifi
import ssl
import socket
from OpenSSL import SSL
import os, sys, platform, socket
from OpenSSL import SSL, crypto
from hexdump import hexdump
from PyQt5.QtGui import QFont

def resources(file):
	try: cdir = sys._MEIPASS
	except: cdir = os.path.abspath(".")
	return os.path.join(cdir, os.path.join("resources", file))

def normalize_path(path):
	return path.replace("\\", "/").replace("/", os.path.sep)

def hex_view(data):
	return hexdump(data, "return")

def get_default_font():
	if platform.system() == "Windows": return QFont("Courier New", 9)
	else: return QFont("Courier New", 10)

def get_cert_chains(host, port=443):
	result = None
	s = None
	try:
		context = SSL.Context(SSL.SSLv23_METHOD)
		s = socket.create_connection((host, port))
		s = SSL.Connection(context, s)
		s.set_connect_state()
		s.set_tlsext_host_name(str.encode(host))
		s.sendall(str.encode("HEAD / HTTP/1.0\n\n"))
		certs = [crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
			for cert in s.get_peer_cert_chain()]
		result = b"".join(certs).decode("utf-8")
		s.shutdown()
	except Exception as e: print(e)
	if not s is None: s.close()
	return result
