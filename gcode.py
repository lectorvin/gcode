import re
import unittest
import timeit

import d3d


class GcodeError(Exception):
    """ Exception for invalid g-codes """
    def __init__(self):
        print('Not G-codes')


def getLine(dot1, dot2):    # generate all dots of line
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
    Return 50, 75 or 100 dots. Number of dots depends on line's length
    """
    x1, y1, z1 = dot1
    x2, y2, z2 = dot2
    coords = []
    x = x1
    if x2-x1 < 5:
        step = (x2-x1) / 50
    elif x2-x1 < 10:
        step = (x2-x1) / 75
    else:
        step = (x2-x1) / 100
    while x < x2:
        dot = [0, 0, 0]
        dot[0] = x
        dot[1] = float((x-x1)*(y2-y1) / (x2-x1)) + y1
        dot[2] = float((x-x1)*(z2-z1) / (x2-x1)) + z1
        coords.append(dot)
        x += step
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
        self.blocks = map(str, text.split('\n'))   # central value of class

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
        coor = re.compile('[XYZ][+-]?[0-9]+(\.[0-9]+)?')
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

    def saveImage(self, fl='images/test'):
        """
        Generate and save image as fl.gif

        Parameters
        ----------
        self : gcode object
            g-codes, which will be used
        fl : string, optional
        """
        gc = self.coordinates
        coords = []
        zmax = ymax = xmax = 0
        zmin = ymin = xmin = 9999
        for line in gc:
            temp = [None, None, None]
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
            if (temp[0] != None) or (temp[1] != None) or (temp[2] != None):
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
                coords.append(temp)

        for i in coords:
            if i[0] == None:
                i[0] = xmin*2
            if i[1] == None:
                i[1] = ymin*2
            if i[2] == None:
                i[2] = zmin*2
            i[0] -= xmin
            i[1] -= ymin
            i[2] -= zmin

        dots = []
        for i in range(len(coords)):
            temp = []
            if i != len(coords)-1:
                temp = getLine(coords[i], coords[i+1])
            if temp:
                for y in temp:
                    dots.append(y)
        d3d.main(dots, str(fl))


if __name__ == "__main__":
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
    print '1.000.000 checked codes - ' + str(timeit.timeit(gcode('G1').check,
                                             number=1000000))
    print '1 generated image - ' + str(timeit.timeit(gcode(
                            'G1 X1\nG1 Y1\nG1 X2 Y3 Z10').saveImage, number=1))
