# main.py
#!/usr/bin/python
import sys
import re
import logging
import gcode

from pyqtgraph.Qt import QtGui, QtCore

icons = {'icon': 'icons/icon.png', 'exit': 'icons/exit.png'}
log = "log.log"
logging.basicConfig(
    format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s %(message)s',
    level=logging.DEBUG, filename=log)


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
        self.show_image = QtGui.QAction('Show image', self, shortcut="Ctrl+G",
                                        statusTip='Show image',
                                        triggered=self.showImage)

        menubar = self.menuBar()
        fl = menubar.addMenu('&File')
        fl.addAction(self.open)
        fl.addAction(self.save)
        fl.addAction(self.exit)
        fl = menubar.addMenu('&Options')
        fl.addAction(self.check)
        fl.addAction(self.del_com)
        fl.addAction(self.show_image)

        toolbar = self.addToolBar("Actions")
        toolbar.addAction(self.open)
        toolbar.addAction(self.save)
        toolbar.addAction(self.show_image)
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
            try:
                logging.debug('Open file: {}'.format(str(fl)))
                self.editor.setText(open(fl).read())
            except IOError:
                logging.error('Try to open non-existent file')
                self.message('Error', 'Non-existent file')
        else:
            logging.error('Try to open file with null filename')

    def saveFile(self):
        fl = QtGui.QFileDialog.getSaveFileName(self, 'Save as', './gcodes',
                                               '*.gcode')
        if fl:
            logging.debug('Save file: {}'.format(str(fl)))
            with open(fl, 'w') as f:
                f.write(self.editor.toPlainText())
        else:
            logging.error('Try to save file with null filename')

    def closeEvent(self, event):
        logging.debug('Closing main window...')
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?",
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            logging.debug('The end')
            event.accept()
        else:
            logging.debug('or not')
            event.ignore()

    def check_func(self):
        valid = gcode.gcode(str(self.editor.toPlainText())).check()
        message = valid and "Valid Gcode" or "Invalid Gcode"
        logging.debug('Checked if Gcode is valid. Result - {}'.format(message))
        self.message("Result", message)

    def delCom(self):
        logging.debug('Delete comments from text')
        self.editor.setText(gcode.gcode(self.editor.toPlainText()).del_comm())

    def showImage(self):
        logging.debug('Show image')
        try:
            if (str(self.editor.toPlainText())):
                gcode.gcode(str(self.editor.toPlainText())).saveImage()
        except gcode.GcodeError:
            self.message('Error', "Invalid g-code")

    def message(self, name, message):
        reply = QtGui.QMessageBox.question(self, name, message,
                                           QtGui.QMessageBox.Yes)
        return reply


class HighlightingRule(object):
    def __init__(self, pattern, format_):
        self.pattern = pattern
        self.format_ = format_


class MyHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, theme):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent
        main_command = QtGui.QTextCharFormat()
        line = QtGui.QTextCharFormat()
        coor = QtGui.QTextCharFormat()
        comment = QtGui.QTextCharFormat()
        feedrate = QtGui.QTextCharFormat()
        error = QtGui.QTextCharFormat()

        self.highlightingRules = []

        # main_command or tech_command (G1 M107)
        brush = QtGui.QBrush(QtCore.Qt.darkBlue, QtCore.Qt.SolidPattern)
        main_command.setForeground(brush)
        main_command.setFontWeight(QtGui.QFont.Bold)
        pattern = re.compile("\\b[GM][0-9]{1,3}\\b")
        rule = HighlightingRule(pattern, main_command)
        self.highlightingRules.append(rule)

        # line (N10)
        brush = QtGui.QBrush(QtCore.Qt.darkMagenta, QtCore.Qt.SolidPattern)
        line.setForeground(brush)
        pattern = re.compile("\\bN[0-9]+\\b")
        rule = HighlightingRule(pattern, line)
        self.highlightingRules.append(rule)

        # coordinates (X10.5 or Y5)
        brush = QtGui.QBrush(QtCore.Qt.darkCyan)
        coor.setForeground(brush)
        pattern = re.compile("\\b[XYZ][-+]?[0-9]+(\.[0-9]+)?\\b")
        rule = HighlightingRule(pattern, coor)
        self.highlightingRules.append(rule)

        # comment (; .... blah blah)
        brush = QtGui.QBrush(QtCore.Qt.darkYellow)
        comment.setForeground(brush)
        pattern = re.compile(";\s.*")
        rule = HighlightingRule(pattern, comment)
        self.highlightingRules.append(rule)

        # feedrate (F160.0)
        brush = QtGui.QBrush(QtCore.Qt.darkGreen)
        feedrate.setForeground(brush)
        pattern = re.compile("\\b[F][-+]?[0-9]+(\.[0-9]+)?\\b")
        rule = HighlightingRule(pattern, feedrate)
        self.highlightingRules.append(rule)

        # error
        brush = QtGui.QBrush(QtCore.Qt.red)
        error.setForeground(brush)
        # this pattern finds correct string
        pattern = re.compile('^(((?!;)[A-Z][+-]?\d+(\.\d+)?\s?)*(\s*;\s.*)?)$')
        self.rule = HighlightingRule(pattern, error)

    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            exp = rule.pattern
            result = exp.search(text, 0)
            while result:
                span = result.span()
                length = span[1] - span[0]
                self.setFormat(span[0], length, rule.format_)
                result = exp.search(text, span[0]+length)

        exp = self.rule.pattern
        result = exp.search(text, 0)
        if not(result):
            self.setFormat(0, len(text), self.rule.format_)

        self.setCurrentBlockState(0)


if __name__ == "__main__":
    with open(log, 'w') as f:
        pass
    logging.debug('Program starts')
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec_()
