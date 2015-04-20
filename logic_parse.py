import re
import unittest


class CodeError(Exception):
    def __init__(self, message):
        self.message = message


class SyntaxCodeError(CodeError):
    def __init__(self, message):
        CodeError.__init__(self, message)


class gcode(object):
    def __init__(self, text):
        self.text = text
        self.blocks = []
        temp = text.split('\n')
        for line in temp:
            self.blocks.append(line.split())

    def check(self):   # full program
        in_block = False   # true, if in block of code % ... %
        comment = False    # true, if text is comment ; ...
        code = re.compile('[A-W][0-9.]+')
        coord = re.compile('[XYZ][+-]?[0-9]+(\.[0-9]+)?')

        for line in self.blocks:   # line is an list
            if line[0] == '%' and (len(line) == 1 or line[1][0] == ';'):
                in_block = not(in_block)
                # not always required to be present on newer machines
            elif re.match('O\d+',line[0]):
                self.program_name = line[0][1:]
            else:
                for piece in line:
                    try:
                        if piece == ';':
                            comment = True
                        elif code.match(piece):
                            pass      # later
                        elif coord.match(piece):
                            pass      # later
                        elif comment:
                            pass      # nothing to do here, just pass
                        else:
                            raise (SyntaxCodeError)
                    except SyntaxCodeError:
                        raise(SyntaxCodeError("Syntax error at \
                              line {} '{}'").format(line.index(piece), piece))
                if in_block:
                    raise(SyntaxCodeError('Not ended block'))
        return True

if __name__ == "__main__":
    class Test(unittest.TestCase):
        def test1(self): self.assertEqual(gcode('N10 G5 X5').check(), True)
        def test2(self): self.assertEqual(gcode('N10 G5 X5.2').check(), True)
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
