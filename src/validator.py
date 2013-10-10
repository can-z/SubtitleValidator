import re
import datetime
import os
import unicodedata


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
        self.system_error_list = []

        if write_to_file:
            self.result_file = file("local_results/" + os.path.basename(filename) + "result-" +
                                    "-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") +
                                    ".txt", "w")

    def parse_file(self):
        parse_file = file(self.filename)
        
        line = parse_file.readline()
        try:
            line = line.decode("utf-8-sig")  # Remove BOM from first line
        except UnicodeDecodeError:
            self.system_error_list.append(
                "Error decoding the following line while removing BOM from file.\n Line: " + line)

        cur_line = 1
        self.initial_upper_list.append(True)
        is_current_upper = True
        
        while line != "":
            if not line.strip().isdigit():
                self.error(cur_line, message_with_context("invalid_line_number", line.strip()))
                return False
            else:
                self.line_numbers.append(line)

            line = parse_file.readline()
            cur_line += 1
            
            timestamp_regex = re.compile('(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)')
            
            timestamp_result = timestamp_regex.match(line)
            if not timestamp_result:
                self.error(cur_line, message_with_context("invalid_time_stamp", line.strip()))
                return False
            else:
                self.timestamps.append(line)
            
            line = parse_file.readline()
            cur_line += 1
            try:
                self.chinese_captions.append(really_smart_decode(line).encode("utf-8"))
            except UnicodeDecodeError:
                self.system_error_list.append("Error smart-decoding Line " + str(cur_line) + " while parsing.")
                self.chinese_captions.append("")
            
            line = parse_file.readline()
            cur_line += 1
            self.english_captions.append(line)
            has_english_line = True
            if len(line.strip()) > 0: 
                end_of_sentence_re = re.compile('.*[\\.\\?!\\*](\'|")*$')
                end_of_sentence_result = end_of_sentence_re.match(line.replace("...", "").strip())
                if end_of_sentence_result:
                    self.initial_upper_list.append(True)
                    is_current_upper = True
                else:
                    self.initial_upper_list.append(False)
                    is_current_upper = False
            else:
                has_english_line = False
                self.initial_upper_list.append(is_current_upper)

            if has_english_line:
                line = parse_file.readline()
                cur_line += 1
            if line.strip() != "":
                self.error(cur_line, message_with_context("empty_line_required", line.strip()))
                return False

            while line != "" and line.strip() == "":
                line = parse_file.readline()
                cur_line += 1

        parse_file.close()

        self.parsed = True    
        return True    

    def whitespace_check(self):

        if not self.parsed:
            print "File not parsed. Exiting."
            
        index = 1
        for line in self.chinese_captions:
            
            if len(line.strip()) > 0:
                if line.lstrip() != line:
                    self.error(index, message_with_context("extra_whitespace_begin", line.strip()))
                if find_whitespace_right(line):
                    self.error(index, message_with_context("extra_whitespace_end", line.strip()))
            index += 1
        
        index = 1
        for line in self.english_captions:
            if len(line.strip()) > 0:
                if line.lstrip() != line:
                    self.error(index, message_with_context("extra_whitespace_begin", line.strip()))
                if find_whitespace_right(line):
                    self.error(index, message_with_context("extra_whitespace_end", line.strip()))
            index += 1

    def upper_case_check(self):
        
        index = 1
        for line in self.english_captions:

            first_letter = find_first_letter(line)

            if self.initial_upper_list[index - 1]:
                if first_letter.islower():
                    if index == 1:
                        self.error(index, message_with_context("require_upper_case", line.strip(),
                                                               prev_line="**This is the first line of the text**"))
                    else:
                        self.error(index, message_with_context("require_upper_case", line.strip(),
                                                               prev_line=self.english_captions[index - 2].strip()))
            
            index += 1
    
    def lower_case_check(self):
        index = 1

        for line in self.english_captions:
            
            first_letter = find_first_letter(line)
            
            if not self.initial_upper_list[index - 1]:
                if first_letter.isupper():
                    if index == 1:
                        self.warning(index, message_with_context("require_lower_case", line.strip(),
                                                                 prev_line="**This is the first line of the text**"))
                    else:
                        self.warning(index, message_with_context("require_lower_case", line.strip(),
                                                                 prev_line=self.english_captions[index - 2].strip()))
            
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
                self.error(index, message_with_context("two_space_chinese", line.strip()))

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
                        self.error(index, message_with_context("one_space_english", line.strip()))
                        break
                    else:
                        prev = True
                else:
                    prev = False

            index += 1

    def ellipsis_check(self):

        index = 1
        for line in self.english_captions:
            if line.strip().endswith("..."):
                if index < len(self.english_captions):
                    self.warning(index, message_with_context("ellipsis", line.strip(),
                                                             next_line=self.english_captions[index].strip()))
                else:
                    self.warning(index, message_with_context("ellipsis", line.strip(),
                                                             next_line="**This is the last line of the text**"))

            index += 1

    def error(self, line_number, message):
        self.error_list.append((line_number, "[ERROR] " + message))
    
    def warning(self, line_number, message):
        self.error_list.append((line_number, "[WARNING] " + message))

    def sort_errors(self):
        self.error_list.sort(key=lambda x: x[0])

    def produce_result_file(self, is_format_error):
        result_string = ""

        if is_format_error:
            result_string += get_text("format_error_message_1").decode("utf-8") + "\n"\
                + get_text("format_error_message_2").decode("utf-8") + "\n"\
                + get_text("format_error_message_3").decode("utf-8") + "\n"\
                + get_text("format_error_message_4").decode("utf-8") + "\n"\
                + get_text("format_error_message_5").decode("utf-8") + "\n"\
                + get_text("format_error_message_6").decode("utf-8") + "\n\n"

        for e in self.error_list:
                try:
                    decoded_message = really_smart_decode(e[1])
                except UnicodeDecodeError:
                    self.system_error_list.append("Error smart-decoding Subtitle Line " + str(e[0]))
                    decoded_message = ""

                result_string += str(e[0]) + ": " + decoded_message + "\n\n"

        for e in self.system_error_list:
            result_string += really_smart_decode(e) + "\n\n"

        if self.write_to_file:
            self.result_file.write(result_string.encode("utf-8"))

        return result_string

    def perform_all_checks(self):
        self.whitespace_check()
        self.upper_case_check()
        self.lower_case_check()
        self.double_whitespace_check()
        self.single_whitespace_check()
        self.ellipsis_check()

        self.sort_errors()


def find_whitespace_right(line):
        
    right_whitespace_re = re.compile('^.*[ \t\f\v]+$')
    right_whitespace_result = right_whitespace_re.match(line)
    return right_whitespace_result


def get_text(key):

    text_file = file("text.properties")

    for line in text_file:
        if len(line.split("=")) == 2:
            if key == line.split("=")[0]:
                return line.split("=")[1].strip()
    raise IOError("Key " + key + " does not exist")


def message_with_context(key, cur_line, prev_line=None, next_line=None):

    res = get_text(key) + "\n\t" + get_text("actual") + ": " + cur_line
    if prev_line is not None:
        res += "\n\t" + get_text("previous") + ": " + prev_line
    if next_line is not None:
        res += "\n\t" + get_text("next") + ": " + next_line

    return res


def smart_decode(s):

    try:
        decoded_message = s.decode("gb2312")
    except UnicodeDecodeError:
        decoded_message = s.decode("utf-8")

    return decoded_message


def find_first_letter(s):
    
    for letter in s:
        if letter.isalpha():
            return letter
    
    return ""


def really_smart_decode(s):

    return really_smart_decode_recur(s, 0, 1, "", "ascii")


def really_smart_decode_recur(s, start, end, res, encoding):

    try:
        cur_code = s[start:end].decode(encoding)
        if encoding != "ascii" and not is_valid_character(cur_code):
            raise UnicodeDecodeError(encoding, '', start, end, 'Not chinese.')

        res += cur_code

        if end < len(s):
            start = end
            end += 1
            return really_smart_decode_recur(s, start, end, res, "ascii")
        else:
            return res
    except UnicodeDecodeError:

        if encoding == "ascii":
            return really_smart_decode_recur(s, start, end, res, "utf-8")

        if end - start == 2:
            if encoding == "utf-8":
                end += 1
                return really_smart_decode_recur(s, start, end, res, "utf-8")
            if encoding == "gb2312":
                res += "**"  # Skip two bytes when a character is replaced with "**".
                if end < len(s):
                    start = end
                    end += 1
                    return really_smart_decode_recur(s, start, end, res, "ascii")
                else:
                    return res
        elif end - start == 3:
            if encoding == "utf-8":
                return really_smart_decode_recur(s, start, end - 2, res, "gb2312")
        else:
            return really_smart_decode_recur(s, start, end + 1, res, encoding)


def is_valid_character(code):

    if len(code) > 1:
        return False

    return u"\u4e00" <= code <= u"\u62ff" or u"\u6300" <= code <= u"\u77ff" or u"\u7800" <= code <= u"\u8cff" or\
        u"\u8d00" <= code <= u"\u9fcc" or unicodedata.category(code) == "Po"