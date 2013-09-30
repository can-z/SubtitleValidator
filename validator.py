import re
import datetime
import Tkinter
import tkFileDialog
import sys
import os


USE_TK = True


class Validator:
    def __init__(self, filename, write_to_file):

        self.write_to_file = write_to_file
        self.filename = filename
        self.line_numbers = []
        self.timestamps = []
        self.chinese_captions = []
        self.english_captions = []
        self.parsed = False
        self.initial_upper_list = []
        self.error_list = []

        if write_to_file:
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
                self.error(cur_line, "Invalid subtitle index \nActual: " + line.strip())
                return False
            else:
                self.line_numbers.append(line)

            line = parse_file.readline()
            cur_line += 1
            
            timestamp_regex = re.compile('(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)')
            
            timestamp_result = timestamp_regex.match(line)
            if not timestamp_result:
                self.error(cur_line, "Invalid timestamp line \nActual: " + line.strip())
                return False
            else:
                self.timestamps.append(line)
            
            line = parse_file.readline()
            cur_line += 1
            self.chinese_captions.append(line)
            
            line = parse_file.readline()
            cur_line += 1
            self.english_captions.append(line)
            end_of_sentence_re = re.compile('.*[\\.\\?!\\*](\'|")*$')
            end_of_sentence_result = end_of_sentence_re.match(line.replace("...", "").strip())
            if end_of_sentence_result:
                self.initial_upper_list.append(True)
            else:
                self.initial_upper_list.append(False)
            
            line = parse_file.readline()
            cur_line += 1
            if line.strip() != "":
                self.error(cur_line, "Empty line expected \nActual: " + line.strip())
                return False
                
            line = parse_file.readline()
            cur_line += 1
        
        self.parsed = True    
        return True    

    def whitespace_check(self):

        if not self.parsed:
            print "File not parsed. Exiting."
            
        index = 1
        for line in self.chinese_captions:
            if line.lstrip() != line:
                self.error(index, "Whitespace at the beginning of sentence\n\tActual: " + line.strip())
            if find_whitespace_right(line):
                self.error(index, "Whitespace at the end of sentence\n\tActual: " + line.strip())
            index += 1
        
        index = 1
        for line in self.english_captions:
            if line.lstrip() != line:
                self.error(index, "Whitespace at the beginning of sentence\n\tActual: " + line.strip())
            if find_whitespace_right(line):
                self.error(index, "Whitespace at the end of sentence\n\tActual: " + line.strip())
            index += 1

    def upper_case_check(self):
        
        index = 1
        for line in self.english_captions:
            if len(line.strip()) > 0:
                first_letter = line.strip()[0]
            else:
                first_letter = "";
            if self.initial_upper_list[index - 1]:
                if first_letter.islower():
                    if index == 1:
                        self.error(index, "Expect upper case letter\n\tActual: " +
                                   line.strip() + "\n\tPrevious: **This is the first line of the text**")
                    else:
                        self.error(index, "Expect upper case letter\n\tActual: " +
                                   line.strip() + "\n\tPrevious: " + self.english_captions[index - 2].strip())
            
            index += 1
    
    def lower_case_check(self):
        index = 1

        for line in self.english_captions:
            if len(line.strip()) > 0:
                first_letter = line.strip()[0]
            else:
                first_letter = ""
            if not self.initial_upper_list[index - 1]:
                if first_letter.isupper():
                    if index == 1:
                        self.warning(index, "Expect lower case letter\n\tActual: " +
                                     line.strip() + "\n\tPrevious: **This is the first line of the text**")
                    else:
                        self.warning(index, "Expect lower case letter\n\tActual: " +
                                     line.strip() + "\n\tPrevious: " + self.english_captions[index - 2].strip())
            
            index += 1

    def double_whitespace_check(self):
        """Check if any two segments are separated by != two spaces.
    Note that this method assumes that the hyphenation is done correctly.
    (i.e. two spaces before hyphen and no space after.)"""

        index = 1

        for line in self.chinese_captions:

            line = line.replace("-", "")
            double_whitespace_regex = re.compile('[^ ]+(( )|( {3,}))[^ ]+')

            if double_whitespace_regex.match(line):
                self.error(index, "Two spaces are required between words in Chinese captions.\n\tActual: " +
                           line.strip())

            index += 1

    def single_whitespace_check(self):
        """English captions only. Assume hyphenation is correct (one space before and after the hyphen)."""

        index = 1
        for line in self.english_captions:

            line = line.replace("- ", "")

            # For some reason, re does not work on this one (Python 2.7). Try the re: [^ ]+((\s)\s+)[^ ]+
            # or [^ ]+(( ) +)[^ ]+
            # Hence this weird solution.
            prev = False
            for w in line:
                if w == " ":
                    if prev:
                        self.error(index, "One space is required between words in English captions.\n\tActual: " +
                                          line.strip())
                        break
                    else:
                        prev = True
                else:
                    prev = False

            index += 1

    def ellipsis_check(self):

        index = 1
        for line in self.english_captions:
            if "..." in line:
                if index < len(self.english_captions):
                    self.manual(index, "Found Ellipsis! Check capitalization of the next line\n\tActual: " +
                                       line.strip() + "\n\tNext: " + self.english_captions[index].strip())
                else:
                    self.manual(index, "Found Ellipsis! Check capitalization of the next line\n\tActual: " +
                                       line.strip() + "\n\tNext: **This is the last line of the file**")
            index += 1

    def error(self, line_number, message):
        self.error_list.append((line_number, "[ERROR] " + message))
    
    def warning(self, line_number, message):
        self.error_list.append((line_number, "[WARNING] " + message))

    def manual(self, line_number, message):
        self.error_list.append((line_number, "[MANUAL] " + message))

    def produce_result_file(self):

        self.error_list.sort(key=lambda x: x[0])

        for e in self.error_list:
            if WRITE_TO_FILE:
                self.result_file.write(str(e[0]) + ": " + e[1] + "\n\n")
            else:
                print str(e[0]) + ": " + e[1] + "\n"


def find_whitespace_right(line):
        
    right_whitespace_re = re.compile('^.*[ \t\f\v]+$')
    right_whitespace_result = right_whitespace_re.match(line)
    return right_whitespace_result


if __name__ == "__main__":

    if USE_TK:
        root = Tkinter.Tk()
        root.withdraw()
    
        f = tkFileDialog.askopenfilename()
    else:
        f = raw_input("Enter the path of the subtitle file:" )

    if not f:
        sys.exit(0)
    v = Validator(f, True)
    if not v.parse_file():
        v.produce_result_file()
        sys.exit(-1)
    v.whitespace_check()
    v.upper_case_check()
    v.lower_case_check()
    v.double_whitespace_check()
    v.single_whitespace_check()
    v.ellipsis_check()
    v.produce_result_file()