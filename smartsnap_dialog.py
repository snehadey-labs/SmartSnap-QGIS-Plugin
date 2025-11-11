from qgis.PyQt import QtWidgets, uic
from qgis.core import QgsProject, QgsProcessingFeedback
import processing
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'smartsnap_dialog_base.ui'))

class SmartSnapDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(SmartSnapDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.populate_layers()
        self.runButton.clicked.connect(self.run_smartsnap)

    def populate_layers(self):
        self.layerComboBox.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == 0:  # Vector layer only
                self.layerComboBox.addItem(layer.name())

    def run_smartsnap(self):
        layer_name = self.layerComboBox.currentText()
        tolerance = self.toleranceSpinBox.value()

        # Find selected layer
        layer = None
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == layer_name:
                layer = lyr
                break

        if not layer:
            QtWidgets.QMessageBox.warning(self, "SmartSnap", "Please select a valid vector layer.")
            return

        feedback = QgsProcessingFeedback()

        # Step 1: Fix invalid geometries
        fixed_geom = processing.run(
            "native:fixgeometries",
            {'INPUT': layer, 'OUTPUT': 'memory:'},
            feedback=feedback
        )['OUTPUT']

        # Step 2: Remove duplicate geometries (supports old & new QGIS)
        try:
            no_duplicates = processing.run(
                "native:removeduplicategeometries",
                {'INPUT': fixed_geom, 'OUTPUT': 'memory:'},
                feedback=feedback
            )['OUTPUT']
        except:
            no_duplicates = processing.run(
                "qgis:deleteduplicategeometries",
                {'INPUT': fixed_geom, 'OUTPUT': 'memory:'},
                feedback=feedback
            )['OUTPUT']

        # Step 3: Snap geometries to themselves
        snapped = processing.run(
            "native:snapgeometries",
            {
                'INPUT': no_duplicates,
                'REFERENCE_LAYER': no_duplicates,
                'TOLERANCE': tolerance,
                'BEHAVIOR': 0,
                'OUTPUT': 'memory:'
            },
            feedback=feedback
        )['OUTPUT']
        # Step 4: Remove dangling short segments (universal, no GRASS required)
        cleaned = processing.run(
            "native:extractbyexpression",
            {
                'INPUT': snapped,
                'EXPRESSION': f'length($geometry) > {tolerance}',
                'OUTPUT': 'memory:'
            },
            feedback=feedback
        )['OUTPUT']


        # Step 5: Final geometry fix
        final_clean = processing.run(
            "native:fixgeometries",
            {'INPUT': cleaned, 'OUTPUT': 'memory:'},
            feedback=feedback
        )['OUTPUT']

        final_clean.setName("SmartSnap_Result")
        QgsProject.instance().addMapLayer(final_clean)

        QtWidgets.QMessageBox.information(self, "SmartSnap", "SmartSnap finished successfully!")
