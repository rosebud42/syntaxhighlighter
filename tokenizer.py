

class Error:  # error class 
    def __init__(self, description, error_line):
        self.description = description
        self.error_line = error_line

    def __str__(self):
        return f"Error (Satır {self.error_line}): {self.description}"


class Token: # special token class 
    def __init__(self, type, value, line):
        self.type = type 
        self.value = value
        self.line = line # important for understanding error line

class Tokenizer:
    def __init__(self):
        self.TOKENS = []
        self.KEYWORDS =  ["if", "else", "while", "def", "return","in","range","for","elif","switch","case","default"] #special keywords
        self.indent_stack = [0]  # helps to understand indents

    def count_leading_spaces(self, code, index): # indent calculation
        count = 0
        while index < len(code) and code[index] == ' ':
            count += 1
            index += 1
        return count
    
    def tokenize(self, code): #tokenize the given code
        i = 0 # char index
        current_line = 1 # current line for error messages
        line_start = True # important for indent calculation


        while i<len(code):
            char = code[i]

            if line_start or char == '\t':
                # calculate the number of spaces at the begining of a line
                space_count = self.count_leading_spaces(code, i)
                i += space_count
                line_start = False


                # understand indent or dedent by difference of spaces
                if space_count > self.indent_stack[-1]:
                    self.indent_stack.append(space_count)
                    self.TOKENS.append(Token("INDENT", ' ' * space_count, current_line))
                while space_count < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.TOKENS.append(Token("DEDENT", '', current_line))

            char = code[i]
            
            # TOKENIZE SYSTEM


            if char == "#":
                    start_pos = i
                    while i < len(code) and code[i] != "\n":
                        i += 1
                    comment_value = code[start_pos:i]
                    self.TOKENS.append(Token("COMMENT", comment_value, current_line))
                    continue
            
            if char.isalpha() or char == '_': # an identifier can start with '_' 
                first = i
                while i < len(code) and (code[i].isalnum() or code[i] == '_' ):
                   i+=1
                word = code[first:i]
                if word in self.KEYWORDS:
                    self.TOKENS.append(Token("KEYWORD", word, current_line))
                elif word in ("True","False"):
                    self.TOKENS.append(Token("BOOLEAN",word,current_line))
                else:
                    self.TOKENS.append(Token("IDENTIFIER",code[first:i], current_line))
                continue

            elif char.isdigit():  # number or float token
                first = i
                has_dot = False
                while i < len(code) and (code[i].isdigit() or (code[i] == '.' and not has_dot)):
                    if code[i] == '.':
                        has_dot = True
                    i += 1
                number_value = code[first:i]

                # '.' ile başlıyorsa veya bitiyorsa, bu geçersiz bir float olabilir
                if number_value.startswith('.') or number_value.endswith('.'):
                    error = Error(f"Geçersiz sayı formatı: {number_value}", current_line)
                    raise SyntaxError(error)

                if has_dot:
                    self.TOKENS.append(Token("FLOAT", number_value, current_line))
                else:
                    self.TOKENS.append(Token("NUMBER", number_value, current_line))
                continue


            # comparison tokens
            elif char == '=' and i+1 < len(code) and code[i+1] == '=':
                self.TOKENS.append(Token("EQEQUAL", '==', current_line))
                i += 2
                continue

            elif char == '!' and i+1 < len(code) and code[i+1] == '=':
                self.TOKENS.append(Token("NOTEQUAL", '!=', current_line))
                i += 2
                continue

            elif char == '<':
                if i+1 < len(code) and code[i+1] == '=':
                    self.TOKENS.append(Token("LESSEQUAL", '<=', current_line))
                    i += 2
                else:
                    self.TOKENS.append(Token("LESS", '<', current_line))
                    i += 1
                continue

            elif char == '>':
                if i+1 < len(code) and code[i+1] == '=':
                    self.TOKENS.append(Token("GREATEREQUAL", '>=', current_line))
                    i += 2
                else:
                    self.TOKENS.append(Token("GREATER", '>', current_line))
                    i += 1
                continue
            
            # arithmetic tokens
            elif char == '+':   
                self.TOKENS.append(Token("PLUS",'+',current_line)) 
            elif char == '-':
                self.TOKENS.append(Token("MINUS",'-',current_line))
            elif char == '*':
                self.TOKENS.append(Token("MULTIPLY",'*',current_line))
            elif char == '/':
                self.TOKENS.append(Token("DIVIDE",'/',current_line))
            elif char == '=':
                self.TOKENS.append(Token('EQUALS','=',current_line))
            elif char == '(':
                self.TOKENS.append(Token("LPAREN", '(',current_line))
            elif char == ')':
                self.TOKENS.append(Token("RPAREN", ')',current_line))
            elif char == '[':
                self.TOKENS.append(Token("LBRACKET",'[',current_line))
            elif char == ']':
                self.TOKENS.append(Token("RBRACKET",']',current_line))
            elif char == ':':
                self.TOKENS.append(Token("COLON", ':', current_line))
            elif char == ',':
                self.TOKENS.append(Token("COMMA",',',current_line))
            elif char == '"': # string token
                i+=1
                string = ""
                while i<len(code) and code[i] != '"':
                    string += code[i]
                    i+=1
                if i>=len(code):
                    error = Error(f"Unclosed string literal!",current_line)
                    raise SyntaxError(error)
                self.TOKENS.append(Token("STRING", string, current_line))


            elif char == '\n': # new line token
                self.TOKENS.append(Token("NEWLINE", '\\n',current_line))
                current_line += 1
                line_start = True
                i+=1
                continue
            elif char == ' ':
                i+=1
                continue
            else:
                error = Error(f"Undefined char! {char}",current_line)
                raise SyntaxError(error)


            i+=1
        
        if self.TOKENS and self.TOKENS[-1].type != "NEWLINE":
            self.TOKENS.append(Token("NEWLINE", '\\n', current_line))
                
        while len(self.indent_stack) > 1: # dedent at the end
            self.indent_stack.pop()
            self.TOKENS.append(Token("DEDENT", '', current_line))
        
        return self.TOKENS