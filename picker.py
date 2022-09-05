from PyQt5.QtWidgets import QFileDialog

DEF_DIR = ""
DEF_FILTER = "All Files (*.*)"

class Picker:

	@staticmethod
	def select_file(parent=None, stype=True, directory=DEF_DIR, filter=DEF_FILTER):
		options = QFileDialog.Options()
		if not stype: options |= QFileDialog.DontUseNativeDialog
		return QFileDialog.getOpenFileName(
			parent, "Select File", directory, DEF_FILTER, options=options)[0]

	@staticmethod
	def select_files(parent=None, stype=True, directory=DEF_DIR, filter=DEF_FILTER):
		options = QFileDialog.Options()
		if not stype: options |= QFileDialog.DontUseNativeDialog
		return QFileDialog.getOpenFileNames(
			parent, "Select Files", directory, DEF_FILTER, options=options)[0]

	@staticmethod
	def save_file(parent=None, stype=True, directory=DEF_DIR, filter=DEF_FILTER):
		options = QFileDialog.Options()
		if not stype: options |= QFileDialog.DontUseNativeDialog
		return QFileDialog.getSaveFileName(
			parent, "Select File", directory, filter, options=options)[0]

	@staticmethod
	def select_directory(parent=None, stype=True, directory=DEF_DIR):
		options = QFileDialog.Options()
		if not stype: options |= QFileDialog.DontUseNativeDialog
		options |= QFileDialog.ShowDirsOnly
		return QFileDialog.getExistingDirectory(
			parent, "Select Directory", directory, options=options)
