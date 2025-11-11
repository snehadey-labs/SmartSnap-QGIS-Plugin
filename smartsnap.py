from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import QAction
from .smartsnap_dialog import SmartSnapDialog

class SmartSnap:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("SmartSnap", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("SmartSnap", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("SmartSnap", self.action)

    def run(self):
        dlg = SmartSnapDialog(self.iface)
        dlg.show()
        dlg.exec_()
