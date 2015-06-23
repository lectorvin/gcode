import re
import unittest
import timeit
import opengl
import numpy as np
from gradient import main as grad
from pyqtgraph import QtGui, QtCore


MIN_COLOR = [0.0, 0.0, 1.0, 0.9]
MAX_COLOR = [1.0, 0.0, 0.0, 0.9]
current_feedrate = 0
current_color = 0


class GcodeError(Exception):
    """ Exception for invalid g-codes """
    def __init__(self):
        print('Not G-codes')


def getColorLine(dot1, dot2):    # generate all dots of line
    """
    Count dots, which are lies on line.

    Parameters
    ----------
    dot1 : array_like
        Coordinates of the beginning of line (x, y, z)
    dot2 : array_like
        Coordinates of the end of line (x, y, z)

    Returns
    -------
    coords : array of dtype float
        Dots, which are lies on line.

    Notes
    -----
    Return 100 dots
    """
    global current_feedrate, current_color
    x1, y1, z1, feed1 = dot1
    x2, y2, z2, feed2 = dot2
    coords = []
    x = x1
    step = (x2-x1) / 100

    if current_feedrate == 0:
        start_color = MIN_COLOR
        if feed2 > feed1:
            finish_color = MAX_COLOR
        else:
            finish_color = MIN_COLOR
    else:
        if feed2 > feed1:
            start_color = MIN_COLOR
            finish_color = MAX_COLOR
        elif feed1 > feed2:
            start_color = MAX_COLOR
            finish_color = MIN_COLOR
        else:   # feed1 == feed2
            if feed2 == current_feedrate:
                start_color = finish_color = current_color

    current_color = finish_color
    current_feedrate = feed2
    color_list = grad(start_color, finish_color, n=101)

    i = 0
    while x < x2:
        dot = [0, 0, 0, 0, 0, 0, 0]   # x, y, z, r, g, b, p
        dot[0] = x
        dot[1] = float((x-x1)*(y2-y1) / (x2-x1)) + y1
        dot[2] = float((x-x1)*(z2-z1) / (x2-x1)) + z1
        dot[3:7] = color_list[i]
        coords.append(dot)
        x += step
        i += 1

    return coords


class gcode(object):
    """
    Class for gcode object

    Attributes
    ----------
    check : bool
        Check, if value is valid gcode.
    del_comm : string
        Delete all comments from text and return string.
    coordinates : array
        Get all coordinates from text.
    text : string
        Return gcode as string.
    get_dots : array
        Return dots with colors
    saveImage : None
        Save image as gif file

    Parameters
    ----------
    text : string_like
        Gcodes.
    """

    def __init__(self, text):
        self._text = str(text)
        # central value of class
        self.blocks = list(map(str, text.split('\n')))

    def check(self):   # full program
        """ Check if self.blocks contains valid gcode """
        r = re.compile('(?!(^(((?!;)[A-Z][+-]?\d+(\.\d+)?\s?)*(\s*;\s.*)?)$))')
        for line in self.blocks:
            if r.match(line) and line and line!='\r' and line!='\n':
                return False
        return True

    def del_comm(self, blocks=False):
        """ Delete all comments from text """
        if not(self.check()):
            raise GcodeError()
        temp = []
        comment = re.compile(';\ .*')
        for line in self.blocks:
            n = comment.search(line)
            if n:
                line = line[:n.span()[0]]
            line = line.strip()
            if line != "":
                temp.append(line)
        if blocks:
            return temp
        return "\n".join(temp)

    @property
    def coordinates(self):
        """ Return all coordinates from self.blocks """
        result = []
        blocks = list(map(str, self.del_comm().split('\n')))  # FIXME: if not work, delete list
        coor = re.compile('[FXYZ][+-]?[0-9]+(\.[0-9]+)?')
        for line in blocks:
            coord_line = False
            comm = line.split()
            temp = []
            for c in comm:
                if c == 'G1':
                    coord_line = True
                if coord_line and coor.match(c):
                    temp.append(c)
            if temp:
                result.append(temp)
        return result

    @property
    def text(self):
        """ Return gcode as string """
        return self._text

    def get_dots(self):
        """ Generate dots and return them """
        gc = self.coordinates
        coords = []
        zmin = ymin = xmin = self.fmin = 9999
        for line in gc:
            temp = [None, None, None, None]  # X, Y, Z, Feedrate
            for c in line:
                if c.startswith('X'):
                    temp[0] = float(c[1:])
                    xmin = min(xmin, temp[0])
                elif c.startswith('Y'):
                    temp[1] = float(c[1:])
                    ymin = min(ymin, temp[1])
                elif c.startswith('Z'):
                    temp[2] = float(c[1:])
                    zmin = min(zmin, temp[2])
                elif c.startswith('F'):
                    temp[3] = float(c[1:])
                    self.fmin = min(self.fmin, temp[3])
            if ((temp[0] is not None) or (temp[1] is not None) or
               (temp[2] is not None) or (temp[3] is not None)):
                try:
                    if temp[0] is None:
                        temp[0] = coords[-1][0]
                except IndexError:
                    pass
                try:
                    if temp[1] is None:
                        temp[1] = coords[-1][1]
                except IndexError:
                    pass
                try:
                    if temp[2] is None:
                        temp[2] = coords[-1][2]
                except IndexError:
                    pass
                try:
                    if temp[3] is None:
                        temp[3] = coords[-1][3]
                except IndexError:
                    pass
                coords.append(temp)

        for i in coords:   # if something is still 0
            if i[0] is None:
                i[0] = xmin * 2  # min*2 - min
            if i[1] is None:
                i[1] = ymin * 2
            if i[2] is None:
                i[2] = zmin * 2
            if i[3] is None:
                i[3] = self.fmin * 2
            i[0] -= xmin
            i[1] -= ymin
            i[2] -= zmin
            i[3] -= self.fmin

        dots = []
        for i in range(len(coords)):
            temp = []
            if i != len(coords)-1:
                temp = getColorLine(coords[i], coords[i+1])
            if temp:
                for y in temp:
                    dots.append(y)

        return dots

    def saveImage(self):
        dots = np.array(self.get_dots())
        print(str(len(dots))+" to draw")
        data = dots[:, :3]
        colors = dots[:, 3:]
        if len(dots):
            data = np.array([[x-40 for x in i] for i in data])
            a = opengl.App(data, colors)
            if __name__ == "__main__":
                test = 1
            else:
                test = 0
            a.main(test)


if __name__ == "__main__":
    import sys
    import glob


    class Test(unittest.TestCase):
        gcodes = glob.glob("gcodes/*")
        def test_a(self):
            self.assertFalse(gcode('asdf').check())

        def test_b(self):
            with open(self.gcodes[0]) as f:
                self.assertTrue(gcode(f.read()).check())

        def test_c(self):
            with open(self.gcodes[1]) as f:
                self.assertTrue(gcode(f.read()).check())

        def test_d(self):
            with open(self.gcodes[2]) as f:
                self.assertTrue(gcode(f.read()).check())


    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print('1.000.000 checked codes - ' + str(timeit.timeit(gcode('G1').check,
                                             number=1000000)))
    a = QtGui.QApplication(sys.argv)
    print('1 generated image - ' + str(timeit.timeit(gcode(
                           'G1 X1\nG1 Y1\nG1 X2 Y3 Z10').saveImage, number=1)))
