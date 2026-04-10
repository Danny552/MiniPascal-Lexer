import ply.lex as lex
import sys
import json

with open ('Tokens.json', 'r') as Tokens:
    dict_tokens = json.load(Tokens)
tokens = [
    "PLUS", "MINUS", "TIMES", "DIVIDE",
    "LPAREN", "RPAREN", "EQUALS", "SEMICOLON", "COLON", "COMMA", "DOT",
    "LBRACKET", "RBRACKET", "SINGLE_COMMENT", "ASSIGN"
] + list(dict_tokens.values())

#Definición de tokens básicos, operadores y símbolos
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_ASSIGN = r':='
t_SEMICOLON = r';'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

#Tokens para números, strings, comentarios y identificadores

def t_INVALID_ID(t):
    r'[0-9]+[a-zA-Z_][a-zA-Z_0-9]*'
    print(f"Lexical Error: Invalid identifier '{t.value}' at line {t.lineno}.") 

def t_NUMBER(t):
	r'\$[0-9a-fA-F]+|\d+(\.\d+)?((E|e)(-)?\d+(\.\d+)?)?'
	return t
def t_STRING(t):
	r'\'([^\\\n]|(\\.))*?\''
	t.value = t.value[1:-1] 
	return t
def t_SINGLE_COMMENT(t):
	r'{.*?}'
	pass

#Captura todos los id y palabras reservadas, luego busca en el diccionario para comprobar su validez
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = dict_tokens.get(t.value.lower(), 'ID') 
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print ("Lexical error: " + str(t.value[0]))
    t.lexer.skip(1)
	
def test(lexer):
	while True:
		tok = lexer.token()
		if not tok:
			break
		print (tok)

lexer = lex.lex()

if __name__ == '__main__':
	if (len(sys.argv) > 1):
		fin = sys.argv[1]
	else:
		fin = 'Prueba.pas'
	f = open(fin, 'r')
	data = f.read()
	print (data)
	lexer.input(data)
	test(lexer)