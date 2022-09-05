import os, sys, platform
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
