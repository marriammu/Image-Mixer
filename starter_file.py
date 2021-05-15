from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtWidgets import QMessageBox
from mixer import Ui_MainWindow
from components import inputimg
import sys
import cv2
import numpy as np
import os
import logging

logging.basicConfig(level=logging.DEBUG,
                    filename="History.log",
                    format='%(lineno)s - %(levelname)s - %(message)s',
                    filemode='w')
logger = logging.getLogger()


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 
        self.count=-1
        self.counter=-1
        self.counter2=-1
        self.data=[]
        self.paths=[]
        self.Size=[]
        self.imgdata=[]
        self.ui.actionOpen1.triggered.connect(lambda:self.opensignal())
        self.ui.img1_combo.currentTextChanged.connect(lambda:self.Components(2))
        self.ui.img2_combo.currentTextChanged.connect(lambda:self.Components(3))
        self.ui.component1_type.currentTextChanged.connect(lambda:self.setcombotext(self.ui.component1_type.currentText()))
        self.ui.component2_type.currentTextChanged.connect(lambda:self.Mixer())
        self.ui.component1_type.currentTextChanged.connect(lambda:self.Mixer()) 
        self.ui.component1_img.currentTextChanged.connect(lambda:self.Mixer())
        self.ui.component2_img.currentTextChanged.connect(lambda:self.Mixer())
        self.ui.component1_slider.valueChanged.connect(lambda:self.Mixer())
        self.ui.component2_slider.valueChanged.connect(lambda:self.Mixer())

    def readsignal(self):
        logger.info("Browsing image ...")
        self.fname=QtGui.QFileDialog.getOpenFileName(self,' Open File',os.getenv('home'),"jpg(*.jpg) ;; jpeg(*.jpeg) ")
        self.path=self.fname[0]
        self.img= cv2.imread(self.path,0)
        self.height, self.width = self.img.shape
        if (self.path):
           logger.info(" Browsed Successfully ! ")
        else:
            logger.warning(" No image to open ")
    def opensignal(self) : 
        
        self.readsignal()
        if (len(self.imgdata)!=0 and(self.width != self.Size[0] or self.height !=self.Size[1]) )   :
            
            QMessageBox.about(self,"Error !","Please Choose Another image with the same dimensions")
            logger.warning("Opened Image with different dimensions ...")
        else:
            self.count+=1
            self.ui.images[self.count%2].clear()
            if(len(self.imgdata)==2):
                self.imgdata=[]
                self.Size=[]

            print(self.imgdata)
            print(self.Size)

            self.imgdata.append(inputimg(self.path))
            print(self.width)
            print(self.height)
            self.ui.enable[self.count%2].setEnabled(True)
            self.Size.append(self.width)
            self.Size.append(self.height)
            self.ui.images[self.count%2].setImage((self.imgdata[self.count%2].img).T)
            self.ui.images[self.count%2].view.setAspectLocked(False)
            logger.info(f" Opening image {1+self.count%2} ...")
        
        if (len(self.imgdata)==2):
            for i in range (1,9):
                self.ui.enable[i].setEnabled(True)
    # def Reset(self):
              

    def Components(self,number):
        imageComponetns=[self.ui.img1_combo.currentText(),self.ui.img2_combo.currentText()]
        component=[0,0]
        component[number-2]=self.imgdata[number-2].components[imageComponetns[number-2]]
        logger.info(f" Presenting {imageComponetns[number-2]}.... ")

        self.ui.images[number].setImage(component[number-2].T)
        self.ui.images[number].view.setAspectLocked(False)
        
    def Mixer(self):
        ratio=[self.ui.component1_slider.value()/100, self.ui.component2_slider.value()/100]
        component=[self.ui.component1_type.currentText(),self.ui.component2_type.currentText()]
        image=[int(self.ui.component1_img.currentText()[-1])-1,int(self.ui.component2_img.currentText()[-1])-1]
        Mix=[0,0]
        MagnitudeIndex=0
        PhaseIndex=1
        if component[0]=="Real" or component[0]=="Imaginary":
            for i in range(2):
                Mix[i]= ratio[i]*self.imgdata[image[i]].Components[component[i]] + (1-ratio[i])*self.imgdata[1-image[i]].Components[component[i]]
            MixInverse= np.real(np.fft.ifft2(Mix[0]+Mix[1]))
            # print(mixInverse)
            
        else:
            if component[0]=="Phase" or component[0]=="Uniphase":
                MagnitudeIndex=1
                PhaseIndex=0
            Mix[PhaseIndex]=np.exp(1j*(ratio[PhaseIndex]*self.imgdata[image[PhaseIndex]].Components[component[PhaseIndex]]+(1-ratio[PhaseIndex])*self.imgdata[1-image[PhaseIndex]].Components[component[PhaseIndex]]))
            Mix[MagnitudeIndex]=(ratio[MagnitudeIndex]*self.imgdata[image[MagnitudeIndex]].Components[component[MagnitudeIndex]])+((1-ratio[MagnitudeIndex])*self.imgdata[1-image[MagnitudeIndex]].Components[component[MagnitudeIndex]])
            MixInverse=np.real(np.fft.ifft2(Mix[0]*Mix[1]))
        self.ui.images[int(self.ui.output_channel.currentText()[-1])+3].setImage(MixInverse.T)
       

    def setcombotext(self, type1):
        self.ui.component2_type.clear()
        if (type1 == "Magnitude" or type1 =="Unimagnitude"):
            self.ui.component2_type.addItem("Phase")
            self.ui.component2_type.addItem("Uniphase")
            self.ui.component2_type.setCurrentText("Phase")
        elif (type1 == "Phase" or type1== "Uniphase"):
            self.ui.component2_type.addItem("Magnitude")
            self.ui.component2_type.addItem("Unimagnitude")
            self.ui.component2_type.setCurrentText("Magnitude")
        elif type1 == "Real":
            self.ui.component2_type.addItem("Imaginary")
            self.ui.component2_type.setCurrentText("Imaginary")
        elif type1 == "Imaginary":
            self.ui.component2_type.addItem("Real")
            self.ui.component2_type.setCurrentText("Real")


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()
