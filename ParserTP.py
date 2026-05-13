import ply.yacc as yacc
from MainLex import tokens
import sys
import re

# --- SEMANTIC UTILITIES ---
scopes = [{}]  # Global scope is at index 0

class AnalysisState:
    current_pass = 1

def set_pass(pass_num):
    """Set the current analysis pass"""
    AnalysisState.current_pass = pass_num

def enter_scope():
    scopes.append({})
    print("DEBUG: Entered new scope.")

def exit_scope():
    if len(scopes) > 1:
        popped = scopes.pop()
        print(f"DEBUG: Exited scope. Symbols lost: {list(popped.keys())}")

def declare_symbol(name, symbol_type, value=None):
    """Declare a symbol with name, type, and optional value (attribute)"""
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
    """Look up a symbol in the scope chain"""
    for scope in reversed(scopes):
        if name in scope:
            if isinstance(scope[name], dict):
                return scope[name]['tipo']
            return scope[name]
    return None

def get_symbol_info(name):
    """Get full symbol info (nombre, tipo, atributo)"""
    for scope in reversed(scopes):
        if name in scope:
            if isinstance(scope[name], dict):
                return scope[name]
            return {'nombre': name, 'tipo': scope[name], 'atributo': None}
    return None

def update_symbol_value(name, value):
    """Update a symbol's attribute (value)"""
    for scope in reversed(scopes):
        if name in scope:
            if isinstance(scope[name], dict):
                scope[name]['atributo'] = value
            break

def evaluate_expression(expr):
    """
    Evaluate an expression and return its numeric value.
    expr can be: NUMBER, ID, or a tuple (left, operator, right)
    """
    if isinstance(expr, (int, float)):
        return expr
    
    if isinstance(expr, str):
        # It's a variable name
        sym_info = get_symbol_info(expr)
        if sym_info and sym_info['atributo'] is not None:
            return sym_info['atributo']
        return 0
    
    if isinstance(expr, tuple) and len(expr) == 3:
        left, op, right = expr
        left_val = evaluate_expression(left)
        right_val = evaluate_expression(right)
        
        if op == '+':
            return left_val + right_val
        elif op == '-':
            return left_val - right_val
        elif op == '*':
            return left_val * right_val
        elif op == '/':
            return left_val / right_val if right_val != 0 else 0
    
    return 0

def print_symbol_table():
    """Print the symbol table in a formatted table"""
    print("\n" + "="*60)
    print("TABLA DE SÍMBOLOS")
    print("="*60)
    print(f"{'NOMBRE':<20} {'TIPO':<15} {'ATRIBUTO':<15}")
    print("-"*60)
    
    for scope in scopes:
        for name, info in scope.items():
            if isinstance(info, dict):
                attr_val = info['atributo'] if info['atributo'] is not None else "---"
                print(f"{info['nombre']:<20} {info['tipo']:<15} {str(attr_val):<15}")
    
    print("="*60)


# --- GRAMMAR RULES ---

# The first rule is automatically the start symbol, 
# but we define it explicitly in yacc.yacc() at the bottom to be safe.
def p_program(p):
    'program : PROGRAM ID SEMICOLON uses_clause declaration_sections compound_stmt DOT'
    # In pass 1: declarations are already processed
    # In pass 2: show final results
    if AnalysisState.current_pass == 2:
        print("\n--- SEMANTIC ANALYSIS PASS 2 COMPLETE ---")
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
    if AnalysisState.current_pass == 1:
        # First pass: declare variables
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
    if AnalysisState.current_pass == 1:
        # First pass: register the procedure in global scope for recursion
        scopes[0][p[2]] = {
            'nombre': p[2],
            'tipo': 'procedure',
            'atributo': None
        }
        print(f"DEBUG [PASS 1]: Registered procedure '{p[2]}'")
        if len(scopes) > 1:
            exit_scope()
    else:
        # Second pass: procedure validate
        print(f"DEBUG [PASS 2]: Validating procedure '{p[2]}'")
        if len(scopes) > 1:
            exit_scope()

def p_function_declaration(p):
    'function_declaration : FUNCTION ID LPAREN args RPAREN COLON type_specifier SEMICOLON compound_stmt SEMICOLON'
    if AnalysisState.current_pass == 1:
        # First pass: register the function in global scope for recursion
        scopes[0][p[2]] = {
            'nombre': p[2],
            'tipo': f'function returning {p[7]}',
            'atributo': None
        }
        print(f"DEBUG [PASS 1]: Registered function '{p[2]}'")
        if len(scopes) > 1:
            exit_scope()
    else:
        # Second pass: function validate
        print(f"DEBUG [PASS 2]: Validating function '{p[2]}'")
        if len(scopes) > 1:
            exit_scope()

# Statements
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
    if lookup_symbol(p[2]) is None:
        print(f"SEMANTIC ERROR: Loop variable '{p[2]}' not declared.")

def p_assignment_stmt(p):
    'assignment_stmt : ID ASSIGN expression'
    if lookup_symbol(p[1]) is None:
        print(f"SEMANTIC ERROR: Variable '{p[1]}' used before declaration.")
    elif AnalysisState.current_pass == 2:
        # Second pass: evaluate the expression and update the symbol's value
        value = evaluate_expression(p[3])
        update_symbol_value(p[1], value)
        print(f"DEBUG [PASS 2]: Assigned value {value} to '{p[1]}'")

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
        # Build a tuple (left, operator, right) for evaluation
        p[0] = (p[1], p[2], p[3])

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        # Build a tuple (left, operator, right) for evaluation
        p[0] = (p[1], p[2], p[3])

def p_factor(p):
    '''factor : NUMBER
              | STRING
              | call_stmt
              | LPAREN expression RPAREN'''
    if len(p) == 2:
        if isinstance(p[1], str):
            # It's either a STRING or a call_stmt (ID)
            try:
                # Try to parse as number (for NUMBER tokens that come as strings)
                p[0] = float(p[1])
            except (ValueError, TypeError):
                # It's a variable name or string
                p[0] = p[1]
        else:
            p[0] = p[1]
    else:
        # LPAREN expression RPAREN
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
        # PASS 1: Collect declarations
        print("="*60)
        print("SEMANTIC ANALYSIS - PASS 1: Collecting Declarations")
        print("="*60)
        set_pass(1)
        parser.parse(data, tracking=True)
        
        # Reset scopes for pass 2 to only keep global declarations
        # Keep only the global scope declarations from pass 1
        global_syms = scopes[0].copy()
        scopes.clear()
        scopes.append(global_syms)
        
        # PASS 2: Full semantic analysis
        print("\n" + "="*60)
        print("SEMANTIC ANALYSIS - PASS 2: Full Analysis")
        print("="*60)
        set_pass(2)
        parser.parse(data, tracking=True)
        
    except Exception as e:
        print(f"Execution Error: {e}")