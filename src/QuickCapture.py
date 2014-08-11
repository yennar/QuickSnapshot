#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CaptureWin(QWidget):
    
    def __init__(self,screenId = -1,parent = None):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.SplashScreen)
        desktop = QApplication.desktop()
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
        painter.setBrush(QColor(250,250,250,100))
        painter.drawRect(self.rect())
        
        
        penMouseLine = QPen(QBrush(Qt.yellow),1,Qt.DashLine)
        painter.setPen(penMouseLine)

        
        if self.mouseClicked == False:
            painter.drawLine(self.mousePos.x(),0,self.mousePos.x(),self.rect().height())
            painter.drawLine(0,self.mousePos.y(),self.rect().width(),self.mousePos.y())
        else:
            sx = self.mousePosLeft.x()
            sy = self.mousePosLeft.y()
            ex = self.mousePos.x()
            ey = self.mousePos.y()
            rect = QRect(min(sx,ex),min(sy,ey),abs(sx-ex),abs(sy-ey)) 
            painter.setBrush(QColor(250,250,250,0))
            
            painter.drawRect(rect)             
        
        
        self.update()
    
    def mouseMoveEvent(self,e):
        self.mousePos = e.pos()
        QWidget.mouseMoveEvent(self,e)
    
    def mousePressEvent(self,e):
        if self.mouseClicked == False:
            self.mouseClicked = True
            self.mousePosLeft = e.pos()
        else:
            pass
        
def showCapture():
    pass

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    w = CaptureWin()
    w.show()
    app.exec_()