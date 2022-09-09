from logging import StreamHandler

class WSHandler(StreamHandler):
	'''
	Websocket Logging Handler
	'''

	m_prefixes = {
		"++Sent raw": "SEND-R",
		"++Sent decoded": "SEND-D",
		"++Rcv raw": "RECV-R",
		"++Rcv decoded": "RECV-D",
	}

	def __init__(self, window):
		super().__init__(None)
		self.m_window = window

	def emit(self, record):
		# super().emit(record)
		msg = self.format(record)
		for k, v in self.m_prefixes.items():
			if msg.startswith(k):
				msg = msg.replace(k, v)
				# tmp = msg[len(k)-1:] # remove prefix
				# if tmp.startswith("b'"): msg = tmp[1:-1].replace("\\x", " ").strip()
				break
		self.m_window.debug(msg)
