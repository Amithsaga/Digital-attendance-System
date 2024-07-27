import pandas as pd
import os

def show_attendance():
    if os.path.isfile('attendance.csv'):
        df = pd.read_csv('attendance.csv')
        print(df)
    else:
        print("No attendance records found.")

if __name__ == "__main__":
    show_attendance()
