from tkinter import scrolledtext
from tokenizer import Tokenizer
import tkinter as tk
from parser import Parser
from tkinter import scrolledtext, messagebox


class RealTimeIDE:
    TAG_COLORS = {
        "COMMENT": "slategray",   # random different colors for every token 
        "KEYWORD": "blue", 
        "FLOAT": "purple",              
        "IDENTIFIER": "darkgreen",  
        "NUMBER": "purple",         
        "STRING": "darkorange",     
        "BOOLEAN": "teal",                  
        "ERROR": "red",            
        "EQUALS": "brown",        
        "EQEQUAL": "brown",        
        "NOTEQUAL": "brown",       
        "LESSEQUAL": "brown",      
        "LESS": "brown",           
        "GREATEREQUAL": "brown",   
        "GREATER": "brown",       
        "PLUS": "darkred",        
        "MINUS": "darkred",        
        "MULTIPLY": "darkred",    
        "DIVIDE": "darkred",       
        "LPAREN": "gray",         
        "RPAREN": "gray",         
        "COLON": "gray",        
        "COMMA": "gray",             
        "LBRACKET": "red",
        "RBRACKET": "red"         
    }


    def __init__(self, root):
        self.root = root
        self.root.title("Real Time Tokenizer and Syntax Highlighter IDE")

        tk.Label(root, text="Enter your code:").pack()

        # frame 
        self.frame = tk.Frame(root)
        self.frame.pack()

        # line numbers modifications
        self.line_numbers = tk.Text(self.frame, width=4, padx=4, takefocus=0, border=0,
                                    background='lightgray', state='disabled', wrap='none')
        self.line_numbers.pack(side="left", fill="y")

        self.text = scrolledtext.ScrolledText(self.frame, width=80, height=20, undo=True)
        self.text.pack(side="right", fill="both", expand=True)

        # adding tags to all tokens
        for tag, color in self.TAG_COLORS.items(): # red background and white font color for error line
            if tag == "ERROR":
                self.text.tag_configure("ERROR", background="red", foreground="white")  
            elif color:
                self.text.tag_configure(tag, foreground=color)


        # modifying tab button 
        self.text.bind("<Tab>", self.insert_tab)

        # user input stage
        self.text.bind("<<Modified>>", self.on_text_change)
        self.text.bind("<KeyRelease>", self.update_line_numbers)
        self.text.bind("<MouseWheel>", self.update_line_numbers)
        self.text.bind("<Button-1>", self.update_line_numbers)

        self._after_id = None

        # parse button
        self.parse_button = tk.Button(root, text="Parse", command=self.parse_code)
        self.parse_button.pack(pady=5)

        self.update_line_numbers()


    # solution for tab indent bug 
    def insert_tab(self, event):
        self.text.insert("insert", " " * 4)
        return "break"  

    # the function works after every text change
    def on_text_change(self, event=None):
        if self._after_id:
            self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(10, self.highlight_tokens)
        self.update_line_numbers()
        self.text.edit_modified(False)

    # highlighting tokens by their tokens (tags)
    def highlight_tokens(self):
        code = self.text.get("1.0", "end-1c")
        tokenizer = Tokenizer()
        try:
            tokens = tokenizer.tokenize(code)
        except Exception as e:
            return

        for tag in self.TAG_COLORS:
            self.text.tag_remove(tag, "1.0", "end")

        lines = code.splitlines(keepends=True)
        line_start_indices = []
        total = 0
        for line in lines:
            line_start_indices.append(total)
            total += len(line)

        for token in tokens:
            if token.type in self.TAG_COLORS:
                line_idx = token.line - 1
                if line_idx >= len(line_start_indices):
                    continue
                line_text = lines[line_idx]
                rel_start = line_text.find(token.value)
                if rel_start == -1:
                    continue
                start = f"{token.line}.{rel_start}"
                end = f"{token.line}.{rel_start + len(token.value)}"
                self.text.tag_add(token.type, start, end)

        self._after_id = None


    def parse_code(self):
        # parsing event runs after the parse button is pressed
        code = self.text.get("1.0", "end-1c")
        tokenizer = Tokenizer()

        self.text.tag_remove("ERROR", "1.0", "end")  # clean processed errors

        try:
            tokens = tokenizer.tokenize(code)
            for token in tokens:
                print(token.type)
            parser = Parser(tokens)
            parser.parse()
            messagebox.showinfo("Parse", "Code parsing completed successfully") # success messagebox
        except Exception as e:
            err_obj = e.args[0]
            err_msg = err_obj.description

            err_line = err_obj.error_line
            
            print(f"Parse error:", err_msg)
            if err_line != -1:
                self.text.tag_add("ERROR", f"{err_line}.0", f"{err_line}.end")
                self.text.see(f"{err_line}.0")  # focus error line

            messagebox.showerror(f"Line {err_line} - Parse error", err_msg) # error messagebox


    def update_line_numbers(self, event=None):
        # add line numbers after new line interaction
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')

        num_lines = int(self.text.index('end-1c').split('.')[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, num_lines + 1))

        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')




if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimeIDE(root)
    root.mainloop()
