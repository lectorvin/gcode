# opengl.py
#!/usr/bin/python
import sys
import logging
import pyqtgraph.opengl as gl

from pyqtgraph.Qt import QtGui, QtCore


log = "log.log"
logging.basicConfig(
    format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s %(message)s',
    level=logging.DEBUG, filename=log)


class App(gl.GLViewWidget):
    def __init__(self, data, colors, time=0):
        gl.GLViewWidget.__init__(self)
        self.data = data
        self.colors = colors
        self.time = time
        self.n = 0
        self.run = 0

        self.setCameraPosition(distance=150)
        self.setWindowTitle('G-codes')

        self.plt = gl.GLLinePlotItem()
        self.addItem(self.plt)

        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"),
                     self.draw_image)

    def show_image(self):
        self.plt.setData(pos=self.data, color=self.colors)
        self.show()

    def drawing(self):
        logging.debug('Start drawing')
        self.show()
        self.timer.start(self.time)
        self.run = 1

    def draw_image(self):
        if self.run:
            if self.n > len(self.data):
                pass
            else:
                if self.n % 1000 == 0 and self.n:
                    logging.debug("drawed {} dots".format(self.n))
                self.n += 1
                self.plt.setData(pos=self.data[:self.n],
                                 color=self.colors[:self.n])

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            logging.debug("Pause drawing")
            self.run = not(self.run)
        elif event.key() == QtCore.Qt.Key_Escape:
            logging.debug("Press esc")
            self.timer.stop()
            self.close()
        else:
            logging.debug("Press key: "+str(event.key()))

    def closeEvent(self, event):
        logging.debug("Quit")
        self.timer.stop()
        event.accept()


if __name__ == "__main__":
    import numpy as np
    from gradient import main as grad

    with open(log, 'w') as f:
        pass
    logging.debug('Test file')
    dots = np.array(([0, 0, 0],
                    [2, 0, 0],
                    [2, 1, 0],
                    [2.5, 1, 0],
                    [2.5, -1, 0],
                    [3, -1, 0],
                    [3, 0, 0],
                    [6, 0, 0]))
    colors = np.array(grad(n=8))
    a = QtGui.QApplication(sys.argv)
    app = App(dots, colors, 1000)
    app.main()
    a.exec_()
    logging.debug('Test ends')
