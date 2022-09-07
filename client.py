import os
import jstyleson as json
from enum import Enum

import websocket, ssl
from websocket import ABNF

from urllib.parse import urlparse

from utils import *
from thread import StoppableThread

DEFAULT_TIME_OUT = 30
DEFAULT_DEBUG_TRACE = False
PREFS_FILE_NAME = normalize_path("preferences/prefs.json")

class color_t(str, Enum):
	# status
	success = "green"
	normal = "black"
	warn = "orange"
	error = "red"
	# color
	red = "red"
	green = "green"

class data_t(int, Enum):
	text = 0
	binary = 1

class WSClient:
	""" Websocket Client """

	m_prefs = {}

	m_ws = None
	m_ws_codes = {}
	m_endpoint = ""
	m_message = ""
	m_sslfile = ""
	m_autossl = True
	m_debug = DEFAULT_DEBUG_TRACE
	m_timeout = DEFAULT_TIME_OUT
	m_custom_header = {}

	m_ws_threads = {}

	def __init__(self, *args, **kwargs):
		pass

	def update_ui(self, update_values=False):
		assert False, "missing implementation"

	def log(self, text, color=color_t.normal):
		assert False, "missing implementation"

	def status(self, text, color=color_t.normal):
		assert False, "missing implementation"

	def prefs_get(self, name, default=""):
		return self.m_prefs[name] if name in self.m_prefs.keys() else default

	def prefs_set(self, name, value):
		self.m_prefs[name] = value

	def prefs_load_from_file(self):
		try:
			if os.path.exists(PREFS_FILE_NAME):
				with open(PREFS_FILE_NAME, "r+") as f:
					self.m_prefs = json.loads(f.read())
					self.m_timeout = self.prefs_get("timeout", DEFAULT_TIME_OUT)
					self.m_endpoint = self.prefs_get("endpoint").strip()
					self.m_debug = self.prefs_get("debug_trace", False)
					self.m_message = self.prefs_get("default_message")
					self.m_ws_codes = self.prefs_get("websocket_codes", {})
					self.m_custom_header = self.prefs_get("default_custom_header", {})
					self.m_autossl = self.prefs_get("autossl", True)
					self.m_sslfile = self.prefs_get("sslfile").strip()
					self.m_sslfile = normalize_path(self.m_sslfile)
		except:
			self.status("Loading preferences file failed", color_t.error)
		self.update_ui(True)

	def prefs_save_to_file(self):
		self.prefs_set("endpoint", self.m_endpoint)
		self.prefs_set("timeout", self.m_timeout)
		self.prefs_set("autossl", self.m_autossl)
		self.prefs_set("sslfile", self.m_sslfile)
		self.prefs_set("debug_trace", self.m_debug)
		self.prefs_set("default_message", self.m_message)
		self.prefs_set("default_custom_header", self.m_custom_header)
		with open(PREFS_FILE_NAME, "w+") as f:
			f.write(json.dumps(self.m_prefs, indent=4))

	def spotcheck_params(self):
		return self.m_timeout > 0 and self.m_endpoint.startswith(("ws:", "wss:"))

	def ws_stop_thread(self, ws):
		if ws in self.m_ws_threads.keys():
			self.m_ws_threads[ws].stop()
			del self.m_ws_threads[ws]

	def ws_on_open(self, ws):
		self.m_ws = ws
		self.status("Opened", color_t.success)
		self.update_ui()

	def ws_on_close(self, ws, close_status_code, close_msg):
		text = "Closed"
		color = color_t.normal
		if close_msg:
			text = close_msg
			color = color_t.error
		elif close_status_code:
			msg = None
			ws_close_codes = self.m_ws_codes.get("close")
			if ws_close_codes: msg = ws_close_codes.get(str(close_status_code))
			text = f"Close code {close_status_code}" if msg is None else msg
			color = color_t.error
		if self.ws_ready(): self.status(text, color)
		self.ws_stop_thread(ws)
		self.m_ws = None
		self.update_ui()

	def ws_on_error(self, ws, error):
		self.m_ws = None
		self.status(str(error), color_t.error)
		self.update_ui()
		if error: raise error

	def ws_on_data(self, ws, data, type, continuous):
		if type == ABNF.OPCODE_TEXT:
			self.log(data, color_t.red)
		elif type == ABNF.OPCODE_BINARY:
			self.log(hex_view(data), color_t.red)
		else:
			print("received data type did not support", ABNF.OPCODE_MAP.get(type))

	def ws_send(self, data, opcode=ABNF.OPCODE_TEXT):
		if self.ws_ready(): self.m_ws.send(data, opcode)

	def ws_ready(self):
		return not self.m_ws is None

	def ws_start(self, use_ssl):
		websocket.enableTrace(self.m_debug)
		websocket.setdefaulttimeout(self.m_timeout)

		if use_ssl: self.status("Initializing SSL connection ...", color_t.warn)

		ssl_opt = None
		if use_ssl: # websocket secure
			sslfile = ""
			try:
				# generate certificate for ssl connection
				if self.m_autossl:
					# get signed certificate from default ca trusted root certificates
					ssl_default_ca_file = get_default_ca_trust_root_certificates()
					# get self-signed certificate chain from server
					url = urlparse(self.m_endpoint)
					ssl_self_signed_file = get_cert_chains_certificates(url.hostname, url.port or 443)
					# combine them all into one
					content = ""
					with open(ssl_default_ca_file, "r") as f: content += f.read()
					content += "\n"
					with open(ssl_self_signed_file, "r") as f: content += f.read()
					# save to a single file in temporary folder
					sslfile = store_as_temporary_file(content.encode())
				elif os.path.exists(self.m_sslfile): # get from specified cert file
					sslfile = self.m_sslfile
				# create ssl context
				ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				ssl_context.load_verify_locations(sslfile)
				ssl_opt = {"context": ssl_context}
			except Exception as e:
				self.status(str(e), color_t.error)
				return

		self.status("Connecting to server ...", color_t.warn)

		ws = websocket.WebSocketApp(
			self.m_endpoint,
			header=self.m_custom_header,
			on_open=self.ws_on_open,
			on_close=self.ws_on_close,
			on_data=self.ws_on_data,
			on_error=self.ws_on_error,
		)

		def run(*args):
			try:
				ws.run_forever(sslopt=ssl_opt)
			except Exception as e:
				ws.close()
				self.ws_stop_thread(ws)

		self.m_ws_threads[ws] = StoppableThread(target=run)
		self.m_ws_threads[ws].start()

	def ws_close(self):
		if self.ws_ready():
			self.status("Closing connection ...", color_t.warn)
			self.m_ws.close()
			self.ws_stop_thread(self.m_ws)
		self.status("Closed")
