import sys
import pyqtgraph.opengl as gl

from pyqtgraph.Qt import QtGui

class App(QtGui.QWidget):
    def __init__(self, dots, parent=None):
        QtGui.QWidget.__init__(self, parent)
        w = gl.GLViewWidget()
        w.opts['distance'] = 40
        w.show()
        w.setWindowTitle('G-codes')

        self.plt = gl.GLLinePlotItem()
        w.addItem(self.plt)

        self.dots = dots

    def main(self):
        self.plt.setData(pos=self.dots)
        self.show()


if __name__ == "__main__":
    import numpy as np

    dots = np.array(([0, 0, 0],
                    [2, 0, 0],
                    [2, 1, 0],
                    [2.5, 1, 0],
                    [2.5, -1, 0],
                    [3, -1, 0],
                    [3, 0, 0]))
    a = QtGui.QApplication(sys.argv)
    app = App(dots)
    app.main()
    a.exec_()
