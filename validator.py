import re

class Validator:
    def __init__(self, filename):
        self.filename = filename
        self.line_numbers = []
        self.timestamps = []
        self.chinese_captions = []
        self.english_captions = []
        self.parsed = False
            
    
    def parse_file(self):
        f = file(self.filename)
        
        line = f.readline()
        cur_line = 1
        while line != "":
            if not line.strip().isdigit():
                print "Line " + str(cur_line) + ": Invalid subtitle index \nActual: " + line
                return False
            else:
                self.line_numbers.append(line)

            
            line = f.readline()
            cur_line += 1
            
            timestamp_regex = re.compile(\
            '(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)')
            
            timestamp_result = timestamp_regex.match(line)
            if (not timestamp_result):
                print "Line " + str(cur_line) + ": Invalid timestamp line \nActual: " + line
                return False
            else:
                self.timestamps.append(line)
            
            line = f.readline()
            cur_line += 1
            self.chinese_captions.append(line)
            
            line = f.readline()
            cur_line += 1
            self.english_captions.append(line)
            
            line = f.readline()
            cur_line += 1
            if line.strip() != "":
                print "Line " + str(cur_line) + ": Empty line expected \nActual: " + line
                return False
                
            line = f.readline()
            cur_line += 1
        
        self.parsed = True    
        return True    
            
                
            
        
    def whitespace(self):
        
        haserror = False
        
        if not self.parsed:
            print "File not parsed. Exiting."
            
        index = 1
        for line in self.chinese_captions:
            if line.lstrip() != line:
                haserror = True
                print str(index) + ": whitespace at the beginning of sentence\nActual: " + line
            if find_whitespace_right(line):
                haserror = True
                print str(index) + ": whitespace at the end of sentence\nActual: " + line
            index += 1
        
        index = 1
        for line in self.english_captions:
            if line.lstrip() != line:
                haserror = True
                print str(index) + ": whitespace at the beginning of sentence\nActual: " + line
            if find_whitespace_right(line):
                haserror = True
                print str(index) + ": whitespace at the end of sentence\nActual: " + line
            index += 1

        return not haserror
			
def find_whitespace_right(line):
        
    right_whitespace_re = re.compile('^.*[ \t\f\v]+$')
    right_whitespace_result = right_whitespace_re.match(line)
    return right_whitespace_result
        
    
if __name__ == "__main__":
    v = Validator("step1.p2.done by.raitorm.srt")
    print v.parse_file()
    print v.whitespace()
