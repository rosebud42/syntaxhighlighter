from tokenizer import Token
from tokenizer import Error


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens # coming from tokenizer class
        self.pos = 0 # current token number in progress

    def current_token(self): # returns current token by pos number
        if self.pos < len(self.tokens): 
            if self.tokens[self.pos].type == "COMMENT": # skip token if the type is comment
                self.pos+=1
                self.current_token()
            return self.tokens[self.pos]
        return Token("EOF", None, None) # returns none if self.pos is bigger than the length of tokens
    def next_token(self): # returns the next token  
        if (self.pos)+1 < len(self.tokens):
            return self.tokens[self.pos+1]
        return Token("EOF", None, None)
    
    def eat(self, expected_type): # checks if the current token type is the same as the expected type
        token = self.current_token()
        if token.type == expected_type:
            self.pos += 1
            return token  # return token if there isn't any problem
        else:  #raise error
            error = Error(f"Expected token type is not found! Expected: {expected_type}, Found : {token.type} - {token.value}",token.line)
            raise SyntaxError(error)
                
    def parse(self):
        self.statement_list()  # can handle more than one statements
        if self.current_token().type != "EOF":
            error = Error(f"Parsing error! More tokens found than expected.",-1)
            raise SyntaxError(error)
        # parsing is done successfully
    
    def statement_list(self):
        while True:
            token = self.current_token() # fetches the current token
            if token.type == "IDENTIFIER": 
                self.statement()
            elif token.type == "KEYWORD" and token.value == "return": # break the loop if the keyword is break
                break   
            elif token.type == "KEYWORD":
                self.statement()
            elif token.type == "NEWLINE":
                self.eat("NEWLINE")         
            else:
                break

    def statement(self):
        token = self.current_token()
        
        if token.type == "IDENTIFIER": # func call statement 
            if self.next_token().type == "LPAREN":
                self.func_call_statement()
            else:
                self.assignment()
        elif token.type == "KEYWORD" and token.value == "switch":
            self.switch_statement()
        elif token.type == "KEYWORD" and token.value == "if": # if statement
            self.if_statement()
        elif token.type == "KEYWORD" and token.value == "while": # while statement
            self.while_statement()
        elif token.type == "KEYWORD" and token.value == "for": # for statement
            self.for_statement()
        elif token.type == "KEYWORD" and token.value == "def": # function definition statement
            self.def_statement()
        else: # raise error 
            error = Error(f"Undefined statement beginning: {token.type} {token.value}",token.line) 
            raise SyntaxError(error)

    def assignment(self): # assignment statement
        print("assignment in progress!") # test line
        self.eat("IDENTIFIER")  # lhs
        self.eat("EQUALS")      
        self.expression()     # rhs   
        self.eat("NEWLINE")     
    
    def if_statement(self):
        print("if statement in progress!") # test line
        self.eat("KEYWORD")  # if keyword
        self.expression()
        self.eat("COLON")
        self.eat("NEWLINE")
        self.eat("INDENT")
        self.statement_list()
        self.eat("DEDENT")

        # elif 
        while self.current_token().type == "KEYWORD" and self.current_token().value == "elif":
            self.eat("KEYWORD")
            self.expression()
            self.eat("COLON")
            self.eat("NEWLINE")
            self.eat("INDENT")
            self.statement_list()
            self.eat("DEDENT")

        # else 
        if self.current_token().type == "KEYWORD" and self.current_token().value == "else":
            self.eat("KEYWORD")
            self.eat("COLON")
            self.eat("NEWLINE")
            self.eat("INDENT")
            self.statement_list()
            self.eat("DEDENT")

    def while_statement(self):
        print("While statement in progress!") #test line
        self.eat("KEYWORD")
        self.expression()
        self.eat("COLON")
        self.eat("NEWLINE")
        self.eat("INDENT")
        self.statement_list()
        self.eat("DEDENT")
    
    def for_statement(self):
        print("For statement in progress!")
        self.eat("KEYWORD") #for
        self.eat("IDENTIFIER")
        self.eat("KEYWORD") # in
        if(self.current_token().type == "KEYWORD"):
            self.eat("KEYWORD") # range
            self.eat("LPAREN")
            self.eat("NUMBER")
            self.eat("COMMA")
            self.eat("NUMBER")
            self.eat("RPAREN")
        else:
            self.expression() 
        self.eat("COLON")
        self.eat("NEWLINE") 
        self.eat("INDENT")
        self.statement_list()
        self.eat("DEDENT")

    def switch_statement(self):
        print("switch statement in progress!")
        
        self.eat("KEYWORD")  # 'switch'
        self.expression()    # expression after switch
        self.eat("COLON")
        self.eat("NEWLINE")
        self.eat("INDENT")

        # At least one case block is expected
        while self.current_token().type == "KEYWORD" and self.current_token().value == "case":
            self.eat("KEYWORD")      # 'case'
            self.expression()        # case condition
            self.eat("COLON")
            self.eat("NEWLINE")
            self.eat("INDENT")
            self.statement_list()    # statements inside case
            self.eat("DEDENT")
        if self.current_token().type == "KEYWORD" and self.current_token().value == "default":
            self.eat("KEYWORD")      # 'case'
            self.eat("COLON")
            self.eat("NEWLINE")
            self.eat("INDENT")
            self.statement_list()    # statements inside case
            self.eat("DEDENT")
        self.eat("DEDENT")



    def def_statement(self):
        print("function definition statement in progress!")
        self.eat("KEYWORD")
        self.eat("IDENTIFIER")
        self.eat("LPAREN")
        while(self.current_token().type == "IDENTIFIER"):
            self.eat("IDENTIFIER")
            if(self.current_token().type != "RPAREN"):
                self.eat("COMMA")
        self.eat("RPAREN")
        self.eat("COLON")
        self.eat("NEWLINE")
        self.eat("INDENT")
        self.statement_list()
        if(self.current_token().type == "KEYWORD"):
            self.eat("KEYWORD") #return
            self.expression()
            self.eat("NEWLINE")
        self.eat("DEDENT")

    def func_call_statement(self):
        print("function call statement  in progress!")
        self.eat("IDENTIFIER")  # function name
        self.eat("LPAREN")      # (

        # read all args if not empty
        if self.current_token().type in ("NUMBER", "STRING", "IDENTIFIER","FLOAT"):
            self.argument()  # first arg

            while self.current_token().type == "COMMA":
                self.eat("COMMA")
                self.argument()

        self.eat("RPAREN")  # )
        self.eat("NEWLINE")


    def argument(self): # all arguments 
        if self.current_token().type == "NUMBER":
            self.eat("NUMBER")
        elif self.current_token().type == "FLOAT":
            self.eat("FLOAT")
        elif self.current_token().type == "STRING":
            self.eat("STRING")
        elif self.current_token().type == "BOOLEAN":
            self.eat("BOOLEAN")
        elif self.current_token().type == "IDENTIFIER":
            self.eat("IDENTIFIER")
        else:
            error = Error(f"Unexpected argument type: {self.current_token().type}",self.current_token().line)
            raise SyntaxError(error)


    def expression(self):
        self.comparison_expression()

    def comparison_expression(self):
        self.arith_expression()
        while self.current_token().type in (
            "EQEQUAL", "NOTEQUAL", "LESS", "LESSEQUAL", "GREATER", "GREATEREQUAL"
        ):
            self.eat(self.current_token().type)
            self.arith_expression()
    
    def arith_expression(self):
        self.term()
        while self.current_token().type in ("PLUS", "MINUS"):
            self.eat(self.current_token().type)
            self.term()
    

    def term(self):
        self.factor()
        while self.current_token().type in ("MULTIPLY", "DIVIDE"):
            self.eat(self.current_token().type)
            self.factor()

    def list_literal(self):
        self.eat("LBRACKET")
        if self.current_token().type != "RBRACKET":  # if not empty list
            self.expression()
            while self.current_token().type == "COMMA":
                self.eat("COMMA")
                self.expression()
        self.eat("RBRACKET")

    def factor(self):
        token = self.current_token()
        if token.type == "NUMBER":
            self.eat("NUMBER")
        elif token.type == "FLOAT":
            self.eat("FLOAT")
        elif token.type == "STRING":
            self.eat("STRING")
        elif token.type == "BOOLEAN":  
            self.eat("BOOLEAN")
        elif token.type == "IDENTIFIER":
            self.eat("IDENTIFIER")
        elif token.type == "LPAREN":
            self.eat("LPAREN")
            self.expression()  
            self.eat("RPAREN")
        elif token.type == "LBRACKET":
            self.list_literal()
        else:
            error = Error(f"Invalid factor: {token.type}",token.line)
            raise SyntaxError(error)



