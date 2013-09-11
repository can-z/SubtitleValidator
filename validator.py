class Validator:
    def __init__(self, filename):
        self.filename = filename
            
    
    def line_format(self):
        f = file(self.filename)
        
        line = f.readline()
        cur_line = 1
        while line != None:
            if not line.strip().isdigit():
                print "Line " + cur_line + ": Invalid subtitle index (" + line + ")"
                return False
            
            line = f.readline()
            
            
            
                
            
        
    def whitespace(self):
        
        
        return True
    