import ply.yacc as yacc
from MainLex import tokens
import sys

# --- SEMANTIC UTILITIES ---
scopes = [{}]  # Global scope is at index 0

def enter_scope():
    scopes.append({})
    print("DEBUG: Entered new scope.")

def exit_scope():
    if len(scopes) > 1:
        popped = scopes.pop()
        print(f"DEBUG: Exited scope. Symbols lost: {list(popped.keys())}")

def declare_symbol(name, symbol_type, value=None):
    """Declare a symbol storing name, type and optional attribute (value)."""
    current_scope = scopes[-1]
    if name in current_scope:
        print(f"SEMANTIC ERROR: '{name}' already declared in this scope.")
    else:
        current_scope[name] = {
            'nombre': name,
            'tipo': symbol_type,
            'atributo': value
        }
        print(f"DEBUG: Declared '{name}' as {symbol_type}")

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
            if isinstance(scope[name], dict):
                scope[name]['atributo'] = value
            break

def evaluate_expression(expr):
    """Evaluate a parsed expression structure and return numeric value if possible."""
    # Numbers as Python ints/floats
    if isinstance(expr, (int, float)):
        return expr

    # If expr is a string (identifier), return its atributo if available
    if isinstance(expr, str):
        sym = get_symbol_info(expr)
        if sym and sym.get('atributo') is not None:
            return sym['atributo']
        try:
            # Try convert numeric-like strings
            return float(expr)
        except Exception:
            return None

    # Tuple operator nodes: (left, op, right)
    if isinstance(expr, tuple) and len(expr) == 3:
        left, op, right = expr
        lval = evaluate_expression(left)
        rval = evaluate_expression(right)
        if lval is None or rval is None:
            return None
        try:
            if op == '+':
                return lval + rval
            if op == '-':
                return lval - rval
            if op == '*':
                return lval * rval
            if op == '/':
                return lval / rval if rval != 0 else None
        except Exception:
            return None

    return None

def print_symbol_table():
    print("\n" + "="*60)
    print("TABLA DE SÍMBOLOS")
    print("="*60)
    print(f"{'NOMBRE':<20} {'TIPO':<15} {'ATRIBUTO':<15}")
    print("-"*60)
    for scope in scopes:
        for name, info in scope.items():
            if isinstance(info, dict):
                attr = info['atributo'] if info['atributo'] is not None else '---'
                print(f"{info['nombre']:<20} {info['tipo']:<15} {str(attr):<15}")
    print("="*60)


# --- GRAMMAR RULES ---

# The first rule is automatically the start symbol, 
# but we define it explicitly in yacc.yacc() at the bottom to be safe.
def p_program(p):
    'program : PROGRAM ID SEMICOLON uses_clause declaration_sections compound_stmt DOT'
    print("\n--- SEMANTIC ANALYSIS COMPLETE ---")
    print_symbol_table()

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


# Sections (Removed '| empty' from here to prevent infinite recursion)
def p_const_section(p):
    'const_section : CONST const_list'
    pass

def p_const_list(p):
    '''const_list : const_list ID EQUALS expression SEMICOLON
                  | ID EQUALS expression SEMICOLON'''
    pass

def p_type_section(p):
    'type_section : TYPE type_list' # Fixed infinite loop here
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
    '''type_specifier : ID
                      | STRING LBRACKET NUMBER RBRACKET
                      | NUMBER DOT DOT NUMBER'''
    p[0] = p[1]

# Procedures and Functions
def p_procedure_declaration(p):
    'procedure_declaration : PROCEDURE ID LPAREN args RPAREN SEMICOLON compound_stmt SEMICOLON'
    # register procedure in global scope
    declare_symbol(p[2], 'procedure')
    exit_scope() # Exit the scope we created during args

def p_function_declaration(p):
    'function_declaration : FUNCTION ID LPAREN args RPAREN COLON type_specifier SEMICOLON compound_stmt SEMICOLON'
    # register function in global scope (attribute can hold return later)
    declare_symbol(p[2], f"function returning {p[7]}")
    exit_scope() # Exit the scope we created during args

# Statements
def p_compound_stmt(p):
    'compound_stmt : BEGIN statement_list END'
    pass

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement
                      | empty''' # Moved empty here to fix infinite loop
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
    if lookup_symbol(p[2]) is None:
        print(f"SEMANTIC ERROR: Loop variable '{p[2]}' not declared.")

def p_assignment_stmt(p):
    'assignment_stmt : ID ASSIGN expression'
    if lookup_symbol(p[1]) is None:
        print(f"SEMANTIC ERROR: Variable '{p[1]}' used before declaration.")
    else:
        val = evaluate_expression(p[3])
        if val is not None:
            update_symbol_value(p[1], val)
            print(f"DEBUG: Assigned {val} to {p[1]}")

def p_call_stmt(p):
    '''call_stmt : ID LPAREN expression_list RPAREN
                 | ID'''
    name = p[1]
    if lookup_symbol(name) is None:
        if name.lower() not in ['write', 'writeln', 'readln']:
            print(f"SEMANTIC ERROR: Function or procedure '{name}' not defined.")
    p[0] = name

# Arguments and Expressions
def p_args(p):
    '''args : arg_list
            | empty'''
    p[0] = p[1]

def p_arg_list(p):
    '''arg_list : ID COLON type_specifier
                | arg_list SEMICOLON ID COLON type_specifier'''
    # We force a scope entry here only if one doesn't exist yet for the function
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
        # Try to convert NUMBER token strings to numeric types
        try:
            if isinstance(p[1], str) and p.slice[1].type == 'NUMBER':
                if '.' in p[1] or 'e' in p[1].lower():
                    p[0] = float(p[1])
                else:
                    p[0] = int(p[1])
            else:
                p[0] = p[1]
        except Exception:
            p[0] = p[1]
    else:
        p[0] = p[2]

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"SYNTAX ERROR AT LINE {p.lineno}: Unexpected token '{p.value}'")
    else:
        print("Error: Unexpected end of file")

# --- MAIN BLOCK ---
# We explicitly define the start symbol so Yacc never gets confused again
parser = yacc.yacc(start='program')

if __name__ == '__main__':
    fin = sys.argv[1] if len(sys.argv) > 1 else 'Pruebabuen.pas'
    with open(fin, 'r') as f:
        data = f.read()
    try:
        parser.parse(data, tracking=True)
    except Exception as e:
        print(f"Execution Error: {e}")