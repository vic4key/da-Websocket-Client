from logging import StreamHandler
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from utils import get_default_font

class WSHandler(StreamHandler):
	'''
	Custom Logging Handler
	'''

	m_list : QListWidget

	m_prefixes = {
		"++Sent raw": "SEND-R",
		"++Sent decoded": "SEND-D",
		"++Rcv raw": "RECV-R",
		"++Rcv decoded": "RECV-D",
	}

	def __init__(self, qlist : QListWidget):
		super().__init__(None)
		self.m_list = qlist

	def emit(self, record):
		# super().emit(record)
		msg = self.format(record)
		for k, v in self.m_prefixes.items():
			if msg.startswith(k):
				msg = msg.replace(k, v)
				# tmp = msg[len(k)-1:] # remove prefix
				# if tmp.startswith("b'"): msg = tmp[1:-1].replace("\\x", " ").strip()
				break
		item = QListWidgetItem(msg)
		item.setFont(get_default_font())
		item.setData(Qt.UserRole, "")
		self.m_list.addItem(item)
		self.m_list.scrollToBottom()