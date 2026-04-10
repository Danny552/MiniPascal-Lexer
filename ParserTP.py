import ply.yacc as yacc
from MainLex import tokens
import MainLex
import sys

#Ayudado por Gemini

# Zona de cabezal
def p_program(p):
    'program : PROGRAM ID SEMICOLON uses_clause declaration_sections compound_stmt DOT'
    pass

def p_uses_clause(p):
    '''uses_clause : USES id_list SEMICOLON
                   | empty'''
    pass

def p_id_list(p):
    '''id_list : ID
               | id_list COMMA ID'''
    pass

# Zona de declaraciones
def p_declaration_sections(p):
    '''declaration_sections : declaration_sections section
                            | empty'''
    pass

def p_section(p):
    '''section : const_section
               | type_section
               | var_section
               | procedure_declaration
               | function_declaration'''
    pass

def p_const_section(p):
    'const_section : CONST const_list'
    pass

def p_const_list(p):
    '''const_list : const_list ID EQUALS expression SEMICOLON
                  | ID EQUALS expression SEMICOLON'''
    pass

def p_type_section(p):
    '''type_section : TYPE type_list
                    | empty'''
    pass

def p_type_list(p):
    '''type_list : type_list ID EQUALS type_specifier SEMICOLON
                 | ID EQUALS type_specifier SEMICOLON'''
    pass

def p_var_section(p):
    'var_section : VAR var_list'
    pass

def p_var_list(p):
    '''var_list : var_list id_list COLON type_specifier SEMICOLON
                | id_list COLON type_specifier SEMICOLON'''
    pass

def p_type_specifier(p):
    '''type_specifier : ID
                      | STRING LBRACKET NUMBER RBRACKET
                      | NUMBER DOT DOT NUMBER'''
    pass

def p_procedure_declaration(p):
    'procedure_declaration : PROCEDURE ID LPAREN args RPAREN SEMICOLON compound_stmt SEMICOLON'
    pass

def p_function_declaration(p):
    'function_declaration : FUNCTION ID LPAREN args RPAREN COLON type_specifier SEMICOLON compound_stmt SEMICOLON'
    pass

# Sentencias
def p_compound_stmt(p):
    'compound_stmt : BEGIN statement_list END'
    pass

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    pass

def p_if_stmt(p):
    '''if_stmt : IF LPAREN expression RPAREN THEN statement
               | IF LPAREN expression RPAREN THEN statement ELSE statement'''
    pass

def p_for_stmt(p):
    'for_stmt : FOR ID ASSIGN expression TO expression DO statement'
    pass

def p_statement(p):
    '''statement : call_stmt SEMICOLON
                 | assignment_stmt SEMICOLON
                 | compound_stmt
                 | if_stmt
                 | for_stmt
                 | empty'''
    pass

def p_call_stmt(p):
    '''call_stmt : ID LPAREN args RPAREN
                 | ID'''
    pass

def p_args(p):
    '''args : expression_list
            | empty'''
    pass

def p_expression_list(p):
    '''expression_list : expression_list COMMA expression
                       | expression'''
    pass

def p_assignment_stmt(p):
    'assignment_stmt : ID ASSIGN expression'
    pass

# Expresiones en general

def p_expression_formatted(p):
    '''expression_formatted : expression COLON type_specifier'''
    pass

def p_expression(p):
    '''expression : term
                  | expression PLUS term
                  | expression MINUS term
                  | expression GREATER term
                  | expression LESS term
                  | expression GREATEREQUAL term
                  | expression LESSEQUAL term
                  | expression NOTEQUAL term
                  | expression_formatted'''
    pass

def p_factor(p):
    '''factor : NUMBER
              | STRING
              | call_stmt
              | LPAREN expression RPAREN'''

    pass

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    pass


def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        error_msg = f"ERROR SINTACTICO EN LA LINEA {p.lineno}: Token inesperado '{p.value}'"
    else:
        error_msg = "Error: Fin de archivo inesperado (EOF)"
    
    print(error_msg)
    raise SyntaxError(error_msg)

parser = yacc.yacc()

if __name__ == '__main__':
    if (len(sys.argv) > 1):
        fin = sys.argv[1]
    else:
        fin = 'Prueba.pas'

    with open(fin, 'r') as f:
            data = f.read()
    try:
        parser.parse(data, tracking=True)
        print("Todo reconocido correctamente")
    except SyntaxError:
        print("La validación falló debido a los errores anteriores.")
