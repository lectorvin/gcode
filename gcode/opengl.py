import sys
import pyqtgraph.opengl as gl

from pyqtgraph.Qt import QtGui, QtCore


class StartException(Exception):
    def __init__(self):
        print('drawing starts NOW!')


class App(QtGui.QWidget):
    def __init__(self, data, colors, time=0, parent=None):
        QtGui.QWidget.__init__(self, parent)
        w = gl.GLViewWidget()
        w.setCameraPosition(distance=150)
        w.show()
        w.setWindowTitle('G-codes')

        self.plt = gl.GLLinePlotItem()
        w.addItem(self.plt)

        self.data = data
        self.colors = colors
        self.n = 0

        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.draw_image)
        self.timer.start(time)

    def main(self, test=0):
        print('start')
        if not(test):
            raise StartException()

    def draw_image(self):
        try:
            if self.n > len(self.data):
                pass
            else:
                self.n += 1
                self.plt.setData(pos=self.data[:self.n],
                                 color=self.colors[:self.n])
        except KeyboardInterrupt:
            self.close()


if __name__ == "__main__":
    import numpy as np
    from gradient import main as grad
    from pyqtgraph.Qt import QtCore

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
    app.main(1)
    a.exec_()
