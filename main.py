import os

from PyQt5 import uic as UiLoader
from PyQt5.QtGui import QColor, QIcon, QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMessageBox

from utils import *
from client import *
from picker import Picker
from about import AboutDlg

class Window(QMainWindow, WSClient):

	m_signal_update_ui = Signal(bool)
	m_signal_status = Signal(str, color_t)
	m_signal_log = Signal(str, color_t, icon_t)
	m_signal_debug = Signal(str)

	def __init__(self, app):
		super(Window, self).__init__()
		super(WSClient, self).__init__()
		self.app = app
		self.setup_ui()
		return

	def setup_ui(self):
		# load ui from file
		UiLoader.loadUi(resources("main.ui"), self)
		# signal & slot
		self.actionSave.triggered.connect(self.on_triggered_menu_file_save)
		self.actionExit.triggered.connect(self.on_triggered_menu_file_exit)
		self.actionAbout.triggered.connect(self.on_triggered_menu_help_about)
		self.txt_endpoint.textChanged.connect(self.on_changed_endpoint)
		self.txt_timeout.textChanged.connect(self.on_changed_timeout)
		self.btn_connect.clicked.connect(self.on_clicked_button_connect)
		self.chk_auto_use_ssl_chains.clicked.connect(self.on_clicked_auto_use_ssl_chains)
		self.btn_browse_ssl_file.clicked.connect(self.on_clicked_button_browse_ssl_file)
		self.chk_ping.clicked.connect(self.on_clicked_auto_ping)
		self.txt_ping_interval.textChanged.connect(self.on_changed_ping_interval)
		self.txt_ping_timeout.textChanged.connect(self.on_changed_ping_timeout)
		self.txt_ping_message.textChanged.connect(self.on_changed_ping_message)
		self.btn_ping_message.clicked.connect(self.on_clicked_button_ping_send_message)
		self.txt_message.textChanged.connect(self.on_changed_message)
		self.btn_send_message.clicked.connect(self.on_clicked_button_send_message)
		self.btn_clear_list_log.clicked.connect(self.on_clicked_button_clear_list_log)
		self.btn_save_list_log.clicked.connect(self.on_clicked_button_save_list_log)
		self.btn_clear_list_debug.clicked.connect(self.on_clicked_button_clear_list_debug)
		self.btn_save_list_debug.clicked.connect(self.on_clicked_button_save_list_debug)
		self.m_signal_update_ui.connect(self.slot_update_ui)
		self.m_signal_status.connect(self.slot_status)
		self.m_signal_log.connect(self.slot_log)
		self.m_signal_debug.connect(self.slot_debug)
		# others
		self.txt_ping_message.setFont(get_default_font())
		self.txt_message.setFont(get_default_font())
		self.list_log.setIconSize(QSize(16, 16))
		# load prefs from file
		self.prefs_load_from_file()
		# hide the debug window as default
		if not self.m_debug:
			w, _ = self.splitter.sizes()
			self.splitter.setSizes([w, 0])
		# others
		self.txt_endpoint.setCursorPosition(0)

	def showEvent(self, a0) -> None:
		super(Window, self).showEvent(a0)
		for e in plugin.plugins():
			self.menuPlugins.addAction(e.name)

	def is_default_style(self):
		return QApplication.instance().style().metaObject().className() == "QWindowsVistaStyle"

	def closeEvent(self, event):
		self.ws_cleanup()
		event.accept()

	def debug(self, text):
		if self.m_debug: self.m_signal_debug.emit(text)

	@Slot(str)
	def slot_debug(self, text):
		item = QListWidgetItem(text)
		item.setFont(get_default_font())
		item.setData(Qt.UserRole, "")
		self.list_debug.addItem(item)
		self.list_debug.scrollToBottom()

	def log(self, text, color=color_t.normal, icon=icon_t.none):
		self.m_signal_log.emit(text, color, icon)

	@Slot(str, color_t, icon_t)
	def slot_log(self, text, color=color_t.normal, icon=icon_t.none):
		item = QListWidgetItem(text)
		item.setFont(get_default_font())
		item.setForeground(QColor(color))
		data = ""
		if icon is not icon_t.none:
			item.setIcon(QIcon(icon))
			if icon is icon_t.down: data = "[RECV]"
			elif icon is icon_t.up: data = "[SEND]"
		item.setData(Qt.UserRole, data)
		self.list_log.addItem(item)
		self.list_log.scrollToBottom()

	def status(self, text, color=color_t.normal):
		self.m_signal_status.emit(text, color)

	@Slot(str, color_t)
	def slot_status(self, text, color=color_t.normal):
		palette = self.lbl_status.palette()
		palette.setColor(QPalette.WindowText, QColor(color))
		self.lbl_status.setPalette(palette)
		self.lbl_status.setToolTip(text)
		self.lbl_status.setText(text)
		self.lbl_status.repaint()

	def update_ui(self, update_values=False):
		self.m_signal_update_ui.emit(update_values)

	@Slot(bool)
	def slot_update_ui(self, update_values=False):
		if update_values:
			self.txt_endpoint.setText(str(self.m_endpoint))
			self.chk_auto_use_ssl_chains.setChecked(self.m_autossl)
			self.txt_ssl_file_path.setText(os.path.basename(self.m_sslfile))
			self.txt_ssl_file_path.setToolTip(self.m_sslfile)
			self.txt_timeout.setText(str(self.m_timeout))
			self.txt_message.setPlainText(self.m_message)
			self.chk_ping.setChecked(self.m_autoping)
			self.txt_ping_interval.setText(str(self.m_ping_interval))
			self.txt_ping_timeout.setText(str(self.m_ping_timeout))
			self.txt_ping_message.setPlainText(self.m_ping_message)
		self.txt_endpoint.setEnabled(not self.ws_ready())
		self.txt_timeout.setEnabled(not self.ws_ready())
		self.chk_auto_use_ssl_chains.setEnabled(not self.ws_ready())
		self.txt_ssl_file_path.setEnabled(not (self.m_autossl or self.ws_ready()))
		self.btn_browse_ssl_file.setEnabled(not (self.m_autossl or self.ws_ready()))
		self.btn_send_message.setEnabled(self.ws_ready())
		self.btn_connect.setText("DISCONNECT" if self.ws_ready() else "CONNECT")
		self.chk_ping.setEnabled(not self.ws_ready())
		self.txt_ping_interval.setEnabled(self.m_autoping and not self.ws_ready())
		self.txt_ping_timeout.setEnabled(self.m_autoping and not self.ws_ready())
		self.btn_ping_message.setEnabled(self.ws_ready())
	
	def selected_send_data_type(self):
		return abs(self.buttonGroup_message.checkedId()) - 2

	def selected_log_type(self):
		return abs(self.buttonGroup_log.checkedId()) - 2

	def on_triggered_menu_help_about(self):
		AboutDlg(self.app).exec_()

	def on_triggered_menu_file_save(self):
		self.prefs_save_to_file()

	def on_triggered_menu_file_exit(self):
		self.ws_cleanup()
		return self.close()

	def on_changed_endpoint(self):
		self.m_endpoint = self.txt_endpoint.text().strip()
		self.btn_connect.setEnabled(self.ws_spotcheck_params())

	def on_changed_timeout(self):
		timeout = self.txt_timeout.text().strip()
		if not timeout.isdecimal(): timeout = str(0)
		self.m_timeout = int(timeout)
		self.btn_connect.setEnabled(self.ws_spotcheck_params())

	def on_changed_ping_interval(self):
		interval = self.txt_ping_interval.text().strip()
		if not interval.isdecimal(): interval = str(0)
		self.m_ping_interval = int(interval)
		self.btn_connect.setEnabled(self.ws_spotcheck_params())

	def on_changed_ping_timeout(self):
		timeout = self.txt_ping_timeout.text().strip()
		if not timeout.isdecimal(): timeout = str(0)
		self.m_ping_timeout = int(timeout)
		self.btn_connect.setEnabled(self.ws_spotcheck_params())

	def on_changed_ping_message(self):
		self.m_ping_message = self.txt_ping_message.toPlainText()
		self.btn_ping_message.setEnabled(self.ws_spotcheck_params())

	def on_changed_message(self):
		self.m_message = self.txt_message.toPlainText()
		self.btn_send_message.setEnabled(len(self.m_message) > 0)

	def on_clicked_button_connect(self):
		if not self.ws_ready():
			use_ssl = self.m_endpoint.startswith("wss:")
			if use_ssl:
				if not self.m_autossl:
					if not os.path.exists(self.m_sslfile):
						self.status("This end-point required SSL file", color_t.error)
						return
			if self.m_autoping:
				if self.m_ping_interval <= self.m_ping_timeout: # refer to websocket._app.py!WebSocketApp.run_forever(...)
					QMessageBox.critical(self, "Error", "Ping required interval-time is greater than ping time-out")
					return
			self.ws_start(use_ssl)
		else:
			self.ws_close()

	def on_clicked_auto_use_ssl_chains(self):
		self.m_autossl = self.chk_auto_use_ssl_chains.isChecked()
		self.update_ui()

	def on_clicked_button_browse_ssl_file(self):
		self.m_sslfile = Picker.select_file(self, self.is_default_style())
		self.update_ui(True)

	def on_clicked_auto_ping(self):
		self.m_autoping = self.chk_ping.isChecked()
		self.update_ui()

	def on_clicked_button_ping_send_message(self):
		self.ws_ping(self.m_ping_message)
		self.log(self.m_ping_message, color_t.orange, icon_t.up)

	def on_clicked_button_send_message(self):
		message = self.m_message
		data_type = self.selected_send_data_type()
		if data_type == data_t.text:
			self.ws_send(message)
		elif data_type == data_t.binary:
			try:
				binary = bytes.fromhex(self.m_message.strip())
				self.ws_send(binary, ABNF.OPCODE_BINARY)
				message = hex_view(binary)
			except Exception as e:
				QMessageBox.critical(self, "Error", str(e))
				return
		self.log(message, color_t.orange, icon_t.up)

	def on_clicked_button_clear_list_log(self):
		self.list_log.clear()

	def on_clicked_button_save_list_log(self):
		log_file_path = Picker.save_file(
			self, self.is_default_style(), directory="log_data.txt", filter="Text Files")
		if log_file_path == "": return
		lines = []
		for i in range(self.list_log.count()):
			item  = self.list_log.item(i)
			line  = ""
			line += item.data(Qt.UserRole)
			line += "\n"
			line += item.text()
			line += "\n"
			lines.append(line)
		with open(log_file_path, "w+") as f:
			f.write("\n".join(lines))

	def on_clicked_button_clear_list_debug(self):
		self.list_debug.clear()

	def on_clicked_button_save_list_debug(self):
		debug_file_path = Picker.save_file(
			self, self.is_default_style(), directory="log_debug.txt", filter="Text Files")
		if debug_file_path == "": return
		lines = [self.list_debug.item(i).text() for i in range(self.list_debug.count())]
		with open(debug_file_path, "w+") as f:
			f.write("\n".join(lines))