import sys
import pyqtgraph.opengl as gl

from pyqtgraph.Qt import QtGui   # , QtCore


class App(QtGui.QWidget):
    def __init__(self, data, colors, parent=None):
        QtGui.QWidget.__init__(self, parent)
        w = gl.GLViewWidget()
        w.setCameraPosition(distance=150)
        w.show()
        w.setWindowTitle('G-codes')

        self.plt = gl.GLLinePlotItem()
        self.data = data
        self.colors = colors
        self.n = 0
        self.timer = 0   # QtCore.QTimer(self)
        '''
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.draw_image)
        '''
        w.addItem(self.plt)

    def main(self):
        print('start')
        wtf()

    def draw_image(self):
        if self.n > len(self.data):
            pass
        else:
            if self.n % 100 == 0:
                print(self.n)
            self.n += 1
            self.plt.setData(pos=self.data[:self.n], color=self.colors[:self.n])


if __name__ == "__main__":
    import numpy as np

    dots = np.array(([0, 0, 0],
                    [2, 0, 0],
                    [2, 1, 0],
                    [2.5, 1, 0],
                    [2.5, -1, 0],
                    [3, -1, 0],
                    [3, 0, 0],
                    [6, 0, 0]))
    a = QtGui.QApplication(sys.argv)
    app = App(dots, [0, 1, 0, 1])
    app.main()
    a.exec_()
