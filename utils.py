import os, sys, platform, socket, requests, math
from OpenSSL import SSL, crypto
from hexdump import hexdump
from datetime import datetime
from tempfile import gettempdir
from PyQt5.QtGui import QFont

def get_current_directory():
	result = ""
	try: result = sys._MEIPASS
	except: result = os.path.abspath(".")
	return normalize_path(result)

def resources(file):
	return os.path.join(get_current_directory(), os.path.join("resources", file))

def normalize_path(path):
	return path.replace("\\", "/").replace("/", os.path.sep)

def hex_view(data):
	return hexdump(data, "return")

def get_default_font():
	if platform.system() == "Windows": return QFont("Courier New", 9)
	else: return QFont("Courier New", 10)

def store_as_temporary_file(content):
	result = None
	try:
		t = datetime.now()
		tmp_file_name = t.strftime("%Y%m%d_%H%M%S") + f"_{t.microsecond}"
		tmp_file_path = os.path.join(gettempdir(), tmp_file_name)
		f = open(tmp_file_path, "wb") # TemporaryFile()
		f.write(content)
		f.close()
		result = f.name
	except Exception as e: print(e)
	return normalize_path(result)

def get_cert_chains_certificates(host, port=443):
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
		result = b"".join(certs)
		s.shutdown()
	except Exception as e: print(e)
	if not s is None: s.close()
	return normalize_path("" if result is None else store_as_temporary_file(result))

def get_default_ca_trust_root_certificates():
	cacert_path = os.path.join(get_current_directory(), "preferences", "cacert.pem")
	try:
		# read from exists ca-cert file
		if os.path.exists(cacert_path):
			with open(cacert_path, "r+") as f:
				if f.read().strip() != "":
					return cacert_path
		# CA certificates extracted from Mozilla
		response = requests.get("https://curl.se/ca/cacert.pem")
		if response.status_code == 200:
			with open(cacert_path, "w+", encoding="utf-8") as f: # store for using later
				f.write(response.text)
	except Exception as e: print(e)
	return cacert_path

def format_bytes(number, unit = 1024): # PyVutils.Bytes.format_bytes(...)
    e = 0
    l = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    if number > 0: e = int(math.log(number, unit))
    if e < len(l):
        s = ("%0.0f %s" if e == 0 else "%0.2f %s" ) % (number / unit**e, l[e])
    # else: s = "%0.2f 10^%d" % (float(number) / unit**e, e)
    return s
