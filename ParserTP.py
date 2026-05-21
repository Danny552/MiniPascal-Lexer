import ply.yacc as yacc
from MainLex import tokens
import sys

# Colaborado con Gemini
error_stats = {
    'sintactico': 0,
    'semantico': 0
}

scopes = [{}] 

def enter_scope():
    scopes.append({})
    print("DEBUG: Se entra a un nuevo scope")


def declare_symbol(name, symbol_type, value=None):
    current_scope = scopes[-1]
    if name in current_scope:
        print(f"Error semantico: '{name}' ya declarado.")
        error_stats['semantico'] += 1
    else:
        current_scope[name] = {
            'nombre': name,
            'tipo': symbol_type,
            'atributo': [value] if value is not None else [] 
        }

def lookup_symbol(name):
    for scope in reversed(scopes):
        if name in scope:
            return scope[name]
    return None

def get_symbol_info(name):
    for scope in reversed(scopes):
        if name in scope:
            return scope[name]
    return None

def update_symbol_value(name, value):
    for scope in reversed(scopes):
        if name in scope:
            if isinstance(scope[name]['atributo'], list):
                if not scope[name]['atributo'] or scope[name]['atributo'][-1] != value:
                    scope[name]['atributo'].append(value)
            break
def evaluate_expression(expr):
    if isinstance(expr, (int, float)):
        return expr

    if isinstance(expr, str):
        sym = get_symbol_info(expr)
        if sym and sym.get('atributo') is not None:
            return sym['atributo']
        try:
            return float(expr)
        except Exception:
            return None

    if isinstance(expr, tuple) and len(expr) == 3:
        left, op, right = expr
        lval = evaluate_expression(left)
        rval = evaluate_expression(right)
        if lval is None or rval is None:
            return None
        try:
            if op == '+': return lval + rval
            if op == '-': return lval - rval
            if op == '*': return lval * rval
            if op == '/': return lval / rval if rval != 0 else None
        except Exception:
            return None
    return None

def print_symbol_table():
    print(f"{'NOMBRE':<15} {'TIPO':<30} {'HISTORIAL DE VALORES':<30}")
    for scope in scopes:
        for name, info in scope.items():
            attr = info['atributo']
            attr_str = ", ".join(map(str, attr)) if isinstance(attr, list) else str(attr)
            if isinstance(attr, list):
                for val in attr_str.split(', '):
                    print(f"{info['nombre']:<15} {info['tipo']:<30} {val:<30}")
            else:
                print(f"{info['nombre']:<15} {info['tipo']:<30} {attr_str:<30}")

def print_error_report():
    print("RESUMEN DE ERRORES")
    print(f"Errores Sintácticos: {error_stats['sintactico']}")
    print(f"Errores Semánticos:  {error_stats['semantico']}")
    print(f"Total de Errores:    {sum(error_stats.values())}")

def p_program(p):
    'program : PROGRAM ID SEMICOLON uses_clause declaration_sections compound_stmt DOT'
    print("\n--- ANÁLISIS SEMANTICO COMPLETO ---")
    print_symbol_table()
    print_error_report()

def p_uses_clause(p):
    '''uses_clause : USES id_list SEMICOLON
                   | empty'''
    pass

def p_id_list(p):
    '''id_list : ID
               | id_list COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

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
    'type_section : TYPE type_list'
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
    if len(p) == 6:
        ids, data_type = p[2], p[4]
    else:
        ids, data_type = p[1], p[3]
    for name in ids:
        declare_symbol(name, data_type)

def p_type_specifier(p):
    '''type_specifier : type_base
                      | ARRAY LBRACKET range RBRACKET OF type_base
                      | STRING LBRACKET NUMBER RBRACKET'''
    
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 7:
        p[0] = f"array of {p[6]}"
    else:
        p[0] = "string"

def p_type_base(p):
    '''type_base : INTEGER
                 | REAL
                 | CHAR
                 | BOOLEAN'''
    p[0] = p[1]

def p_range(p):
    '''range : NUMBER DOT DOT NUMBER'''
    p[0] = (p[1], p[4])

def p_procedure_declaration(p):
    'procedure_declaration : PROCEDURE ID LPAREN args RPAREN SEMICOLON compound_stmt SEMICOLON'
    declare_symbol(p[2], 'procedure')


def p_function_declaration(p):
    'function_declaration : FUNCTION ID LPAREN args RPAREN COLON type_base SEMICOLON compound_stmt SEMICOLON'
    declare_symbol(p[2], f"function returning {p[7]}")

def p_compound_stmt(p):
    'compound_stmt : BEGIN statement_list END'
    pass

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement
                      | empty''' 
    pass

def p_statement(p):
    '''statement : call_stmt SEMICOLON
                 | assignment_stmt SEMICOLON
                 | compound_stmt
                 | if_stmt
                 | for_stmt'''
    pass

def p_if_stmt(p):
    '''if_stmt : IF LPAREN expression RPAREN THEN statement
               | IF LPAREN expression RPAREN THEN statement ELSE statement'''
    pass

def p_for_stmt(p):
    'for_stmt : FOR ID ASSIGN expression TO expression DO statement'
    
    var_name = p[2]
    inicio = evaluate_expression(p[4])
    fin = evaluate_expression(p[6])
    
    if lookup_symbol(var_name) is None:
        print(f"Error semántico: Variable de control '{var_name}' no declarada.")
        error_stats['semantico'] += 1
    else:
        
        if inicio is not None and fin is not None:
            for i in range(inicio, fin + 1):
                update_symbol_value(var_name, i)
                print(f"DEBUG: Bucle FOR para '{var_name}', valor actual: {i}")

def p_assignment_stmt(p):
    'assignment_stmt : ID ASSIGN expression'
    if lookup_symbol(p[1]) is None:
        print(f"Error semántico: Variable '{p[1]}' usada antes de su declaración.")
        error_stats['semantico'] += 1 
    else:
        val = evaluate_expression(p[3])
        if val is not None:
            update_symbol_value(p[1], val)
            print(f"DEBUG: Asignado {val} a {p[1]}")

def p_call_stmt(p):
    '''call_stmt : ID LPAREN expression_list RPAREN
                 | ID'''
    name = p[1]
    if lookup_symbol(name) is None:
        if name.lower() not in ['write', 'writeln', 'readln']:
            print(f"Error semántico: Función o procedimiento '{name}' no definido.")
            error_stats['semantico'] += 1
    p[0] = name
    
def p_args(p):
    '''args : arg_list
            | empty'''
    p[0] = p[1]

def p_arg_list(p):
    '''arg_list : ID COLON type_base
                | arg_list SEMICOLON ID COLON type_base'''
    if len(scopes) == 1: 
        enter_scope() 
        
    if len(p) == 4:
        declare_symbol(p[1], p[3])
    else:
        declare_symbol(p[3], p[5])

def p_expression_list(p):
    '''expression_list : expression_list COMMA expression
                       | expression'''
    pass

def p_expression(p):
    '''expression : term
                  | expression PLUS term
                  | expression MINUS term
                  | expression GREATER term
                  | expression LESS term
                  | expression GREATEREQUAL term
                  | expression LESSEQUAL term
                  | expression NOTEQUAL term'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = (p[1], p[2], p[3])

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = (p[1], p[2], p[3])

def p_factor(p):
    '''factor : NUMBER
              | STRING
              | call_stmt
              | LPAREN expression RPAREN'''
    if len(p) == 2:
            if isinstance(p[1], str) and p[1].replace('.','',1).isdigit():
                p[0] = float(p[1]) if '.' in p[1] else int(p[1])
            else:
                p[0] = p[1]
    else: p[0] = p[2]

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    error_stats['sintactico'] += 1
    if p:
        print(f"Error de sintaxis en la línea {p.lineno}: Token inesperado '{p.value}'")
    else:
        print("Error: Fin de archivo inesperado")

parser = yacc.yacc(start='program')

if __name__ == '__main__':
    fin = sys.argv[1] if len(sys.argv) > 1 else 'Prueba.pas'
    with open(fin, 'r') as f:
        data = f.read()
    try:
        parser.parse(data, tracking=True)
    except Exception as e:
        print(f"Error de ejecución: {e}")