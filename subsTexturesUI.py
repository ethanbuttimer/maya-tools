from PySide2.QtWidgets import QRadioButton
from maya import cmds
from PySide2 import QtWidgets, QtCore, QtGui
from os import listdir
from os.path import isfile, join
from mtoa.utils import *
from rfm2.api import *

class SubsTextureManagerUI(QtWidgets.QDialog):

    def __init__(self):
        super(SubsTextureManagerUI, self).__init__()
        self.setWindowTitle('PxrSurface from Substance Textures')
        self.name_input = None
        self.pxr_surface_name = None
        self.directory = "none"
        self.textures = {
            "diffColor": "none",
            "specFaceColor": "none",
            "specEdgeColor": "none",
            "specRough": "none",
            "normal": "none",
            "bump": "none",
            "glowColor": "none",
            "presence": "none",
            "subsurfaceColor": "none"
        }
        self.node_names = {
            "diffColor": "none",
            "specFaceColor": "none",
            "specEdgeColor": "none",
            "specRough": "none",
            "normal": "none",
            "bump": "none",
            "glowColor": "none",
            "presence": "none",
            "subsurfaceColor": "none"
        }
        self.reverse_normals = True
        self.spec_mode_artistic = False
        self.loaded_existing = False
        self.buildUI()


    # UI AND FILE MANAGEMENT


    def buildUI(self):
        print "building"
        self.layout = QtWidgets.QVBoxLayout(self)

        self.loadPxrWidget = QtWidgets.QWidget()
        self.loadPxrLayout = QtWidgets.QHBoxLayout(self.loadPxrWidget)
        self.loadPxrBtn = QtWidgets.QPushButton("Load PxrSurface of Selected")
        self.loadPxrLayout.addWidget(self.loadPxrBtn)
        self.loadPxrBtn.clicked.connect(self.find_existing_pxr)

        self.layout.addWidget(self.loadPxrWidget)

        #Fields to enter PxrSurface name and locate the texture directory
        self.nameWidget = QtWidgets.QWidget()
        self.nameLayout = QtWidgets.QHBoxLayout(self.nameWidget)
        self.pxrNameLabel = QtWidgets.QLabel("PxrSurface Name:")
        self.nameLayout.addWidget(self.pxrNameLabel)
        self.pxrNameField = QtWidgets.QLineEdit()
        self.nameLayout.addWidget(self.pxrNameField)
        self.layout.addWidget(self.nameWidget)

        self.directoryWidget = QtWidgets.QWidget()
        self.directoryLayout = QtWidgets.QHBoxLayout(self.directoryWidget)
        self.directoryLabel = QtWidgets.QLabel("Texture Directory:")
        self.directoryLayout.addWidget(self.directoryLabel)
        self.directoryField = QtWidgets.QLineEdit()
        self.directoryLayout.addWidget(self.directoryField)
        self.directoryBtn = QtWidgets.QPushButton("Locate")
        self.directoryLayout.addWidget(self.directoryBtn)
        self.directoryBtn.clicked.connect(self.locate_directory)

        self.layout.addWidget(self.directoryWidget)

        #All Textures checkbox, checkbox for each texture file found
        self.plugWidget = QtWidgets.QWidget()
        self.plugLayout = QtWidgets.QVBoxLayout(self.plugWidget)
        self.plugCheckbox = QtWidgets.QCheckBox()
        self.plugCheckbox.toggle()
        self.plugCheckbox.setText("Plug in all available textures")
        self.plugLayout.addWidget(self.plugCheckbox)
        self.plugCheckbox.stateChanged.connect(self.plug_checkbox_handler)

        self.filesWidget = QtWidgets.QListWidget()
        self.plugLayout.addWidget(self.filesWidget)
        self.filesWidget.setEnabled(False)

        self.layout.addWidget(self.plugWidget)

        #checkboxes to reverse normals, set diffuse texture destination, specular color options
        self.optionsWidget = QtWidgets.QWidget()
        self.optionsLayout = QtWidgets.QVBoxLayout(self.optionsWidget)

        self.specDestLabel = QtWidgets.QLabel("Primary specular mode:")
        self.optionsLayout.addWidget(self.specDestLabel)
        self.specDestWidget = QtWidgets.QWidget()
        self.specDestLayout = QtWidgets.QHBoxLayout(self.specDestWidget)
        self.specPhysicalRadio = QRadioButton("Physical")
        self.specPhysicalRadio.toggled.connect(self.spec_toggle)
        self.specDestLayout.addWidget(self.specPhysicalRadio)
        self.specArtisticRadio = QRadioButton("Artistic")
        self.specArtisticRadio.setChecked(True)
        self.specArtisticRadio.toggled.connect(self.spec_toggle)
        self.specDestLayout.addWidget(self.specArtisticRadio)
        self.optionsLayout.addWidget(self.specDestWidget)

        self.reverseCheckbox = QtWidgets.QCheckBox()
        self.reverseCheckbox.toggle()
        self.reverseCheckbox.setText("Invert bump for normals (recommended)")
        self.optionsLayout.addWidget(self.reverseCheckbox)

        self.layout.addWidget(self.optionsWidget)


        #Apply and Close buttons
        self.btnWidget = QtWidgets.QWidget()
        self.btnLayout = QtWidgets.QHBoxLayout(self.btnWidget)

        self.applyBtn = QtWidgets.QPushButton("Create New")
        self.btnLayout.addWidget(self.applyBtn)
        self.applyBtn.clicked.connect(self.createPxr)

        self.updateButton = QtWidgets.QPushButton("Update Existing")
        self.btnLayout.addWidget(self.updateButton)
        self.updateButton.clicked.connect(self.updatePxr)

        self.closeBtn = QtWidgets.QPushButton("Close")
        self.btnLayout.addWidget(self.closeBtn)
        self.closeBtn.clicked.connect(self.close)

        self.layout.addWidget(self.btnWidget)

    def spec_toggle(self):
        self.spec_mode_artistic = not self.spec_mode_artistic

    def find_existing_pxr(self):
        objSel = cmds.ls(sl=True, s=1, dag=1)
        if len(objSel) == 0:
            cmds.warning("Please select a mesh")
            return True
        for object in objSel:
            pxr = nodes.get_bxdf(nodes.get_shape_shading_engine(object))
            if pxr:
                self.pxr_surface_name = pxr
                break
        self.pxrNameField.setText(self.pxr_surface_name)
        if not self.pxr_surface_name:
            cmds.warning("No existing PxrSurface found. Use 'Create and Assign' option.")
            return

        connections = cmds.listConnections(self.pxr_surface_name, connections=True)
        print connections
        for i in range(0, len(connections), 2):
            plug = connections[i]
            input = connections[i+1]
            if "diffuseColor" in plug:
                self.node_names["diffColor"] = input
            if "specularFaceColor" in plug:
                self.node_names["specFaceColor"] = input
            if "specularEdgeColor" in plug:
                self.node_names["specEdgeColor"] = input
            if "specularRoughness" in plug:
                self.node_names["specRough"] = input
            if "bumpNormal" in plug:
                if "normal" in input:
                    self.node_names["normal"] = input
                else:
                    self.node_names["bump"] = input
            if "glowColor" in plug:
                self.node_names["glowColor"] = input
            if "presence" in plug:
                self.node_names["presence"] = input
            if "subsurfaceColor" in plug:
                self.node_names["subsurfaceColor"] = input

        self.loaded_existing = True

    def plug_checkbox_handler(self):
        if self.plugCheckbox.isChecked():
            for i in range(self.filesWidget.count()):
                self.filesWidget.item(i).setCheckState(QtCore.Qt.Checked)
            self.filesWidget.setEnabled(False)
        else:
            self.filesWidget.setEnabled(True)

    def locate_directory(self):
        self.directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory', os.path.join(cmds.workspace(q=True, rd=True), 'sourceimages'))
        self.directoryField.setText(self.directory)
        self.update_file_list()

    def update_file_list(self):
        print "listing"
        if self.directory == "none":
            return

        onlyFiles = [f for f in listdir(self.directory) if self.check_file_type(join(self.directory, f))]

        for file in onlyFiles:
            if "_DiffuseColor" in file:
                self.textures["diffColor"] = file
                self.textures["subsurfaceColor"] = file
            if "_SpecularFaceColor" in file:
                self.textures["specFaceColor"] = file
            if "_SpecularEdgeColor" in file:
                self.textures["specEdgeColor"] = file
            if "_SpecularRoughness" in file:
                self.textures["specRough"] = file
            if "_Normal" in file:
                self.textures["normal"] = file
            if "_Displacement" in file:
                self.textures["bump"] = file
            if "_GlowColor" in file:
                self.textures["glowColor"] = file
            if "_Presence" in file:
                self.textures["presence"] = file

        self.filesWidget.clear()
        for key in self.textures:
            if self.textures[key] != "none":
                print "adding"
                listText = self.textures[key]
                if key == "diffColor":
                    listText = ("DIFFUSE <-- %s" % self.textures[key])
                elif key == "subsurfaceColor":
                    listText = ("SUBSURFACE <-- %s" % self.textures[key])

                temp = QtWidgets.QListWidgetItem(listText)
                temp.setCheckState(QtCore.Qt.Checked)
                self.filesWidget.addItem(temp)

    def check_file_type(self, path):
        return (isfile(path) and ".png" in path and ".tex" not in path)

    def collect_user_input(self):
        self.name_input = self.pxrNameField.text()
        self.directory = self.directoryField.text()
        for i in range(self.filesWidget.count()):
            if self.filesWidget.item(i).checkState() != QtCore.Qt.Checked:
                for key in self.textures.keys():
                    if (self.textures[key] == self.filesWidget.item(i).text()) or (("SUBSURFACE <-- %s" % self.textures[key]) == self.filesWidget.item(i).text()) or (("DIFFUSE <-- %s" % self.textures[key]) == self.filesWidget.item(i).text()):
                        self.textures[key] = "none"
        self.spec_mode_artistic = self.specArtisticRadio.isChecked()
        self.reverse_normals = self.reverseCheckbox.isChecked()

    def bad_use(self):
        selected = cmds.ls(sl=True, fl=True)
        if len(selected) == 0:
            cmds.warning("Please select a mesh")
            return True
        print selected
        if not self.name_input:
            cmds.warning("Please enter a PxrSurface name")
            return True
        if not self.directory:
            cmds.warning("Please locate a texture directory")
            return True
        return False


    #PXRSURFACE MANIPULATION


    def createPxr(self):
        print "creating"
        self.collect_user_input()
        if self.bad_use():
            return

        nodes.create_and_assign_bxdf('PxrSurface')
        sel = cmds.ls(sl=True)[0]
        self.pxr_surface_name = cmds.rename(sel, self.name_input)

        for key in self.textures.keys():
            if self.textures[key] != "none":
                self.add_tex_node(key)
                self.update_tex(key)

        if self.node_names["diffColor"] == "none":
            cmds.setAttr('%s.diffuseGain' % self.pxr_surface_name, 0.0)

        cmds.select(self.pxr_surface_name)

    def updatePxr(self):
        print "updating"
        self.collect_user_input()
        if self.bad_use():
            return

        if not self.loaded_existing or not self.pxr_surface_name:
            cmds.warning("No existing PxrSurface found. Use 'Create and Assign' option.")
            return
        if self.name_input:
            self.pxr_surface_name = cmds.rename(self.pxr_surface_name, self.name_input)

        for key in self.textures.keys():
            if self.textures[key] != "none":
                if self.node_names[key] == "none":
                    self.add_tex_node(key)
                self.update_tex(key)

        if self.node_names["diffColor"] == "none":
            cmds.setAttr('%s.diffuseGain' % self.pxr_surface_name, 0.0)

        cmds.select(self.pxr_surface_name)

    def add_tex_node(self, key):
        if key == "normal":
            nodes.create_and_select('PxrNormalMap')
        elif key == "bump":
            nodes.create_and_select('PxrBump')
        else:
            nodes.create_and_select('PxrTexture')

        nodeName = cmds.ls(sl=True)[0]

        if key == "diffColor":
            print "adding diffuse color texture"
            nodeName = cmds.rename(nodeName, '%s_diffuse_tex' % self.pxr_surface_name)
            cmds.connectAttr('%s.resultRGB' % nodeName, '%s.diffuseColor' % self.pxr_surface_name, f=True)
        elif key == "specFaceColor":
            if self.spec_mode_artistic:
                print "adding specular face color texture, ARTISTIC"
                cmds.setAttr('%s.specularFresnelMode' % self.pxr_surface_name, 0)
                nodeName = cmds.rename(nodeName, '%s_spec_face_color_tex' % self.pxr_surface_name)
                cmds.connectAttr('%s.resultRGB' % nodeName, '%s.specularFaceColor' % self.pxr_surface_name, f=True)
            else:
                print "adding specular face color texture, PHYSICAL"
                #ADD CHANGES TO EXTINCTION COEFF
                cmds.setAttr('%s.specularFresnelMode' % self.pxr_surface_name, 1)
                nodeName = cmds.rename(nodeName, '%s_spec_edge_physical_color_tex' % self.pxr_surface_name)
                cmds.connectAttr('%s.resultRGB' % nodeName, '%s.specularEdgeColor' % self.pxr_surface_name, f=True)
        elif key == "specEdgeColor":
            if self.spec_mode_artistic:
                print "adding specular edge color texture"
                nodeName = cmds.rename(nodeName, '%s_spec_edge_color_tex' % self.pxr_surface_name)
                cmds.connectAttr('%s.resultRGB' % nodeName, '%s.specularEdgeColor' % self.pxr_surface_name, f=True)
        elif key == "specRough":
            print "adding specular roughness texture"
            nodeName = cmds.rename(nodeName, '%s_spec_rough_tex' % self.pxr_surface_name)
            cmds.connectAttr('%s.resultR' % nodeName, '%s.specularRoughness' % self.pxr_surface_name, f=True)
        elif key == "normal":
            print "adding global normal texture"
            nodeName = cmds.rename(nodeName, '%s_global_normal' % self.pxr_surface_name)
            cmds.connectAttr('%s.resultN' % nodeName, '%s.bumpNormal' % self.pxr_surface_name, f=True)
            cmds.setAttr('%s.invertBump' % nodeName, self.reverse_normals)
        elif key == "bump" and self.node_names["normal"] == "none":
            print "adding global bump texture"
            nodeName = cmds.rename(nodeName, '%s_global_bump' % self.pxr_surface_name)
            cmds.connectAttr('%s.resultN' % nodeName, '%s.bumpNormal' % self.pxr_surface_name, f=True)
        elif key == "glowColor":
            print "adding glow color texture"
            nodeName = cmds.rename(nodeName, '%s_glow_tex' % self.pxr_surface_name)
            cmds.connectAttr('%s.resultRGB' % nodeName, '%s.glowColor' % self.pxr_surface_name, f=True)
            cmds.setAttr('%s.glowGain' % self.pxr_surface_name, 1.0)
        elif key == "presence":
            print "adding presence texture"
            nodeName = cmds.rename(nodeName, '%s_presence_tex' % self.pxr_surface_name)
            cmds.connectAttr('%s.resultR' % nodeName, '%s.presence' % self.pxr_surface_name, f=True)
        elif key == "subsurfaceColor":
            print "adding specular color texture"
            nodeName = cmds.rename(nodeName, '%s_subsurface_tex' % self.pxr_surface_name)
            cmds.connectAttr('%s.resultRGB' % nodeName, '%s.subsurfaceColor' % self.pxr_surface_name, f=True)

        self.node_names[key] = nodeName

    def update_tex(self, key):
        if self.node_names[key] == "none":
            return
        cmds.setAttr('%s.filename' % self.node_names[key], os.path.join(self.directory, self.textures[key]), type='string')


#MAIN UI LAUNCHER


def showUI():
    ui = SubsTextureManagerUI()
    ui.show()
    return ui
