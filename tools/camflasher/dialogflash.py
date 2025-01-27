# Form implementation generated from reading ui file 'dialogflash.ui'
#
# Created by: PyQt6 UI code generator 6.2.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_dialog_flash(object):
    def setupUi(self, dialog_flash):
        dialog_flash.setObjectName("dialog_flash")
        dialog_flash.resize(438, 218)
        self.gridLayout = QtWidgets.QGridLayout(dialog_flash)
        self.gridLayout.setObjectName("gridLayout")
        self.label_firmware = QtWidgets.QLabel(dialog_flash)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_firmware.sizePolicy().hasHeightForWidth())
        self.label_firmware.setSizePolicy(sizePolicy)
        self.label_firmware.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_firmware.setObjectName("label_firmware")
        self.gridLayout.addWidget(self.label_firmware, 0, 0, 1, 1)
        self.firmware_layout = QtWidgets.QHBoxLayout()
        self.firmware_layout.setObjectName("firmware_layout")
        self.firmware = QtWidgets.QLineEdit(dialog_flash)
        self.firmware.setObjectName("firmware")
        self.firmware_layout.addWidget(self.firmware)
        self.select_firmware = QtWidgets.QPushButton(dialog_flash)
        self.select_firmware.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.select_firmware.sizePolicy().hasHeightForWidth())
        self.select_firmware.setSizePolicy(sizePolicy)
        self.select_firmware.setAcceptDrops(True)
        self.select_firmware.setObjectName("select_firmware")
        self.firmware_layout.addWidget(self.select_firmware)
        self.gridLayout.addLayout(self.firmware_layout, 1, 0, 1, 2)
        self.label_baud = QtWidgets.QLabel(dialog_flash)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_baud.sizePolicy().hasHeightForWidth())
        self.label_baud.setSizePolicy(sizePolicy)
        self.label_baud.setMaximumSize(QtCore.QSize(16777215, 16777213))
        self.label_baud.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.label_baud.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_baud.setObjectName("label_baud")
        self.gridLayout.addWidget(self.label_baud, 2, 0, 1, 1)
        self.baud_layout = QtWidgets.QHBoxLayout()
        self.baud_layout.setObjectName("baud_layout")
        self.baud = QtWidgets.QComboBox(dialog_flash)
        self.baud.setEnabled(True)
        self.baud.setMinimumSize(QtCore.QSize(150, 0))
        self.baud.setObjectName("baud")
        self.baud_layout.addWidget(self.baud)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.baud_layout.addItem(spacerItem)
        self.gridLayout.addLayout(self.baud_layout, 3, 0, 1, 2)
        self.erase = QtWidgets.QCheckBox(dialog_flash)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.erase.sizePolicy().hasHeightForWidth())
        self.erase.setSizePolicy(sizePolicy)
        self.erase.setObjectName("erase")
        self.gridLayout.addWidget(self.erase, 4, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem1, 5, 1, 1, 1)
        self.button_box = QtWidgets.QDialogButtonBox(dialog_flash)
        self.button_box.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.button_box.setObjectName("button_box")
        self.gridLayout.addWidget(self.button_box, 6, 0, 1, 2)

        self.retranslateUi(dialog_flash)
        self.button_box.accepted.connect(dialog_flash.accept) # type: ignore
        self.button_box.rejected.connect(dialog_flash.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(dialog_flash)
        dialog_flash.setTabOrder(self.firmware, self.select_firmware)
        dialog_flash.setTabOrder(self.select_firmware, self.baud)
        dialog_flash.setTabOrder(self.baud, self.erase)

    def retranslateUi(self, dialog_flash):
        _translate = QtCore.QCoreApplication.translate
        dialog_flash.setWindowTitle(_translate("dialog_flash", "Flash firmware"))
        self.label_firmware.setText(_translate("dialog_flash", "Firmware"))
        self.firmware.setToolTip(_translate("dialog_flash", "Enter firmware file"))
        self.select_firmware.setToolTip(_translate("dialog_flash", "Select firmware file"))
        self.select_firmware.setText(_translate("dialog_flash", "..."))
        self.label_baud.setText(_translate("dialog_flash", "Baud rate"))
        self.baud.setToolTip(_translate("dialog_flash", "Select flash baud rate"))
        self.erase.setToolTip(_translate("dialog_flash", "Check to erase the flash content before write firmware"))
        self.erase.setText(_translate("dialog_flash", "Erase flash"))
