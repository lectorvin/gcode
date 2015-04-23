import re
import unittest


class gcode(object):
    def __init__(self, text):
        self.text = text
        self.blocks = []
        self.blocks = text.split('\n')

    def check(self):   # full program
        for line in self.blocks:
            if re.match('(?!(^(((?!;)[A-Z][+-]?\d+(\.\d+)?\s?)*(\s*;\s.*)?)$))', line):
                return False 
        return True


if __name__ == "__main__":
    class Test(unittest.TestCase):
        def testa_5(self): self.assertFalse(gcode('asdf').check())
        def testb_2(self): self.assertTrue(gcode('G1 X1.1').check())
        def testc_1(self): self.assertTrue(gcode('').check())
        def testd_one(self): self.assertTrue(gcode('; generated by Slic3r\nG21 ; set units to millimeters').check())
        def teste_big(self): self.assertTrue(gcode("M107\nM104 S200 ; set temperature\nG28 ; home all axes").check())
        def testf_piece(self): self.assertTrue(gcode('G1 Z5 F5000 ; lift nozzle\n\nM109 S200 ; wait for temp').check())
        def testg_of(self): self.assertTrue(gcode('G90 ; use absolute\nG92 E0\nM82 ; use absolute distance').check())
        def testh_gcode(self): self.assertTrue(gcode('G1 F1800.000 E-1.00000\nG92 E0\nG1 Z0.500 F7800.000').check())
        def testi_generated(self): self.assertTrue(gcode('G1 X91.746 Y93.225 F7800.000\nG1 E1.000 F1800.000').check())
        def testj_by(self): self.assertTrue(gcode('G1 X93.774 Y92.057 E1.4774 F600.00\nG1 X96.075 Y91.635 E1.39').check())
        def testk_Slic3r(self): self.assertTrue(gcode('M106 S255\nG1 F1800.000 E2.99327\nG92 E0\nG1 Z0.900 F7800.000').check())
        def testl_is(self): self.assertTrue(gcode('G1 Z12.900 F7800.000\nG1 Z13.300 F7800.000\nG1 Z13.700 F7800.000').check())
        def testm_absolutely(self): self.assertTrue(gcode('M107\nM104 S0 ; turn off temperature').check())
        def testn_correct(self): self.assertTrue(gcode('G28 X0 ; home X axis\nM84 ; disable motors').check())

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
