#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pygs import QxtGlobalShortcut

import ui_res

class Settings(QObject):
    def __init__(self,parent = None):
        QObject.__init__(self,parent)
        self.settings = QSettings("YennarOpenSource", "QuickSnapshot")
        
    def value(self,key):
        defaultValue = ''
        if key == 'SnapShotSaveDir':
            defaultValue = QDesktopServices.storageLocation(QDesktopServices.DesktopLocation)
        if key == 'SnapShotKey':
            defaultValue = QKeySequence(Qt.SHIFT | Qt.CTRL | Qt.Key_A).toString()
        return self.settings.value(key,defaultValue)
    
    def setValue(self,key,value):
        self.settings.setValue(key,value)
        self.settings.sync()
        
class CaptureWin(QWidget):
    
    captureDone = pyqtSignal(str)
    
    def __init__(self,settings,screenId = -1,parent = None):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.SplashScreen)
        desktop = QApplication.desktop()
        self.settings = settings
        #print "Screen count %d" % desktop.screenCount()
        if screenId == -1:
            screenId = desktop.primaryScreen()
        
        desktop_widget = desktop.screen(screenId)
        self.geo = desktop.screenGeometry(screenId)
        self.resize(self.geo.width(),self.geo.height())
        self.move(self.geo.x(),self.geo.y())
        self.originalPixmap = QPixmap.grabWindow(desktop_widget.winId())
        self.setMouseTracking(True)
        self.mousePos = QPoint(0,0)
        self.mousePosLeft = QPoint(0,0)
        self.mouseClicked = False
        

    
    def paintEvent(self,e):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(),self.originalPixmap,self.geo)

        
        
        penMouseLine = QPen(QBrush(Qt.yellow),1,Qt.DashLine)
        painter.setPen(penMouseLine)

        
        if self.mouseClicked == False:
            painter.setBrush(QColor(250,250,250,100))
            painter.drawRect(self.rect())            
            painter.drawLine(self.mousePos.x(),0,self.mousePos.x(),self.rect().height())
            painter.drawLine(0,self.mousePos.y(),self.rect().width(),self.mousePos.y())
        else:
            sx = self.mousePosLeft.x()
            sy = self.mousePosLeft.y()
            ex = self.mousePos.x()
            ey = self.mousePos.y()
            d1x = min(sx,ex)
            d1y = min(sy,ey)
            dw = abs(sx-ex)
            dh = abs(sy-ey)
            d2x = d1x + dw
            d2y = d1y + dh
            rx = self.rect().width()
            ry = self.rect().height()
            rect = QRect(d1x,d1y,dw,dh)
            self.snaprect = rect
            painter.drawRect(rect)     
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(250,250,250,100))
            painter.drawRect(QRect(0,0,d1x,ry)) 
            painter.drawRect(QRect(d2x,0,rx - d2x,ry)) 
            painter.drawRect(QRect(d1x,0,dw,d1y))
            painter.drawRect(QRect(d1x,d1y + dh,dw,ry - d2y))
        
        self.update()

    def keyReleaseEvent(self,e):
        if e.key() == Qt.Key_Escape:
            if self.mouseClicked == False:
                self.close()
            else:
                self.mouseClicked = False
        QWidget.keyReleaseEvent(self,e)
    
    def mouseMoveEvent(self,e):
        self.mousePos = e.pos()
        QWidget.mouseMoveEvent(self,e)
    
    def mousePressEvent(self,e):
        if self.mouseClicked == False:
            self.mouseClicked = True
            self.mousePosLeft = e.pos()
        else:
            saveDir = self.settings.value('SnapShotSaveDir')
            d = QDateTime.currentDateTime()
            saveFileName = 'Snapshot-' + d.toString('yyyy_MM_dd_hh_mm_ss') + '.png'
            image = self.originalPixmap.copy(self.snaprect)
            saveFileFull = saveDir + '/' + saveFileName
            image.save(saveFileFull)
            self.captureDone.emit(saveFileFull)
            self.close()
            
class QXShortCutKeyConfigureDialog(QDialog):
    def __init__(self,keySeqCurrent,iconMain,parent = None):
        QDialog.__init__(self,parent)
        
        self.lblIcon = QLabel()
        self.lblIcon.setFrameStyle(QFrame.NoFrame)
        self.lblIcon.setPixmap(QPixmap(iconMain))
        
        self.lblInfo = QLabel()
        self.lblInfoText = "Please press new key sequence"
        self.lblInfo.setText(self.lblInfoText)
        layInfo = QHBoxLayout()
        layInfo.addWidget(self.lblIcon)
        layInfo.addWidget(self.lblInfo)
        
        self.btnBoxes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btnBoxes.button(QDialogButtonBox.Ok).setEnabled(False)
        self.btnBoxes.accepted.connect(self.onAccept)
        self.btnBoxes.rejected.connect(self.close)
        
        layMain = QVBoxLayout()
        layMain.addLayout(layInfo)
        layMain.addWidget(self.btnBoxes)
        self.setLayout(layMain)
        
        self.tmr = QTimer()
        self.tmr.setInterval(700)
        self.tmr.timeout.connect(self.onTimeOut)
        self.lblInfoShow = True

        self.keySet = False
        
        self.tmr.start()
        self.grabKeyboard()
        self.key = None
        
    def onTimeOut(self):
        
        if not self.keySet:
            self.lblInfoShow = not self.lblInfoShow 
            
            if self.lblInfoShow:
                self.lblInfo.setText(self.lblInfoText)
            else:
                self.lblInfo.clear()
        else:
            pass
    def closeEvent(self,e):
        self.releaseKeyboard()
        e.accept()
        
    def keyPressEvent(self,e):
        self.seq = QKeySequence(e.modifiers() | e.key())
        self.keySet = True
        self.lblInfo.setText(self.seq.toString())
        self.btnBoxes.button(QDialogButtonBox.Ok).setEnabled(True)
        
    def onAccept(self):
        self.key = self.seq.toString()
        self.close()

        
class MainController(QSystemTrayIcon):
    
    appExit = pyqtSignal()
    
    def __init__(self,icon,settings,parent = None):
        self.settings = settings
        QSystemTrayIcon.__init__(self,icon,parent)
        self.mainMenu = QMenu()
        self.actCapture = QAction(QIcon(":/config.png"),"Capture",self,triggered=self.onCapture)

        self.actCapture.setShortcut(QKeySequence.fromString(settings.value('SnapShotKey')))
        self.mainMenu.addAction(self.actCapture)
        
        self.mainMenu.addAction(QAction("Set save directory...",self,triggered=self.onSetSavePath))
        self.mainMenu.addAction(QAction("Set shortcut...",self,triggered=self.onConfigureShortCut))
        
        self.mainMenu.addAction(QAction("Exit",self,triggered=self.onExit))
        self.setContextMenu(self.mainMenu)
        self.activated.connect(self.onActived)
        
        self.gsKey = QxtGlobalShortcut()
        self.gsKey.setShortcut(QKeySequence.fromString(settings.value('SnapShotKey')))
        self.gsKey.activated.connect(self.onCapture)
        
    def onActived(self,r):
        if r == QSystemTrayIcon.Trigger:
            self.onClick()
        elif r == QSystemTrayIcon.DoubleClick:
            self.onCapture()
        
    def onCapture(self):
        self.w = CaptureWin(self.settings)
        self.w.captureDone.connect(self.onCaptureMessage)
        self.w.show()   
        
    def onClick(self):
        self.showMessage("meo~","Press %s to capture" % self.settings.value('SnapShotKey'),QSystemTrayIcon.Information,50)
        
    def onConfigureShortCut(self):
        c = QXShortCutKeyConfigureDialog(self.settings.value('SnapShotKey'), ":/help.png")
        c.windowTitle = 'QuickCapture'
        c.exec_()
        if not c.key is None:
            self.settings.setValue('SnapShotKey',c.key)
            del self.gsKey
            self.gsKey = QxtGlobalShortcut()
            self.gsKey.setShortcut(QKeySequence.fromString(self.settings.value('SnapShotKey')))
            self.gsKey.activated.connect(self.onCapture)   
            self.actCapture.setShortcut(QKeySequence.fromString(self.settings.value('SnapShotKey')))
        
    def onSetSavePath(self):
        d = QFileDialog.getExistingDirectory(None,"Open Directory",
            QDesktopServices.storageLocation(QDesktopServices.HomeLocation),QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if (not d is None) and (not d == '') and (QDir().exists(d)):
            self.settings.setValue('SnapShotSaveDir',d)
            self.showMessage("QuickCapture","Set save directory to %s" % d,QSystemTrayIcon.Information,50)
            
    def onCaptureMessage(self,s):
        self.showMessage("QuickCapture","Capture screen snapshot to %s" % s,QSystemTrayIcon.Information,50)
         
    def onExit(self):
        del self.gsKey
        QApplication.exit(0)

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    s = Settings()
    mainController = MainController(QIcon(":/trayicon.png"),s)
    mainController.appExit.connect(app.quit)
    
    mainController.show()
    
    #

    app.exec_()