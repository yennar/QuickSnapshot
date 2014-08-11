#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Settings(QDialog):
    def __init__(self,parent = None):
        QDialog.__init__(self,parent)
        self.settings = QSettings("YennarOpenSource", "QuickSnapshot")
        
    def value(self,key):
        defaultValue = ''
        if key == 'SnapShotSaveDir':
            defaultValue = QDesktopServices.storageLocation(QDesktopServices.DesktopLocation)
            
        return self.settings.value(key,defaultValue).toString()
    
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
        print "Screen count %d" % desktop.screenCount()
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
            
            
        
def showCapture():
    pass

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    s = Settings()
    w = CaptureWin(s)
    w.show()
    app.exec_()