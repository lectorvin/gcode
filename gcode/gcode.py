# gcode.py
#!/usr/bin/python
import re
import logging
import opengl
import numpy as np
from gradient import main as grad
from pyqtgraph import QtGui


log = "log.log"
logging.basicConfig(
    format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s %(message)s',
    level=logging.DEBUG, filename=log)
MIN_COLOR = [0.0, 0.0, 1.0, 1.0]
MAX_COLOR = [1.0, 0.0, 0.0, 1.0]


class GcodeError(Exception):
    """ Exception for invalid g-codes """
    def __init__(self, message):
        self.message = message
        logging.error(self.message)


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
    current_feedrate = 0
    current_color = 0
    speed = 50  # not speed, 1/speed

    def __init__(self, text):
        self._text = str(text)
        # central value of class
        self.blocks = list(map(str, text.split('\n')))

    def check(self):   # full program
        """ Check if self.blocks contains valid gcode """
        r = re.compile('(?!(^(((?!;)[A-Z][+-]?\d+(\.\d+)?\s?)*(\s*;\s.*)?)$))')
        for line in self.blocks:
            if r.match(line) and line and line != '\r' and line != '\n':
                return False
        return True

    def del_comm(self, blocks=False):
        """ Delete all comments from text """
        logging.debug('Delete comments from text')
        if not(self.check()):
            raise GcodeError("Invalid g-codes")
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
        logging.debug('Get coordinates from text')
        result = []
        blocks = self.del_comm(blocks=True)
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
        logging.debug('Generate dots to draw')
        gc = self.coordinates
        coords = []
        zmin = ymin = xmin = self.fmin = 999999
        self.fmax = 0
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
                    temp[3] = int(float(c[1:]))
                    self.fmin = min(self.fmin, temp[3])
                    self.fmax = max(self.fmax, temp[3])
            if ((temp[0] is not None) or (temp[1] is not None) or
               (temp[2] is not None) or (temp[3] is not None)):
                if coords:
                    if temp[0] is None:
                        temp[0] = coords[-1][0]
                    if temp[1] is None:
                        temp[1] = coords[-1][1]
                    if temp[2] is None:
                        temp[2] = coords[-1][2]
                    if temp[3] is None:
                        temp[3] = coords[-1][3]
                coords.append(temp)

        if (self.fmin == 999999) or (self.fmax == 0):
            raise GcodeError('Please check feedrate')
        if (xmin == ymin == zmin == 999999):
            raise GcodeError('Please check coordinates')
        if xmin == 999999:
            xmin = 0
        if ymin == 999999:
            ymin = 0
        if zmin == 999999:
            zmin = 0

        for i in coords:   # if something is still 0
            if i[0] is None:
                i[0] = xmin
            if i[1] is None:
                i[1] = ymin
            if i[2] is None:
                i[2] = zmin
            if i[3] is None:
                i[3] = self.fmin
            i[0] -= xmin
            i[1] -= ymin
            i[2] -= zmin
            i[3] -= self.fmin

        self.fmax -= self.fmin
        self.colors_list = grad(MIN_COLOR, MAX_COLOR, self.fmax+1)

        dots = []
        for i in range(len(coords)):
            temp = []
            if i != len(coords)-1:
                temp = self.getColorLine(coords[i], coords[i+1])
            if temp:
                dots.extend(temp)

        return dots

    def get_data(self):
        logging.debug('Get data')
        dots = np.array(self.get_dots())
        data = dots[:, :3]
        colors = dots[:, 3:]
        if len(dots):
            data = np.array([[x-40 for x in i] for i in data])

        return data, colors

    def drawing(self):
        data, colors = self.get_data()
        logging.debug(str(len(data))+" dots to draw")
        a = opengl.App(data, colors)
        a.drawing()

    def show_image(self):
        data, colors = self.get_data()
        logging.debug(str(len(data))+" dots to show")
        a = opengl.App(data, colors)
        a.show_image()

    def getColorLine(self, dot1, dot2):    # generate all dots of line
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
        Return {self.speed} dots
        """
        x1, y1, z1, feed1 = dot1
        x2, y2, z2, feed2 = dot2
        min_color = self.colors_list[feed1]
        max_color = self.colors_list[feed2]

        # NB! feed1,feed2 >= 0; 0 = dot[3]-fmin
        # self.colors_list = grad(MIN_COLOR, MAX_COLOR, self.fmax)
        if self.current_feedrate == 0:
            start_color = min_color
            if feed2 > feed1:
                finish_color = max_color
            else:
                finish_color = min_color
        else:
            if feed2 > feed1:
                start_color = min_color
                finish_color = max_color
            elif feed1 > feed2:
                start_color = max_color
                finish_color = min_color
            else:   # feed1 == feed2
                if feed2 == self.current_feedrate:
                    start_color = finish_color = self.current_color

        self.current_color = finish_color
        self.current_feedrate = feed2
        color_list = grad(start_color, finish_color, n=self.speed+1)

        i = 0
        coords = []
        stepx = (x2-x1) / self.speed
        stepy = (y2-y1) / self.speed
        stepz = (z2-z1) / self.speed
        for i in range(self.speed):
            dot = [0, 0, 0, 0, 0, 0, 0]   # x, y, z, r, g, b, p
            dot[0] = x1 + i*stepx
            dot[1] = y1 + i*stepy
            dot[2] = z1 + i*stepz
            dot[3:7] = color_list[i]
            coords.append(dot)

        return coords


if __name__ == "__main__":
    import unittest
    import timeit
    import sys
    import glob

    with open(log, 'w') as f:
        pass
    logging.debug('Test file')

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

        def test_d(self):
            with open(self.gcodes[3]) as f:
                self.assertTrue(gcode(f.read()).check())

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print('1.000.000 checked codes - ' +
          str(timeit.timeit(gcode('G1').check, number=1000000)))
    a = QtGui.QApplication(sys.argv)
    print('1 generated image - ' +
          str(
              timeit.timeit(gcode(
                  'G1 X1 F100\nG1 Y1 F120\nG1 X2 Y3 Z10 F200').show_image,
                            number=1))
          )
    logging.debug('Test ends')
