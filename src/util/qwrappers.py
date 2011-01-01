#!/usr/bin/env python

from __future__ import with_statement
from __future__ import division

from PyQt4 import QtGui
from PyQt4 import QtCore

from util import qui_utils
from util import misc as misc_utils
import logging


_moduleLogger = logging.getLogger(__name__)


class ApplicationWrapper(object):

	def __init__(self, qapp, constants):
		self._constants = constants
		self._qapp = qapp
		self._clipboard = QtGui.QApplication.clipboard()

		self._errorLog = qui_utils.QErrorLog()
		self._mainWindow = None

		self._fullscreenAction = QtGui.QAction(None)
		self._fullscreenAction.setText("Fullscreen")
		self._fullscreenAction.setCheckable(True)
		self._fullscreenAction.setShortcut(QtGui.QKeySequence("CTRL+Enter"))
		self._fullscreenAction.toggled.connect(self._on_toggle_fullscreen)

		self._logAction = QtGui.QAction(None)
		self._logAction.setText("Log")
		self._logAction.setShortcut(QtGui.QKeySequence("CTRL+l"))
		self._logAction.triggered.connect(self._on_log)

		self._quitAction = QtGui.QAction(None)
		self._quitAction.setText("Quit")
		self._quitAction.setShortcut(QtGui.QKeySequence("CTRL+q"))
		self._quitAction.triggered.connect(self._on_quit)

		self._aboutAction = QtGui.QAction(None)
		self._aboutAction.setText("About")
		self._aboutAction.triggered.connect(self._on_about)

		self._qapp.lastWindowClosed.connect(self._on_app_quit)
		self._mainWindow = self._new_main_window()
		self._mainWindow.window.destroyed.connect(self._on_child_close)

		self.load_settings()

		self._mainWindow.show()
		self._idleDelay = QtCore.QTimer()
		self._idleDelay.setSingleShot(True)
		self._idleDelay.setInterval(0)
		self._idleDelay.timeout.connect(lambda: self._mainWindow.start())
		self._idleDelay.start()

	def load_settings(self):
		raise NotImplementedError("Booh")

	def save_settings(self):
		raise NotImplementedError("Booh")

	def _new_main_window(self):
		raise NotImplementedError("Booh")

	@property
	def constants(self):
		return self._constants

	@property
	def errorLog(self):
		return self._errorLog

	@property
	def fullscreenAction(self):
		return self._fullscreenAction

	@property
	def logAction(self):
		return self._logAction

	@property
	def aboutAction(self):
		return self._aboutAction

	@property
	def quitAction(self):
		return self._quitAction

	def _close_windows(self):
		if self._mainWindow is not None:
			self.save_settings()
			self._mainWindow.window.destroyed.disconnect(self._on_child_close)
			self._mainWindow.close()
			self._mainWindow = None

	@misc_utils.log_exception(_moduleLogger)
	def _on_app_quit(self, checked = False):
		if self._mainWindow is not None:
			self.save_settings()
			self._mainWindow.destroy()

	@misc_utils.log_exception(_moduleLogger)
	def _on_child_close(self, obj = None):
		if self._mainWindow is not None:
			self.save_settings()
			self._mainWindow = None

	@misc_utils.log_exception(_moduleLogger)
	def _on_toggle_fullscreen(self, checked = False):
		for window in self._walk_children():
			window.set_fullscreen(checked)

	@misc_utils.log_exception(_moduleLogger)
	def _on_about(self, checked = True):
		raise NotImplementedError("Booh")

	@misc_utils.log_exception(_moduleLogger)
	def _on_log(self, checked = False):
		with open(self._constants._user_logpath_, "r") as f:
			logLines = f.xreadlines()
			log = "".join(logLines)
			self._clipboard.setText(log)

	@misc_utils.log_exception(_moduleLogger)
	def _on_quit(self, checked = False):
		self._close_windows()


class WindowWrapper(object):

	def __init__(self, parent, app):
		self._app = app

		self._errorDisplay = qui_utils.ErrorDisplay(self._app.errorLog)

		self._layout = QtGui.QVBoxLayout()
		self._layout.setContentsMargins(0, 0, 0, 0)
		self._layout.addWidget(self._errorDisplay.toplevel)

		centralWidget = QtGui.QWidget()
		centralWidget.setLayout(self._layout)
		centralWidget.setContentsMargins(0, 0, 0, 0)

		self._window = QtGui.QMainWindow(parent)
		self._window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		qui_utils.set_autorient(self._window, True)
		qui_utils.set_stackable(self._window, True)
		self._window.setWindowIcon(QtGui.QIcon(self._app.appIconPath))
		self._window.setCentralWidget(centralWidget)

		self._closeWindowAction = QtGui.QAction(None)
		self._closeWindowAction.setText("Close")
		self._closeWindowAction.setShortcut(QtGui.QKeySequence("CTRL+w"))
		self._closeWindowAction.triggered.connect(self._on_close_window)

		toolsMenu = self._window.menuBar().addMenu("&Tools")
		toolsMenu.addAction(self._app.aboutAction)

		self._window.addAction(self._closeWindowAction)
		self._window.addAction(self._app.quitAction)
		self._window.addAction(self._app.fullscreenAction)
		self._window.addAction(self._app.logAction)

	@property
	def window(self):
		return self._window

	def walk_children(self):
		return ()

	def start(self):
		pass

	def close(self):
		for child in self.walk_children():
			child.window.destroyed.disconnect(self._on_child_close)
			child.close()
		self._window.close()

	def destroy(self):
		pass

	def show(self):
		self.set_fullscreen(self._app.fullscreenAction.isChecked())
		self._window.show()
		for child in self.walk_children():
			child.show()

	def hide(self):
		for child in self.walk_children():
			child.hide()
		self._window.hide()

	def set_fullscreen(self, isFullscreen):
		if isFullscreen:
			self._window.showFullScreen()
		else:
			self._window.showNormal()
		for child in self.walk_children():
			child.set_fullscreen(isFullscreen)

	@misc_utils.log_exception(_moduleLogger)
	def _on_close_window(self, checked = True):
		self.close()
