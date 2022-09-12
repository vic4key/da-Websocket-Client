import os
import jstyleson as json
from enum import Enum

import websocket, ssl
from websocket import ABNF

from urllib.parse import urlparse

from utils import *
from logger import WSHandler
from thread import StoppableThread

import plugin

DEFAULT_TIME_INTERVAL = 5
DEFAULT_TIME_OUT = 30
DEFAULT_DEBUG_TRACE = False
PREFS_FILE_NAME = normalize_path("preferences/prefs.json")

class icon_t(str, Enum):
	none = ""
	down = ":/icons/arrow-down.png"
	up   = ":/icons/arrow-up.png"

class color_t(str, Enum):
	# status
	success = "green"
	normal = "black"
	warn = "orange"
	error = "red"
	# color
	red = "red"
	orange = "orange"

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
	m_autoping = False
	m_ping_interval = DEFAULT_TIME_INTERVAL
	m_ping_timeout = DEFAULT_TIME_OUT
	m_ping_message = ""

	m_ws_threads = {}
	m_ws_temp_files = []

	def __init__(self, *args, **kwargs):
		pass

	def update_ui(self, update_values=False):
		assert False, "missing implementation"

	def log(self, text, color=color_t.normal, icon=icon_t.none):
		assert False, "missing implementation"

	def status(self, text, color=color_t.normal):
		assert False, "missing implementation"

	def prefs_get(self, name, default=""):
		parts = name.split(".")
		if len(parts) == 1:
			prefs = self.m_prefs
		elif len(parts) == 2:
			if parts[0] in self.m_prefs.keys():
				prefs = self.m_prefs[parts[0]]
				name = parts[1]
		else: assert False, "prefs get faied -> unsupported"
		return prefs[name] if name in prefs.keys() else default

	def prefs_set(self, name, value):
		parts = name.split(".")
		if len(parts) == 1:
			prefs = self.m_prefs
		elif len(parts) == 2:
			if not parts[0] in self.m_prefs.keys():
				self.m_prefs[parts[0]] = {}
			prefs = self.m_prefs[parts[0]]
			name = parts[1]
		else: assert False, "prefs set faied -> unsupported"
		prefs[name] = value

	def prefs_load_from_file(self):
		try:
			if os.path.exists(PREFS_FILE_NAME):
				with open(PREFS_FILE_NAME, "r+") as f:
					self.m_prefs = json.loads(f.read())
					# connection
					self.m_endpoint = self.prefs_get("endpoint").strip()
					self.m_timeout = self.prefs_get("timeout", DEFAULT_TIME_OUT)
					self.m_debug = self.prefs_get("show_debug_window", False)
					self.m_message = self.prefs_get("default_message")
					self.m_custom_header = self.prefs_get("default_custom_header", {})
					# auto ssl
					self.m_autossl = self.prefs_get("autossl", True)
					self.m_sslfile = self.prefs_get("sslfile").strip()
					self.m_sslfile = normalize_path(self.m_sslfile)
					# auto ping
					self.m_autoping = self.prefs_get("ping.enabled", False)
					self.m_ping_interval = self.prefs_get("ping.interval", DEFAULT_TIME_INTERVAL)
					self.m_ping_timeout = self.prefs_get("ping.timeout", DEFAULT_TIME_OUT)
					self.m_ping_message= self.prefs_get("ping.message")
					# others
					self.m_ws_codes = self.prefs_get("websocket_codes", {})
		except:
			self.status("Loading preferences file failed", color_t.error)
		self.update_ui(True)

	def prefs_save_to_file(self):
		# connection
		self.prefs_set("endpoint", self.m_endpoint)
		self.prefs_set("timeout", self.m_timeout)
		self.prefs_set("show_debug_window", self.m_debug)
		self.prefs_set("default_message", self.m_message)
		self.prefs_set("default_custom_header", self.m_custom_header)
		# auto ssl
		self.prefs_set("autossl", self.m_autossl)
		self.prefs_set("sslfile", self.m_sslfile)
		# auto ping
		self.prefs_set("ping.enabled", self.m_autoping)
		self.prefs_set("ping.interval", self.m_ping_interval)
		self.prefs_set("ping.timeout", self.m_ping_timeout)
		self.prefs_set("ping.message", self.m_ping_message)
		# save to file
		with open(PREFS_FILE_NAME, "w+") as f:
			f.write(json.dumps(self.m_prefs, indent=4))

	def remember_to_delete_temp_file(self, temp_file):
		self.m_ws_temp_files.append(temp_file)

	def stop_thread(self, ws):
		if ws in self.m_ws_threads.keys():
			self.m_ws_threads[ws].stop()
			del self.m_ws_threads[ws]

	def ws_spotcheck_params(self):
		return self.m_timeout > 0 and self.m_endpoint.startswith(("ws:", "wss:"))

	def ws_on_open(self, ws):
		self.m_ws = ws
		self.status("Opened", color_t.success)
		self.update_ui()
		for e in plugin.plugins(): e.on_open(e, ws)

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
		self.stop_thread(ws)
		self.m_ws = None
		self.update_ui()
		for e in plugin.plugins(): e.on_close(e, ws, close_status_code, close_msg)

	def ws_on_error(self, ws, error):
		self.m_ws = None
		self.status(str(error), color_t.error)
		self.update_ui()
		for e in plugin.plugins(): e.on_error(e, ws, error)
		if error: raise error

	def ws_on_ping(self, ws, message):
		for e in plugin.plugins(): e.on_ping(e, ws, message)

	def ws_on_pong(self, ws, message):
		for e in plugin.plugins(): e.on_pong(e, ws, message)

	def ws_on_data(self, ws, data, type, continuous):
		if type == ABNF.OPCODE_TEXT:
			self.log(data, color_t.red, icon_t.down)
		elif type == ABNF.OPCODE_BINARY:
			self.log(hex_view(data), color_t.red, icon_t.down)
		else:
			print("received data type did not support", ABNF.OPCODE_MAP.get(type))
		for e in plugin.plugins(): e.on_recv(e, ws, data, type, continuous)

	def ws_send(self, data, opcode=ABNF.OPCODE_TEXT):
		if self.ws_ready():
			self.m_ws.send(data, opcode)
			for e in plugin.plugins(): e.on_send(e, self.m_ws, data, opcode)

	def ws_ready(self):
		return not self.m_ws is None

	def ws_start(self, use_ssl):
		websocket.enableTrace(traceable=True, handler=WSHandler(self))
		websocket.setdefaulttimeout(self.m_timeout)

		if use_ssl: self.status("Initializing SSL connection ...", color_t.warn)

		ssl_opt = None
		if use_ssl: # websocket secure
			sslfile = ""
			try:
				# generate certificate for ssl connection
				if self.m_autossl:
					# get signed certificate from default ca trusted root certificates
					sslfile = ssl_default_ca_file = get_default_ca_trust_root_certificates()
					# get self-signed certificate chain from server
					url = urlparse(self.m_endpoint)
					ssl_self_signed_file = get_cert_chains_certificates(url.hostname, url.port or 443)
					self.remember_to_delete_temp_file(ssl_self_signed_file)
					# combine them all into one and save to a single file in temporary folder
					if os.path.exists(ssl_default_ca_file) and os.path.exists(ssl_self_signed_file):
						content = ""
						with open(ssl_default_ca_file, "r") as f:  content += f.read() + "\n"
						with open(ssl_self_signed_file, "r") as f: content += f.read() + "\n"
						sslfile = store_as_temporary_file(content.encode())
						self.remember_to_delete_temp_file(sslfile)
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
			on_ping=self.ws_on_ping,
			on_pong=self.ws_on_pong,
		)

		ping_interval = 0
		ping_timeout  = None
		ping_payload  = ""
		if self.m_autoping:
			ping_interval = self.m_ping_interval
			ping_timeout  = self.m_ping_timeout
			ping_payload  = self.m_ping_message

		def run(*args):
			try:
				ws.run_forever(
					sslopt=ssl_opt,
					ping_interval=ping_interval,
					ping_timeout=ping_timeout,
					ping_payload=ping_payload,
				)
			except Exception as e:
				ws.close()
				self.stop_thread(ws)

		self.m_ws_threads[ws] = StoppableThread(target=run)
		self.m_ws_threads[ws].start()

	def ws_close(self):
		if self.ws_ready():
			self.status("Closing connection ...", color_t.warn)
			self.m_ws.close()
			self.stop_thread(self.m_ws)
		self.status("Closed")

	def	ws_cleanup(self):
		self.ws_close()
		for ws in self.m_ws_threads.keys():
			ws.close()
			self.stop_thread(ws)
		for e in self.m_ws_temp_files:
			if os.path.exists(e):
				os.unlink(e)
