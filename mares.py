from datetime import datetime
from email import header
import serial
import json
import re
import csv
import configparser
import experiment_details as exp
import time

config = configparser.ConfigParser()
config.read('pendulum.ini')

last_time = 0
dt = 720

serial_port = None
dbuging = config['DEFAULT']['DEBUG']
header_pendulum= ['Samples number','Period [s]','g [m/s^2]','Velocity [m/s]','Temperature [ºC]']

def try_to_lock_experiment(serial_port):
    
    #LOG_INFO
    # print("AH PROCURA DO PIC NA PORTA SERIE")
    pic_message = serial_port.read_until(b'\r')
    pic_message = pic_message.decode(encoding='ascii')
    pic_message = pic_message.strip()
    # print("MENSAGEM DO PIC:\n")
    # print(pic_message)
        
    match = re.search(r"^(IDS)\s(?P<exp_name>[^ \t]+)\s(?P<exp_state>[^ \t]+)$",pic_message)
    if (dbuging == "on"):
        print("\-------- --------/\n")
        print(match.group("exp_name"))
    if match.group("exp_name") != None:
        #LOG_INFO
        if (dbuging == "on"):
            print("PIC FOUND ON THE SERIAL PORT")
        if match.group("exp_state") == "STOPED":
            return True
        else:
            if (dbuging == "on"):
                print("STATE OF MACHINE DIF OF STOPED")
            if do_stop():
                return True
            else:
                return False
    else:
        #LOG INFO
        if (dbuging == "on"):
            print("PIC NOT FOUND ON THE SERIAL PORT")
        return False

def serial_lock():
    global serial_port
    try:
        serial_port = serial.Serial(port = config['DEFAULT']['DEV_PORT'],\
                        baudrate=int(config['DEFAULT']['BAUDRATE']),\
                        timeout = int(config['DEFAULT']['DEATH_TIMEOUT']))
    except serial.SerialException:
        #LOG_WARNING: couldn't open serial port exp_port. Port doesnt exist or is in use
        pass
    else:
        if try_to_lock_experiment(serial_port) :
            return True
        else:
            serial_port.close()
            return False



def do_start() :
    global serial_port
    if (dbuging == "on"):
        print("Trying to start the experiment\n")
    cmd = "str\r"
    cmd = cmd.encode(encoding='ascii')
    serial_port.reset_input_buffer()
    serial_port.write(cmd)
    while True :
        pic_message = serial_port.read_until(b'\r')
        if (dbuging == "on"):
            print("MESSAGE FROM THE PIC TO CONFIRM STROK: \n")
            print(pic_message.decode(encoding='ascii'))
            print("\-------- --------/\n")
        if "STROK" in pic_message.decode(encoding='ascii') :
            return True
        elif re.search(r"(STOPED|CONFIGURED|RESETED){1}$",pic_message.decode(encoding='ascii')) != None:
            return False
        #elif "STOPED" or "CONFIGURED" or "RESETED" in pic_message.decode(encoding='ascii') :
        #    return False
        #Aqui não pode ter else: false senão rebenta por tudo e por nada
        #tem de se apontar aos casos especificos -_-
    

def do_stop() :
    global serial_port
    if (dbuging == "on"):
        print("Try to stop the experiment\n")
    cmd = "stp\r"
    cmd = cmd.encode(encoding='ascii')
    serial_port.reset_input_buffer()
    serial_port.flush()
    serial_port.write(cmd)
    while True :
        try:
            pic_message = serial_port.read_until(b'\r')
            if (dbuging == "on"):
                print("MESSAGE FROM THE PIC TO CONFIRM STPOK: \n")
                print(pic_message.decode(encoding='ascii'))
                print("\-------- ! --------/\n")
                print ( pic_message.decode(encoding='ascii').split("\t"))
        except:
            pass
        if "STPOK" in pic_message.decode(encoding='ascii') :
            return True
        # elif "STP" in pic_message.decode(encoding='ascii') :
        #     print("Reading the STP  send to the pic")
        #     pass
        elif len(pic_message.decode(encoding='ascii').split("\t")) == 3 and  pic_message.decode(encoding='ascii').split("\t")[2] in ["CONFIGURED\r","RESETED\r"] :
        # elif re.search(r"(CONFIGURED|RESETED){1}$",pic_message.decode(encoding='ascii')) != None :
            if (dbuging == "on"):
                print("There is garbage in the serial port try the command again!")
            serial_port.reset_input_buffer()
            serial_port.write(cmd)
        # Maybe create a counter to give a time out if the pic is not working correct
        #Aqui não pode ter else: false senão rebenta por tudo e por nada
        #tem de se apontar aos casos especificos -_-
    

def do_reset() :
    global serial_port
    if (dbuging == "on"):
        print("Trying to reset the experience \n")
    cmd = "rst\r"
    cmd = cmd.encode(encoding='ascii')
    serial_port.reset_input_buffer()
    serial_port.write(cmd)
    while True :
        pic_message = serial_port.read_until(b'\r')
        if (dbuging == "on"):
            print("MESSAGE FROM THE PIC TO CONFIRM RSTOK: \n")
            print(pic_message.decode(encoding='ascii'))
            print("\-------- --------/\n")
        if "RSTOK" in pic_message.decode(encoding='ascii') :
            return True
        elif re.search(r"(STOPED|CONFIGURED){1}$",pic_message.decode(encoding='ascii')) != None :
            return False
        #Aqui não pode ter else: false senão rebenta por tudo e por nada
        #tem de se apontar aos casos especificos -_-



def do_config() :
    global serial_port

    cmd ="cfg\t"+str(config['DEFAULT']['DELTAX'])+"\t"+str(config['DEFAULT']['SAMPLES'])+"\r"
    cmd = cmd.encode(encoding="ascii")
    #Deita fora as mensagens recebidas que não
    #interessam
    serial_port.reset_input_buffer()
    serial_port.write(cmd)
    if (dbuging == "on"):
        print("TRYING TO CFG THE PIC")
    while True :
        pic_message = serial_port.read_until(b'\r')
        if (dbuging == "on"):
            print("CONFIGURATION PIC MESSAGE:\n")
            print(pic_message.decode(encoding='ascii'))
            print("\-------- --------/\n")
        if "CFG" in pic_message.decode(encoding='ascii') :
            pic_message = pic_message.decode(encoding='ascii')
            #Remover os primeiros 4 caracteres para tirar o "CFG\t" 
            pic_message = pic_message[4:]
            pic_message = pic_message.replace("\t"," ")
            break
        elif re.search(r"(STOPED|RESETED){1}$",pic_message.decode(encoding='ascii')) != None:
            return -1,False
    status_confirmation = serial_port.read_until(b'\r')
    status_confirmation = status_confirmation.decode(encoding='ascii')
    if (dbuging == "on"):
        print("PIC MESSAGE TO CONFIRM CFGOK: \n")
        print(status_confirmation)
        print("\-------- --------/\n")
    if "CFGOK" in status_confirmation:
        return pic_message, True
    else:
        return -1, False

def receive_data_from_exp():
    global serial_port
    if (dbuging == "on"):
        print("SEARCHING FOR INFO IN THE SERIE PORT\n")
    try:
        pic_message = serial_port.read_until(b'\r')
        pic_message = pic_message.decode(encoding='ascii')
    except:
        print("TODO: send error to server, pic is not conected")
    if (dbuging == "on"):
        print("MENSAGE FORM PIC:\n")
        print(pic_message)
        print("\-------- --------/\n")
    if "DAT" in pic_message:
        if (dbuging == "on"):
            print("INFO FOUND\nEXPERIMENTE STARTED")
        return "DATA_START"
    elif "END" in pic_message:
        if (dbuging == "on"):
            print("INFO FOUND\nEXPERIMENTE ENDED")
        return "DATA_END"
    else:
        #1       3.1911812       9.7769165       21.2292843      25.72
        if (dbuging == "on"):
            print("INFO FOUND\nDATA SEND TO THE SERVER")
        pic_message = pic_message.strip()
        pic_message = pic_message.split("\t")
        return pic_message

def do_experiment():
    o, ok=do_config()
    if ok == True:
        do_start()
        name_file=datetime.now()
        name_file = "./"+str(config['DEFAULT']['FOLDER'])+"/"+name_file.strftime("%Y-%m-%d %H:%M:%S")+".csv"
        if (dbuging == "on"):
            print(name_file)
        with open(name_file, mode='w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(header_pendulum)
            while True:
                exp_data = receive_data_from_exp()
                if exp_data == "DATA_START":
                    pass
                elif exp_data != "DATA_END":
                    writer.writerow(exp_data)
                else:
                    break

if __name__ == "__main__":
    if serial_lock() == True:
        if config['DEFAULT']['ROSSA'] == "on":
            while True:
                time_now= int(time.time())
                if time_now >=(last_time+dt):
                    do_experiment()
                    last_time = time_now
        else:
            do_experiment()
    else: 
        print("Serial port not found")
            
