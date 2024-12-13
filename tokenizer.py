# Token types
TOKEN_TYPES = [
    'LPAREN',       # (
    'RPAREN',       # )
    'EQUAL',       # =
    'SEMICOLON',    # ;
    'VAR',          # var
    'SHOW',         # show
    'SHOW_ONES',    # show_ones
    'NOT',          # not
    'AND',          # and
    'OR',           # or
    'TRUE',         # True
    'FALSE',        # False
    'ID',           # Identifiers
    'EOF',          # End of file/input
]

# Reserved keywords
RESERVED_KEYWORDS = {
    'var': 'VAR',
    'show': 'SHOW',
    'show_ones': 'SHOW_ONES',
    'not': 'NOT',
    'and': 'AND',
    'or': 'OR',
    'True': 'TRUE',
    'False': 'FALSE',
}

class Token:
    def __init__(self, type_, value=None, line=1, column=1):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.text else None

    def error(self, message):
        raise Exception(f"Error at line {self.line}, column {self.column}: {message}")

    def advance(self):
        # Move to the next character
        self.pos += 1
        
        if self.pos >= len(self.text):
            self.current_char = None  
        else:
            self.current_char = self.text[self.pos]  
        

        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        else:
            self.column += 1  


    def get_next_token(self):
        while self.current_char is not None:
            # Skip comments
            if self.current_char == '#':
                while self.current_char is not None and self.current_char != '\n':
                    self.advance()
                continue  

            # Skip whitespace
            if self.current_char in ' \t\r\n':
                self.advance()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                start_column = self.column
                result = ''
                while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
                    result += self.current_char
                    self.advance()
                token_type = RESERVED_KEYWORDS.get(result, 'ID')
                return Token(token_type, result, self.line, start_column)
            
            token = self.match_single_char_token()
            if token:
                return token

        return Token('EOF', None, self.line, self.column)
    
    def match_single_char_token(self):
        single_char_tokens = {
            '(': 'LPAREN',
            ')': 'RPAREN',
            '=': 'EQUAL',
            ';': 'SEMICOLON'
        }

        if self.current_char in single_char_tokens:
            token_type = single_char_tokens[self.current_char]
            token = Token(token_type, self.current_char, self.line, self.column)
            self.advance()
            return token
        
        return None