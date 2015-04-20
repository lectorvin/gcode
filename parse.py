import sys
import re
# import pyparsing as pp  # pp.regex

from PyQt4 import QtGui, QtCore  # QtCore.QRegExp

'''for i in code.scanString(asdf):
    print(i[0])
'''
class WrongCodeError(Exception):
    def __init__(self):
        pass


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.resize(250, 150)
        self.setWindowTitle('test')
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.exit = QtGui.QAction(QtGui.QIcon('exit.png'), "Exit", self)
        self.exit.setShortcut('Ctrl+Q')
        self.exit.setStatusTip('Exit application')
        self.connect(self.exit, QtCore.SIGNAL('triggered()'),
                     QtGui.qApp, QtCore.SLOT('quit()'))

        self.editor = QtGui.QTextEdit()
        self.editor.setFont(font)
        highlighter = MyHighlighter(self.editor, "Classic")
        self.setCentralWidget(self.editor)

        '''self.check = QtGui.QAction(QtGui.QIcon('exit.png'), 'Check', self)
        self.check.setShortcut('Ctrl+B')
        self.connect(self.check, QtCore.SIGNAL('triggered()'),
                     self.check_func )'''

        self.statusBar().showMessage('Ready')

        menubar = self.menuBar()
        fl = menubar.addMenu('&File')
        fl.addAction(self.exit)
        # fl.addAction(self.check)

    '''def check_func(self):
        mass = self.editor.toPlainText().split(' ')
        code = re.compile(r'\b[A-Z]\d+\b')
        for i in mass:
            if !(code.match(i)):

        print(a)
        print(1)'''


class HighlightingRule(object):
    def __init__(self, pattern, format):
        self.pattern = pattern
        self.format = format


class MyHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, theme):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent
        main_command = QtGui.QTextCharFormat()
        line = QtGui.QTextCharFormat()
        coordinate = QtGui.QTextCharFormat()

        self.highlightingRules = []

        #main_command or tech_command G10 G2
        brush = QtGui.QBrush(QtCore.Qt.darkBlue, QtCore.Qt.SolidPattern)
        main_command.setForeground(brush)
        main_command.setFontWeight(QtGui.QFont.Bold)
        pattern = QtCore.QRegExp("\\b[GM][0-9]{1,2}\\b")
        rule = HighlightingRule(pattern, main_command)
        self.highlightingRules.append(rule)

        #line N10
        brush = QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern)
        line.setForeground(brush)
        pattern = QtCore.QRegExp("\\bN[0-9]+\\b")
        rule = HighlightingRule(pattern, line)
        self.highlightingRules.append(rule)

        #coordinates
        brush = QtGui.QBrush(QtCore.Qt.green)
        coordinate.setForeground(brush)
        pattern = QtCore.QRegExp("\\b[XYZ][-+]?(([0-9]*\.?[0-9]+)|([0-9]+\.?[0-9]*))\\b")
        rule = HighlightingRule(pattern, coordinate)
        self.highlightingRules.append(rule)


    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            expression = QtCore.QRegExp(rule.pattern)
            index = expression.indexIn(text, 0)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = text.indexOf(expression, index+length)
        self.setCurrentBlockState(0)


app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec_()
'''asdf = 'G5 D8 T9 R8 AS5'
a = asdf.split(' ')
code = re.compile(r'(\b[A-Z]\d+\b){0,4}')
for i in a:
    try:
        if code.match(i):
            print(i)
        else:
            raise WrongCodeError()
    except WrongCodeError:
        pass
'''
