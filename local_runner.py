import Tkinter
import tkFileDialog
import sys
import datetime
import shutil
import os
import traceback
from src import validator

LOG = False


def error_logger(type, value, tb):
    shutil.copy(trouble_maker, "troublemaker/" + os.path.basename(trouble_maker))
    for line in traceback.format_exception(type, value, tb):
        print line

if __name__ == "__main__":

    if LOG:
        sys.excepthook = error_logger
        log = open("log/" + datetime.datetime.now().strftime("%Y%m%d") + ".log", "a")
        sys.stdout = log
        sys.stderr = log

        log.write("*********************\n*")
        log.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*\n*********************\n")

    root = Tkinter.Tk()
    root.withdraw()

    f = tkFileDialog.askopenfilename()

    if not f:
        sys.exit(0)
    global trouble_maker
    trouble_maker = f

    if LOG:
        log.write("File name: " + f.encode("utf8", errors="ignore") + "\n\n")

    v = validator.Validator(f, True)

    if not v.parse_file():
        v.produce_result_file(True)
        sys.exit(-1)
    v.perform_all_checks()
    v.produce_result_file(False)
