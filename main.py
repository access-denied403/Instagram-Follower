from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal)
from matplotlib import style
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys, sqlite3, requests, time, datetime
style.use('fivethirtyeight')

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Instagram Follower Counter")
        self.initUI()

    def initUI(self):
        self.user_entry = QtWidgets.QLineEdit(self)
        self.user_entry.setGeometry(QtCore.QRect(250, 70, 261, 35))
        self.user_entry.setObjectName("user_entry")
        self.user_entry.setPlaceholderText("Enter username here...")

        self.top_label = QtWidgets.QLabel(self)
        self.top_label.setGeometry(QtCore.QRect(270, 20, 221, 51))
        font = QtGui.QFont()
        font.setFamily("Gargi-1.2b")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.top_label.setFont(font)
        self.top_label.setObjectName("top_label")
        self.top_label.setText("Instagram Followers")

        self.result_button = QtWidgets.QPushButton(self)
        self.result_button.setGeometry(QtCore.QRect(530, 50, 71, 71))
        font = QtGui.QFont()
        font.setFamily("Bitstream Vera Serif")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.result_button.setFont(font)
        self.result_button.setObjectName("result_button")
        self.result_button.clicked.connect(self.go_button)
        self.result_button.setText("Go!")

        self.result_field = QtWidgets.QLabel(self)
        self.result_field.setGeometry(QtCore.QRect(250, 120, 261, 41))
        self.result_field.setText("")
        self.result_field.setObjectName("result_field")

        self.save_checkBox = QtWidgets.QCheckBox(self)
        self.save_checkBox.setGeometry(QtCore.QRect(530, 140, 191, 24))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.save_checkBox.setFont(font)
        self.save_checkBox.setObjectName("save_checkBox")
        self.save_checkBox.setText("Save to database")

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(120, 211, 551, 321))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(670, 547, 111, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Diagram")
        self.pushButton.clicked.connect(self.diagram_button)


    def go_button(self):
        self.connection = sqlite3.connect("Instagram_Database.db")
        self.cursor = self.connection.cursor()
        self.username = str(self.user_entry.text())
        self.date = str(datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S'))
        self.result_field.setText(self.total_followers())

        if self.save_data() == True:
            self.data_table()
        
        self.populate_table()
        self.cursor.close()
        self.connection.close()
    
    def save_data(self):
        if self.save_checkBox.isChecked():
            save = True
        else:
            save = False
        return save


    def diagram_button(self):
        self.connection = sqlite3.connect("Instagram_Database.db")
        self.cursor = self.connection.cursor()
        self.username = str(self.user_entry.text())

        self.plot_data()

        self.cursor.close()
        self.connection.close()
    
    
    def total_followers(self):
        url = 'https://www.instagram.com/' + self.username
        r = requests.get(url).text
        start = '"edge_followed_by":{"count":'
        end = '},"followed_by_viewer"'
        return str(r[r.find(start)+len(start):r.rfind(end)])

    def data_table(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.username} (Account TEXT, Followers INT, Datestamp TEXT)")
        self.cursor.execute(f"INSERT INTO {self.username} (Account, Followers, datestamp) VALUES(?,?,?)",
                                                    (self.username, self.total_followers(), self.date))
        self.connection.commit()
    
    def plot_data(self):
        self.cursor.execute(f"SELECT Datestamp, Followers FROM {self.username}")
        dates = []
        followers = []
        for row in self.cursor.fetchall():
            dates.append(row[0])
            followers.append(row[1])
        plt.plot_date(dates, followers, '-')
        plt.show()

    def populate_table(self):
        self.cursor.execute(f"SELECT Datestamp, Followers FROM {self.username}")
        rowPosition = self.tableWidget.rowCount()
        for row in self.cursor.fetchall():
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(row[0])))
            self.tableWidget.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(str(row[1])))
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())