import requests, sqlite3, time, datetime, sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
style.use('fivethirtyeight')


class Instagram_counter(object):
    def __init__(self, username):
        self.username = username
    
    def menu_func(self):
        self.connection = sqlite3.connect("Instagram_Database.db")
        self.cursor = self.connection.cursor()
        while True:
            display = " >> "
            print(f"""
            Profile:  {self.username}
            Amount Of Followers:  {self.total_followers()}\n
            0. Exit
            1. Insert account data.
            2. Show your data.
            3. Show plot of your data. 
            """)
            try:
                menu = int(input(display))
                if menu == 0:
                    self.cursor.close()
                    self.connection.close()
                    sys.exit()
                elif menu == 1:
                    self.data_table()
                elif menu == 2:
                    self.show_data()
                elif menu == 3:
                    self.plot_data()
                else:
                    print("Invalid data!")
            except TypeError:
                print("Invalid Data!")
        
    def total_followers(self):
        url = 'https://www.instagram.com/' + self.username
        r = requests.get(url).text
        start = '"edge_followed_by":{"count":'
        end = '},"followed_by_viewer"'
        followers = (r[r.find(start)+len(start):r.rfind(end)])
        return followers

    def data_table(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.username} (Account TEXT, Followers INT, Datestamp TEXT)")
        date = str(datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S'))
        self.cursor.execute(f"INSERT INTO {self.username} (Account, Followers, datestamp) VALUES(?,?,?)",
                            (self.username, self.total_followers(), date))
        self.connection.commit()

    def show_data(self):
        self.cursor.execute(f"SELECT * FROM {self.username}")
        for line in self.cursor.fetchall():
            print(line)

    def plot_data(self):
        self.cursor.execute(f"SELECT Datestamp, Followers FROM {self.username}")
        dates = []
        followers = []
        for row in self.cursor.fetchall():
            dates.append(row[0])
            followers.append(row[1])
        plt.plot_date(dates, followers, '-')
        plt.show()

if __name__ == '__main__':
    user = str(input("Instagram account: "))
    account = Instagram_counter(user)
    account.menu_func()
