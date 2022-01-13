from datetime import datetime
from email import header
import serial
import json
import re
import csv
import configparser
import experiment_details as exp
config = configparser.ConfigParser()
config.read('pendulum.ini')
header_pendulum= ['Samples number','Period [s]','g [m/s^2]','Velocity [m/s]','Temperature [ºC]']

#https://stackoverflow.com/questions/54944524/how-to-write-csv-file-into-specific-folder
if __name__ == "__main__":
    name_file=datetime.now()
    name_file = "./"+str(config['DEFAULT']['FOLDER'])+"/"+name_file.strftime("%Y-%m-%d %H:%M:%S")+".csv"
    print(name_file)
    with open(name_file, mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header_pendulum)