import re
import unittest
import timeit
import opengl
import numpy as np
from gradient import main as grad


COLOR_MIN = [0.0, 0.0, 1.0, 0.9]
COLOR_MAX = [1.0, 0.0, 0.0, 0.9]
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
        start_color = COLOR_MIN
        if feed2 > feed1:
            finish_color = COLOR_MAX
        else:
            finish_color = COLOR_MIN
    else:
        if feed2 > feed1:
            start_color = COLOR_MIN
            finish_color = COLOR_MAX
        elif feed1 > feed2:
            start_color = COLOR_MAX
            finish_color = COLOR_MIN
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
            if r.match(line):
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
        blocks = map(str, self.del_comm().split('\n'))
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
        """ Generate dots and return them
        """
        gc = self.coordinates
        coords = []
        zmax = ymax = xmax = self.fmax = 0
        zmin = ymin = xmin = self.fmin = 9999
        for line in gc:
            temp = [None, None, None, None]  # X, Y, Z, Feedrate
            for c in line:
                if c.startswith('X'):
                    temp[0] = float(c[1:])
                    xmax = max(xmax, temp[0])
                    xmin = min(xmin, temp[0])
                elif c.startswith('Y'):
                    temp[1] = float(c[1:])
                    ymax = max(ymax, temp[1])
                    ymin = min(ymin, temp[1])
                elif c.startswith('Z'):
                    temp[2] = float(c[1:])
                    zmax = max(zmax, temp[2])
                    zmin = min(zmin, temp[2])
                elif c.startswith('F'):
                    temp[3] = float(c[1:])
                    self.fmax = max(self.fmax, temp[3])
                    self.fmin = min(self.fmin, temp[3])
            if ((temp[0] != None) or (temp[1] != None) or (temp[2] != None) or
               (temp[3] != None)):
                try:
                    if temp[0] == None:
                        temp[0] = coords[-1][0]
                except IndexError:
                    pass
                try:
                    if temp[1] == None:
                        temp[1] = coords[-1][1]
                except IndexError:
                    pass
                try:
                    if temp[2] == None:
                        temp[2] = coords[-1][2]
                except IndexError:
                    pass
                try:
                    if temp[3] == None:
                        temp[3] = coords[-1][3]
                except IndexError:
                    pass
                coords.append(temp)

        for i in coords:   # if something is still 0
            if i[0] == None:
                i[0] = xmin * 2  # min*2 - min
            if i[1] == None:
                i[1] = ymin * 2
            if i[2] == None:
                i[2] = zmin * 2
            if i[3] == None:
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
        print(len(dots))
        data = dots[:, :3]
        colors = dots[:, 3:]
        if len(dots):
            data = np.array([[x-40 for x in i] for i in data])
            a = opengl.App(data, colors)
            a.main()


if __name__ == "__main__":
    import sys
    from pyqtgraph.Qt import QtGui, QtCore

    class Test(unittest.TestCase):
        def testa_5(self): self.assertFalse(gcode('asdf').check())

        def testb_2(self): self.assertTrue(gcode('G1 X1.1 ; asdf').check())

        def testc_1(self): self.assertTrue(gcode('').check())

        def testd_one(self): self.assertTrue(gcode(
             '; generated by Slic3r\nG21 ; set units to millimeters').check())

        def teste_big(self): self.assertTrue(gcode(
            "M107\nM104 S200 ; set temperature\nG28 ; home all axes").check())

        def testf_piece(self): self.assertTrue(gcode(
            'G1 Z5 F5000 ; lift nozzle\n\nM109 S200 ; wait for temp').check())

        def testg_of(self): self.assertTrue(gcode(
                'N1 G90 ; use absolute\nM82 ; use absolute distance').check())

        def testh_gcode(self): self.assertTrue(gcode(
               'G1 F1800.000 E-1.00000\nG92 E0\nG1 Z0.500 F7800.000').check())

        def testi_generated(self): self.assertTrue(gcode(
                 'G1 X91.746 Y93.225 F7800.000\nG1 E1.000 F1800.000').check())

        def testj_by(self): self.assertTrue(gcode(
            'G1 X93.7 Y92.57 E1.4774 F600.00\nG1 X96.07 Y91.63 E1.3').check())

        def testk_Slic3r(self): self.assertTrue(gcode(
             'M106 S255\nG1 F1800.000 E2.99327\nG1 Z0.900 F7800.000').check())

        def testl_is(self): self.assertTrue(gcode(
                        'G1 Z12.900 F7800.000\nG1 Z13.700 F7800.000').check())

        def testm_absolutely(self): self.assertTrue(gcode(
                              'M107\nM104 S0 ; turn off temperature').check())

        def testn_correct(self): self.assertTrue(gcode(
                        'G28 X0 ; home X axis\nM84 ; disable motors').check())

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print('1.000.000 checked codes - ' + str(timeit.timeit(gcode('G1').check,
                                             number=1000000)))
    a = QtGui.QApplication(sys.argv)
    print('1 generated image - ' + str(timeit.timeit(gcode(
                           'G1 X1\nG1 Y1\nG1 X2 Y3 Z10').saveImage, number=1)))
