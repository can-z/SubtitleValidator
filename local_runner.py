import Tkinter
import tkFileDialog
import sys
from src import validator

if __name__ == "__main__":

    root = Tkinter.Tk()
    root.withdraw()

    f = tkFileDialog.askopenfilename()

    if not f:
        sys.exit(0)
    v = validator.Validator(f, True)
    if not v.parse_file():
        v.produce_result_file(True)
        sys.exit(-1)
    v.perform_all_checks()
    v.produce_result_file(False)