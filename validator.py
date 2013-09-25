import re
import datetime
import Tkinter
import tkFileDialog
import sys
import os


class Validator:
    def __init__(self, filename):
        self.filename = filename
        self.line_numbers = []
        self.timestamps = []
        self.chinese_captions = []
        self.english_captions = []
        self.parsed = False
        self.initial_upper_list = []

        self.result_file = file(os.path.basename(filename) + "result-" +
                                "-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") +
                                ".txt", "w")

    def parse_file(self):
        parse_file = file(self.filename)
        
        line = parse_file.readline()
        cur_line = 1
        self.initial_upper_list.append(True)
        
        while line != "":
            if not line.strip().isdigit():
                self.error("Line " + str(cur_line) + ": Invalid subtitle index \nActual: " + line.strip())
                return False
            else:
                self.line_numbers.append(line)

            line = parse_file.readline()
            cur_line += 1
            
            timestamp_regex = re.compile('(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)')
            
            timestamp_result = timestamp_regex.match(line)
            if not timestamp_result:
                self.error("Line " + str(cur_line) + ": Invalid timestamp line \nActual: " + line.strip())
                return False
            else:
                self.timestamps.append(line)
            
            line = parse_file.readline()
            cur_line += 1
            self.chinese_captions.append(line)
            
            line = parse_file.readline()
            cur_line += 1
            self.english_captions.append(line)
            end_of_sentence_re = re.compile('.*[\\.\\?!](\'|")*$')
            end_of_sentence_result = end_of_sentence_re.match(line.strip())
            if end_of_sentence_result:
                self.initial_upper_list.append(True)
            else:
                self.initial_upper_list.append(False)
            
            line = parse_file.readline()
            cur_line += 1
            if line.strip() != "":
                self.error("Line " + str(cur_line) + ": Empty line expected \nActual: " + line.strip())
                return False
                
            line = parse_file.readline()
            cur_line += 1
        
        self.parsed = True    
        return True    

    def whitespace_check(self):
        
        has_error = False
        
        if not self.parsed:
            print "File not parsed. Exiting."
            
        index = 1
        for line in self.chinese_captions:
            if line.lstrip() != line:
                has_error = True
                self.error(str(index) + ": whitespace at the beginning of sentence\n\tActual: " + line.strip())
            if find_whitespace_right(line):
                has_error = True
                self.error(str(index) + ": whitespace at the end of sentence\n\tActual: " + line.strip())
            index += 1
        
        index = 1
        for line in self.english_captions:
            if line.lstrip() != line:
                has_error = True
                self.error(str(index) + ": whitespace at the beginning of sentence\n\tActual: " + line.strip())
            if find_whitespace_right(line):
                has_error = True
                self.error(str(index) + ": whitespace at the end of sentence\n\tActual: " + line.strip())
            index += 1

        return not has_error

    def upper_case_check(self):
        
        index = 0
        has_error = False
        for line in self.english_captions:
            first_letter = line.strip()[0]
            if self.initial_upper_list[index]:
                if first_letter.islower():
                    has_error = True
                    if index == 0:
                        self.error(str(index + 1) + ": Expect upper case letter\n\tActual: " +
                                   line.strip() + "\n\tPrevious: **This is the first line of the text**")
                    else:
                        self.error(str(index + 1) + ": Expect upper case letter\n\tActual: " +
                                   line.strip() + "\n\tPrevious: " + self.english_captions[index - 1].strip())
            
            index += 1
        return not has_error
    
    def lower_case_check(self):
        index = 0
        has_error = False
        for line in self.english_captions:
            first_letter = line.strip()[0]
            
            if not self.initial_upper_list[index]:
                if first_letter.isupper():
                    has_error = True
                    if index == 0:
                        self.warning(str(index + 1) + ": Expect lower case letter\n\tActual: " +
                                     line.strip() + "\n\tPrevious: **This is the first line of the text**")
                    else:
                        self.warning(str(index + 1) + ": Expect lower case letter\n\tActual: " +
                                     line.strip() + "\n\tPrevious: " + self.english_captions[index - 1].strip())
            
            index += 1
        return not has_error

    def double_whitespace_check(self):
        """Check if any two segments are separated by != two spaces.
    Note that this method assumes that the hyphenation is done correctly.
    (i.e. two spaces before hyphen and no space after.)"""

        index = 1
        has_error = False
        for line in self.chinese_captions:

            line = line.replace("-", "")
            double_whitespace_regex = re.compile('[^ ]+ [^ ]+')

            if double_whitespace_regex.match(line):
                has_error = True
                self.error(str(index) + ": Two spaces are required between words in Chinese captions.\n\tActual: " +
                           line.strip())

            index += 1

        return not has_error

    def error(self, message):
        self.result_file.write("[ERROR] " + message + "\n\n")
    
    def warning(self, message):
        self.result_file.write("[WARNING] " + message + "\n\n")


def find_whitespace_right(line):
        
    right_whitespace_re = re.compile('^.*[ \t\f\v]+$')
    right_whitespace_result = right_whitespace_re.match(line)
    return right_whitespace_result
         
if __name__ == "__main__":

    USE_TK = True

    if USE_TK:
        root = Tkinter.Tk()
        root.withdraw()
    
        f = tkFileDialog.askopenfilename()
    else:
        f = raw_input("Enter the path of the subtitle file:" )

    if not f:
        sys.exit(0)
    v = Validator(f)
    v.parse_file()
    v.whitespace_check()
    v.upper_case_check()
    v.lower_case_check()
    v.double_whitespace_check()