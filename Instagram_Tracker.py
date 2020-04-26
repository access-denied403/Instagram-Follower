from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLCDNumber
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
        self.setWindowTitle("Instagram Tracker")
        self.initUI()

        self.connection = sqlite3.connect("Insta-Track.db")
        self.cursor  = self.connection.cursor()

    def initUI(self):
        self.current_followers = QtWidgets.QLCDNumber(self)
        self.current_followers.setGeometry(QtCore.QRect(670, 10, 111, 35))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(200)
        self.current_followers.setFont(font)
        self.current_followers.setSmallDecimalPoint(False)
        self.current_followers.setDigitCount(7)
        self.current_followers.setProperty("value", 0.0)
        self.current_followers.setObjectName("current_followers")
        self.current_followers.setStyleSheet("QLCDNumber { color: black }")

        self.username_entry = QtWidgets.QLineEdit(self)
        self.username_entry.setGeometry(QtCore.QRect(240, 70, 311, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.username_entry.setFont(font)
        self.username_entry.setPlaceholderText("Enter username here...")
        self.username_entry.setObjectName("username_entry")

        self.update_button = QtWidgets.QPushButton(self)
        self.update_button.setGeometry(QtCore.QRect(670, 70, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.update_button.setFont(font)
        self.update_button.setObjectName("update_button")
        self.update_button.setText("Update")
        self.update_button.clicked.connect(self.update)

        self.save_button = QtWidgets.QPushButton(self)
        self.save_button.setGeometry(QtCore.QRect(670, 110, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.save_button.setFont(font)
        self.save_button.setObjectName("save_button")
        self.save_button.setText("Save")
        self.save_button.clicked.connect(self.save)

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(160, 130, 461, 361))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setHorizontalHeaderLabels(["Date", "Followers"])

        self.plot_button = QtWidgets.QPushButton(self)
        self.plot_button.setGeometry(QtCore.QRect(670, 150, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.plot_button.setFont(font)
        self.plot_button.setObjectName("plot_button")
        self.plot_button.setText("Plot")
        self.plot_button.clicked.connect(self.plot)

        self.delete_button = QtWidgets.QPushButton(self)
        self.delete_button.setGeometry(QtCore.QRect(670, 460, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.delete_button.setFont(font)
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setText("Delete")
        self.delete_button.clicked.connect(self.delete)

    def update(self):
        self.date = str(datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S'))
        try:
            url = 'https://www.instagram.com/' + str(self.username_entry.text())
            r = requests.get(url).text
            start = '"edge_followed_by":{"count":'
            end = '},"followed_by_viewer"'
            self.result = str(r[r.find(start)+len(start):r.rfind(end)])
            self.current_followers.display(int(self.result))
            self.table()
        except:
            self.username_entry.setText("ERROR")

    def save(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.username_entry.text()} (User TEXT, Followers INT, Datestamp TEXT)")
        self.cursor.execute(f"INSERT INTO {self.username_entry.text()} (User, Followers, Datestamp) VALUES(?,?,?)",
                                        (self.username_entry.text(), self.result, self.date))
        self.connection.commit()

    def table(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.username_entry.text()} (User TEXT, Followers INT, Datestamp TEXT)")
        self.cursor.execute(f"SELECT Datestamp, Followers FROM {self.username_entry.text()}")  
            
        row_position = self.cursor.fetchall()
        self.tableWidget.setRowCount(0)
        for row in enumerate(row_position):
            self.tableWidget.insertRow(row[0])
            self.tableWidget.setItem(row[0], 0, QtWidgets.QTableWidgetItem(str(row[1][0])))
            self.tableWidget.setItem(row[0], 1, QtWidgets.QTableWidgetItem(str(row[1][1])))
            
    
    def plot(self):
        self.cursor.execute(f"SELECT Datestamp, Followers FROM {self.username_entry.text()}")
        dates = []
        followers = []
        for row in self.cursor.fetchall():
            dates.append(row[0])
            followers.append(row[1])
        plt.plot_date(dates, followers, '-')
        plt.show()

    def delete(self):
        row = int(self.tableWidget.currentRow())
        self.tableWidget.removeRow(row)
        self.cursor.execute(f"DELETE FROM {self.username_entry.text()} WHERE rowid={row}")
        self.connection.commit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    if sys.exit(app.exec_()):
        MainWindow.cursor.close()
        MainWindow.connection.close()