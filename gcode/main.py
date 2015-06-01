import sys
import gcode

try:
    from PyQt4 import QtGui, QtCore
except ImportError:
    sys.exit("Could not import PyQt4,\
             you may try 'sudo apt-get install python-qt4'")

if sys.version_info >= (3, ):
    raise SystemError('Nope! Use python2.7!')

icons = {'icon':'icons/icon.png', 'exit':'icons/exit.png'}

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(550, 350)
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
                  (screen.height()-size.height())/2)
        self.setWindowTitle('G-code parser')
        self.setWindowIcon(QtGui.QIcon(icons['icon']))

        # buttons start
        self.open = QtGui.QAction('Open', self, shortcut='Ctrl+O',
                                  statusTip='Open file',
                                  triggered=self.openFile)
        self.save = QtGui.QAction('Save as ..', self, shortcut='Ctrl+Shift+S',
                                  statusTip='Save file as ..',
                                  triggered=self.saveFile)
        self.exit = QtGui.QAction(QtGui.QIcon(icons['exit']), "Exit", self,
                                  shortcut='Ctrl+Q',
                                  statusTip='Exit application',
                                  triggered=self.close)
        self.check = QtGui.QAction('Check', self, shortcut="Ctrl+B",
                                   statusTip='Check code',
                                   triggered=self.check_func)
        self.del_com = QtGui.QAction('Delete all comments', self,
                                     statusTip='Delete all comments',
                                     triggered=self.delCom)
        self.image = QtGui.QAction('Create image', self, shortcut='Ctrl+G',
                                   statusTip='Create and save image',
                                   triggered=self.genImage)

        menubar = self.menuBar()
        fl = menubar.addMenu('&File')
        fl.addAction(self.open)
        fl.addAction(self.save)
        fl.addAction(self.exit)
        fl = menubar.addMenu('&Options')
        fl.addAction(self.check)
        fl.addAction(self.del_com)
        fl.addAction(self.image)

        toolbar = self.addToolBar("Actions")
        toolbar.addAction(self.open)
        toolbar.addAction(self.save)
        toolbar.addAction(self.image)
        toolbar.addAction(self.exit)
        # end

        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = QtGui.QTextEdit()
        self.editor.setFont(font)
        highlighter = MyHighlighter(self.editor, "Classic")
        self.setCentralWidget(self.editor)

        self.statusBar().showMessage('Ready')

    def openFile(self):
        fl = QtGui.QFileDialog.getOpenFileName(self, 'Open file', './gcodes',
                                               'Text Files (*.gcode *.txt)')
        if fl:
            self.editor.setText(open(fl).read())

    def saveFile(self):
        fl = QtGui.QFileDialog.getSaveFileName(self, 'Save as', './gcodes',
                                               '*.gcode')
        if fl:
            with open(fl, 'w') as f:
                f.write(self.editor.toPlainText())

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?",
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def check_func(self):
        valid = gcode.gcode(str(self.editor.toPlainText())).check()
        self.message("Result", valid and "Valid g-code" or "Invalid g-code")

    def delCom(self):
        self.editor.setText(gcode.gcode(self.editor.toPlainText()).del_comm())

    def genImage(self):
        fl = QtGui.QFileDialog.getSaveFileName(self, 'Save image as')
        try:
           if fl:
               self.message_without_buttons("Message", "Waiting please ...")
               gcode.gcode(str(self.editor.toPlainText())).saveImage(fl=fl)
               self.message("Message", "Done!")
        except Exception as e:
           self.message("Error", str(e))

    def message(self, name, message):
        reply = QtGui.QMessageBox.question(self, name,
                                         message, QtGui.QMessageBox.Yes)

    def message_without_buttons(self, name, message):
        reply = QtGui.QMessageBox.question(self, name, message)

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
        coor = QtGui.QTextCharFormat()
        comment = QtGui.QTextCharFormat()
        error = QtGui.QTextCharFormat()

        self.highlightingRules = []

        # main_command or tech_command (G1 M107)
        brush = QtGui.QBrush(QtCore.Qt.darkBlue, QtCore.Qt.SolidPattern)
        main_command.setForeground(brush)
        main_command.setFontWeight(QtGui.QFont.Bold)
        pattern = QtCore.QRegExp("\\b[GM][0-9]{1,3}\\b")
        rule = HighlightingRule(pattern, main_command)
        self.highlightingRules.append(rule)

        # line (N10)
        brush = QtGui.QBrush(QtCore.Qt.darkMagenta, QtCore.Qt.SolidPattern)
        line.setForeground(brush)
        pattern = QtCore.QRegExp("\\bN[0-9]+\\b")
        rule = HighlightingRule(pattern, line)
        self.highlightingRules.append(rule)

        # coordinates (X10.5 or Y5)
        brush = QtGui.QBrush(QtCore.Qt.darkCyan)
        coor.setForeground(brush)
        pattern = QtCore.QRegExp("\\b[XYZ][-+]?[0-9]+(\.[0-9]+)?\\b")
        rule = HighlightingRule(pattern, coor)
        self.highlightingRules.append(rule)

        # comment (; .... blah blah)
        brush = QtGui.QBrush(QtCore.Qt.darkYellow)
        comment.setForeground(brush)
        pattern = QtCore.QRegExp(";\s.*")
        rule = HighlightingRule(pattern, comment)
        self.highlightingRules.append(rule)

        # error
        brush = QtGui.QBrush(QtCore.Qt.red)
        error.setForeground(brush)
        # this pattern finds correct string
        pattern = QtCore.QRegExp(
                            '^(((?!;)[A-Z][+-]?\d+(\.\d+)?\s?)*(\s*;\s.*)?)$')
        self.rule = HighlightingRule(pattern, error)

    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            expression = QtCore.QRegExp(rule.pattern)
            index = expression.indexIn(text, 0)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = text.indexOf(expression, index+length)
        # highlight errors
        exp = QtCore.QRegExp(self.rule.pattern)
        index = exp.indexIn(text, 0)
        if index < 0:          # if string isn't correct
            self.setFormat(0, len(text), self.rule.format)

        self.setCurrentBlockState(0)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec_()
