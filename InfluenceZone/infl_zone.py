# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InfluenceZone
                                 A QGIS plugin
 Crea poligono del area de influencia de una polilinea, a la derecha, izquierda o, ambos lados
                              -------------------
        begin                : 2017-06-03
        git sha              : $Format:%H$
        copyright            : (C) 2017 by dalxder
        email                : dalxder@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,QVariant,SIGNAL
from PyQt4.QtGui import QAction, QIcon,QDialog,QMessageBox
from PyQt4 import uic
from qgis.core import *
from math import *
import math
from shapely.geometry import LineString,Polygon,LinearRing
from shapely.ops import cascaded_union
# Initialize Qt resources from file resources.py
#import resources
# Import the code for the dialog
import os.path
#from mmqgis.mmqgis_library import *


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'infl_zone_dialog.ui'))

class InfluenceZoneDialog(QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        """Constructor."""
         #QDialog.__init__(self)
        super(InfluenceZoneDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        #self.selectedfeats.stateChanged.connect(self.atr_cambio)
        self.comboAtrib.currentIndexChanged.connect(self.atr_cambio)

        #self.connect(self.comboAtrib, SIGNAL("currentIndexChanged()"), self.atr_cambio)

    def populatedialogue(self, layername):
        self.buffer_layer_name.clear()
        self.buffer_layer_name.setText(layername)

    def atr_cambio(self):
        self.bufferDistance.setEnabled(str(self.comboAtrib.currentText() )== "Valor Fijo")

class InfluenceZone:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'InfluenceZone_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = InfluenceZoneDialog()
        #self.dlg.connect(self.dlg.comboAtrib, SIGNAL("currentIndexChanged()"), self.dlg.atr_cambio)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Zonas de Influencia')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Zonas de Influencia')
        self.toolbar.setObjectName(u'InfluenceZone')




    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('InfluenceZone', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = InfluenceZoneDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = self.plugin_dir+'/icon.svg'
        self.add_action(
            icon_path,
            text=self.tr(u'Zonas de Influencia'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Zonas de Influencia'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    def dissolve(self, input_feats):
        # Function to dissolve input features to allow for buffering of multiple features
        feats = []
        # Create and empty list of features and add all features to it.
        # We use feature 0 later and this ensures it exits.
        for each_feat in input_feats:
            feats.append(each_feat)
        # Do not run if geometry is empty, produce an error instead.
        if len(feats) > 0:
            # Need to create empty geometry to hold the dissolved features, we use the first feature to seed it.
            # Combine require a non-empty geometry to work (I could not get it to work).
            feat = feats[0]
            dissolved_geom = QgsGeometry()
            dissolved_geom = feat.geometry()
            # Progress bar for dissolving
            progressMessageBar = self.iface.messageBar().createMessage("Dissolving...")
            progress = QProgressBar()
            progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            progressMessageBar.layout().addWidget(progress)
            self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)
            maximum_progress = len(feats)
            progress.setMaximum(maximum_progress)
            i = 0
            # Run through the features and dissolve them all.
            for each_feat in feats:
                geom = each_feat.geometry()
                dissolved_geom = geom.combine(dissolved_geom)
                i = i + 1
                progress.setValue(i + 1)
            return_f = QgsFeature()
            return_f.setGeometry(dissolved_geom)
            self.iface.messageBar().clearWidgets()
            return return_f
        else:
            QMessageBox.warning(self.iface.mainWindow(), "Warning",
                "No features to dissolve.", QMessageBox.Ok)
            return input_feats

    def run(self):

        active_vl = self.iface.activeLayer()
        # Plugin uses selected layer, hope to add layer selection later.

        # Logic if to run the dialog
        if active_vl is None:
            sel_feats = ''
            QMessageBox.warning(self.iface.mainWindow(), u"Atención",
                "No ha seleccionado ninguna capa.", QMessageBox.Ok)
            result = 0

        elif active_vl.type() == QgsMapLayer.RasterLayer:
            sel_feats = ''
            QMessageBox.warning(self.iface.mainWindow(), u"Atención",
                "Ha seleccionado una capa raster", QMessageBox.Ok)
            result = 0
        elif active_vl.type() == QgsMapLayer.PluginLayer:
            sel_feats = ''
            QMessageBox.warning(self.iface.mainWindow(),u"Atención",
                "No se puede trabajar con esta capa. Solo capas vectoriales de Qgis", QMessageBox.Ok)
            result = 0
        elif active_vl is not None:
            self.dlg.populatedialogue(active_vl.name())
            for field in active_vl.dataProvider().fields().toList():
    			if (field.type() in [QVariant.Double, QVariant.Int, QVariant.UInt]):
    				self.dlg.comboAtrib.addItem(field.name())
            if len(active_vl.selectedFeatures())!=0:
                self.dlg.selectedfeats.setEnabled(1)
            else:
                self.dlg.selectedfeats.setEnabled(1)
            # Campos ideales para buffer


            #self.dlg.show()
            result = self.dlg.exec_()
        else:
            sel_feats = ''
            QMessageBox.warning(self.iface.mainWindow(), "Warning",
                "Could not process layer.", QMessageBox.Ok)
            result = 0

        if result == 1:
            # Check the current CRS of the layer
            buffer_crs = self.iface.activeLayer().crs().authid()

             # Apply that to the created layer if recognised
            buffer_input_crs = "Polygon?crs=%s" % buffer_crs
            # Create empty memory vector layer for buffers
            vl = QgsVectorLayer(buffer_input_crs, "%s_Buffer" % active_vl.name(), "memory")
            vl_pr = vl.dataProvider()
            # Distance feature for buffer distance
            vl_pr.addAttributes([QgsField("distance", QVariant.String)])

            vl_pr.addAttributes([QgsField("b", QVariant.String),
                                QgsField("a",  QVariant.Int),
                                QgsField("c", QVariant.Double)])
            vl.updateFields()
            # Inputs from the dialog:

            # We use "sel_feats" to populate a box in the dialog, but if all features wanted, we need to re-populate it
            # with all the features in the layer.
            if bool( self.dlg.selectedfeats.isChecked()):
                features = active_vl.selectedFeatures()
            else:
                features = active_vl.getFeatures()

            idx = active_vl.fieldNameIndex(str(self.dlg.comboAtrib.currentText() ))


            newfet=[]
            polgns=self.generadorBuffer(features,idx)
            if bool(self.dlg.dissovle_button_2.isChecked()):
                print(polgns)
                s=cascaded_union(polgns)
                f = QgsFeature()
                f.setGeometry(QgsGeometry.fromWkt(str(s)))
                f.setAttributes([100,1,1])
                vl_pr.addFeatures([f])

            else:# sin disolver poligonos
                newfet=[]
                for pol in polgns:
                    f = QgsFeature()
                    f.setGeometry(QgsGeometry.fromWkt(str(pol)))
                    f.setAttributes([100,0,0])
                    newfet.append(f)
                vl_pr.addFeatures(newfet)

            vl.commitChanges()
            QgsMapLayerRegistry.instance().addMapLayer(vl)





    def generadorBuffer(self,features,idx):
        polgns=[]
        side=str(self.dlg.comboSide.currentText())
        distance=float(self.dlg.bufferDistance.text())
        for feature in features:
            print(feature.attributes()[idx])
            fet = QgsFeature()
            geom = feature.geometry()
            if (geom.wkbType() == QGis.WKBLineString) or (geom.wkbType()  == QGis.WKBLineString25D):
                h = geom.asPolyline()
                line = LineString(h)
                if side=="Completo":
                    nline1 = line.parallel_offset(distance, 'left',resolution=16,join_style=1,mitre_limit=10.0)
                    nline2 = line.parallel_offset(distance, 'right',resolution=16,join_style=1,mitre_limit=10.0)
                    li=list(nline1.coords)+list(nline2.coords)
                else:
                    if side=='Izquierda':
                        s='left'
                        nline = line.parallel_offset(distance, s,resolution=16,join_style=1,mitre_limit=10.0)
                        li=h+list(nline.coords)[::-1]
                    else:
                        s='right'
                        nline = line.parallel_offset(distance, s,resolution=16,join_style=1,mitre_limit=10.0)
                        li=h+list(nline.coords)
                polgns.append(Polygon(LinearRing(li)))
        return polgns