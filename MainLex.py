import ply.lex as lex
import sys
import json

with open ('Tokens.json', 'r') as Tokens:
    tokens = json.load(Tokens)



def t_PROGRAM(t):
	r'program'
	return t

def t_ARRAY(t):
	r'array'
	return t

def t_BEGIN(t):
	r'begin'
	return t

def t_CASE(t):
	r'case'
	return t

def t_CONST(t):
	r'array'
	return t

def t_NUMBER(t):
    r'(-)?\d+(\.\d+)'
    return t

def t_ID(t):
    r'\w+(\d\w)*' 
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print ("Lexical error: " + str(t.value[0]))
    t.lexer.skip(1)
	
def test(data, lexer):
	lexer.input(data)
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
	test(data, lexer)