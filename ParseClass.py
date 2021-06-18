# Muntherr anati 
import time
import CommandClass
import re
import json
import optparse
import logging
import os
import logging.handlers
import glob
import csv


def logging_file(status, Out_log, Max_log, filetype):
    files_path = os.path.join(Out_log, '*.log')  # to join and find all files ends with .log extension
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)  # sort files by date created.
    # to find the oldest one and delete it if max_log is reached.
    logtime = time.localtime()  # to make new log file in each run
    file_name = Out_log + '/output' + str(logtime.tm_sec)
    LogCounter = len(glob.glob1(Out_log, "*.log")) + 1  # log file counter To count number of files ends with .log
    CSVcounter = len(glob.glob1(Out_log, "*.csv")) + 1  # log file counter To count number of files ends with .log

    if int(LogCounter) >= int(Max_log):  # If Log counter bigger than max log files from the script file
        First_log = files[LogCounter - 2]  # Oldest file stored in the last index
        os.remove(First_log)  # remove the oldest file
    logging.basicConfig(filename=(file_name + '.log'), level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    # logging basic configuration to simple configuration the log output file
    logging.debug(status)  # Detailed information, typically of interest only when diagnosing problems.
    if filetype == "csv":  # If file type in script file is csv then the log file will be  .csv not .log
        if int(CSVcounter) >= int(Max_log):  # If Log counter bigger than max log files from the script file
            First_csv = files[CSVcounter - 2]  # Oldest file stored in the last index
            os.remove(First_csv)  # remove the oldest file
        if LogCounter != 1:
            with open((file_name + '.log')) as file:  # last file created will be .log file
                # take the .log file and convert it to .csv fils
                lines = file.read().splitlines()
                lines = [lines[x:x + 3] for x in
                         range(0, len(lines), 3)]  # Copy contents for each line in .log file until reach last line
                with open(file_name + '.csv',
                          'w') as csvfile:  # create .csv file and write contents to it
                    w = csv.writer(csvfile)
                    w.writerows(lines)
            #os.remove((file_name + '.log'))


def extraction_commands(Script_path):  # This function will do the following
    # 1.Get all commands values from configuration.json file
    # 2.Get all directories and commands from script file
    command_counter = 1
    n = 0
    Status = dict()  # make dictionary to save the status from commands if all good then the output will be True, if not it will be False
    with open('configuration.json') as json_file:  # open configuration file to read it
        data = json.load(json_file)  # load .json file to be read in python invironment
        Threshold_size = data[" Threshold_size "]  # get key and value from .json file
        Threshold_size_int = int(
            re.search(r'\d+', Threshold_size).group())  # split the string to take only the digits from it
        if Threshold_size.find('K') != -1:  # convert from KB to B , K = 1000
            Threshold_size_int = Threshold_size_int * 1000
        # Extracting all command
        Max_commands = data[" Max_commands "]
        Max_commands_int = int(Max_commands)
        Max_log_files = data[" Max_log_files "]
        Same_dir = data[" Same_dir "]
        output = data[" output "]

    with open(Script_path, "r") as my_file:  # read script file and get the directories and commands from it `
        for line in my_file:
            des = None
            if command_counter <= Max_commands_int:
                command = line.split()[0]  # split the first column in the files, it contains all commands
                dir = re.search('<(.*?)>',
                                line)  # get directory for each function. note: for Grep function i took the name of the wanted file
                dir = dir[1]
                if command != "Categorize":
                    des = re.search('>\s<(.*?)>\n', line)  # get specific directory
                    des = des[1]
                    if os.path.exists(des) == False and os.path.isdir(des) == False and os.path.exists(dir) == False and os.path.isdir(dir) == False:
                        flag = False
                        c = 1
                        count = len(open(Script_path).readlines())
                        while c <= count:
                            Status["line-%d" % (c)] = '%s' % (flag)
                            c = c+1
                        Json = json.dumps(Status, indent=4)
                        return Json, Max_log_files, output

                    # Call each functions for each command
                if command == "Grep":
                    GrepStatus = CommandClass.Command(dir, des).grep()
                    Status["line-%d" % (command_counter)] = '%s' % (GrepStatus)
                elif command == "Mv_last":
                    Mvstatus = CommandClass.Command(dir, des).mv_last()
                    Status["line-%d" % (command_counter)] = '%s' % (Mvstatus)
                elif command == "Categorize":
                    Cate = CommandClass.Command(None, dir).Categorize(Threshold_size_int)
                    Status["line-%d" % (command_counter)] = '%s' % (Cate)
                command_counter = command_counter + 1  # To executed the max values
            else:
                print("Error, You Have reached the maximum command execution per script.")
    Json = json.dumps(Status, indent=4)  # Save the result in Json to store it to logging function
    my_file.close()
    return Json, Max_log_files, output




optionP = optparse.OptionParser()  # object for option parser
optionP.add_option("-s", "--scriptpath", dest="Script_path",
                   help="Script path")  # first argument will be -s and it's point to the script path
optionP.add_option("-o", "--outlog", dest="Out_log",
                   help="Output log file ")  # Second argument will -o with output path file
(values, keys) = optionP.parse_args()
Script_path = values.Script_path  # store values and save them to variables
Out_log = values.Out_log


try:
    (Json_status, Max_log, filetype) = extraction_commands(Script_path)
    logging_file(Json_status, Out_log, Max_log, filetype)
except FileNotFoundError as not_found:
    print("Error, Please sure that the path is written correctly")
    logging.basicConfig(filename='output.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
    logging.error("Error, Not found path")
