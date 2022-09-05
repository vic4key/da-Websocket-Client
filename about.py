from PyQt5 import uic as UiLoader
from PyQt5.QtWidgets import QDialog

from utils import *

class AboutDlg(QDialog):
	def __init__(self, app):
		super(AboutDlg, self).__init__()
		self.app = app
		self.setup_ui()

	def setup_ui(self):
		UiLoader.loadUi(resources("about.ui"), self)
		self.buttonBox.clicked.connect(lambda: self.close())