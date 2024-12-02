from lark import Lark, Transformer, Tree, Token
import sys

# Gramática de CMPL
cmpl_grammar = r"""

start: main_function statement*

statement: function_definition
         | conditional
         | loop
         | print_statement 
         | return_statement
         | expression ";"
         | function_call ";"

main_function: "function" "main" "(" ")" "{" statement* return_statement "}"

function_definition: "function" NAME "(" param_list ")" "{" statement* return_statement "}"

param_list: (NAME ("," NAME)*)?

function_call: NAME "(" arg_list ")"
arg_list: (expression ("," expression)*)?

print_statement: "print" "(" (function_call | expression) ")" ";"

conditional: "if" "(" condition ")" "{" statement+ "}" 
           | "if" "(" condition ")" "{" statement+ "}" "else" "{" statement+ "}"

loop: "for" NAME "in" "range" "(" NUMBER "," NUMBER "," NUMBER ")" "{" statement+ "}"

return_statement: "return" expression ";"

expression: term (("+" | "-" | "%") term)*
          | condition

term: factor (("*" | "/" | "%") factor)*

factor: NUMBER
      | NAME
      | "(" expression ")"

condition: expression (("==" | "!=" | "<" | "<=" | ">" | ">=") expression)
         | "!" condition
         | condition ("and" | "or") condition

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
NUMBER: /\d+/

%import common.WS
%ignore WS
"""

def print_ast(node, indent=0):
    if isinstance(node, Tree):
        print("  " * indent + f"{node.data} (type: Tree)")
        for child in node.children:
            print_ast(child, indent + 1)
    elif isinstance(node, Token):
        print("  " * indent + f"{node.type}: {node.value} (type: Token)")
        
def translate_program(ast, out):
    """
    Traduce el árbol de sintaxis abstracta (AST) generado por la gramática
    y lo convierte en código ensamblador LLVM.
    """
    if ast.data == "start":
        for child in ast.children:
            translate_program(child, out)
    
    elif ast.data == "main_function":
        out.write("define dso_local i32 @main() {\n")
        for child in ast.children:
            translate_program(child, out)
        out.write("  ret i32 0\n}\n")
    
    elif ast.data == "function_definition":
        function_name = ast.children[0].value  
        params = ast.children[1] 
        out.write(f"define dso_local i32 @{function_name}(")
        if params.children:
            param_list = ", ".join(f"i32 %{param.value}" for param in params.children)
            out.write(param_list)
        out.write(") {\n")
        for child in ast.children[2:]:
            translate_program(child, out)
        out.write("}\n")
        
    elif ast.data == "function_call":
        function_name = ast.children[0].value
        args = ast.children[1]
        arg_list = ", ".join(f"i32 {translate_expression(arg, out)}" for arg in args.children)
        out.write(f"  call i32 @{function_name}({arg_list})\n")
    
    elif ast.data == "print_statement":
        value = translate_expression(ast.children[0], out)
        out.write(f"  call void @print(i32 {value})\n")
    
    elif ast.data == "return_statement":
        value = translate_expression(ast.children[0], out)
        out.write(f"  ret i32 {value}\n")
    
    elif ast.data == "expression":
        result = translate_expression(ast, out)
        out.write(f"  {result}\n")
    
    elif ast.data == "statement":  
        for child in ast.children:
            translate_program(child, out)

    elif ast.data == "conditional":
        condition = translate_expression(ast.children[0], out)
        out.write(f"  br i1 {condition}, label %if_true, label %if_false\n")
        out.write("if_true:\n")
        for stmt in ast.children[1].children:
            translate_program(stmt, out)
        out.write("  br label %if_end\n")
        out.write("if_false:\n")
        if len(ast.children) > 2: 
            for stmt in ast.children[2].children:
                translate_program(stmt, out)
        out.write("  br label %if_end\n")
        out.write("if_end:\n")

    elif ast.data == "loop":
        out.write("  ; Loop translation not fully implemented yet\n")
    else:
        print(f"Warning: No implementation for AST node {ast.data}")


def translate_program(ast, out):
    """
    Traduce el árbol de sintaxis abstracta (AST) generado por la gramática
    y lo convierte en código ensamblador LLVM.
    """
    if ast.data == "start":
        for child in ast.children:
            translate_program(child, out)
    
    elif ast.data == "main_function":
        out.write("define dso_local i32 @main() {\n")
        for child in ast.children:
            translate_program(child, out)
        out.write("  ret i32 0\n") 
        out.write("}\n")
    
    elif ast.data == "function_definition":
        function_name = ast.children[0].value  
        params = ast.children[1]  
        out.write(f"define dso_local i32 @{function_name}(")
        if params.children:
            param_list = ", ".join(f"i32 %{param.value}" for param in params.children)
            out.write(param_list)
        out.write(") {\n")
        for child in ast.children[2:]:
            translate_program(child, out)
        out.write("}\n")  
        
    elif ast.data == "return_statement":
        value = translate_expression(ast.children[0], out)
        out.write(f"  ret i32 {value}\n")
    
    elif ast.data == "statement":
        for child in ast.children:
            translate_program(child, out)
    
    elif ast.data == "expression":
        result = translate_expression(ast, out)
        out.write(f"  {result}\n")
    
    elif ast.data == "function_call":
        function_name = ast.children[0].value
        args = ast.children[1]
        arg_list = ", ".join(f"i32 {translate_expression(arg, out)}" for arg in args.children)
        out.write(f"  call i32 @{function_name}({arg_list})\n")
    
    elif ast.data == "conditional":
       
        condition = translate_expression(ast.children[0], out)
        out.write(f"  br i1 {condition}, label %if_true, label %if_false\n")
        out.write("if_true:\n")
        for stmt in ast.children[1].children:
            translate_program(stmt, out)
        out.write("  br label %if_end\n")
        out.write("if_false:\n")
        if len(ast.children) > 2:  
            for stmt in ast.children[2].children:
                translate_program(stmt, out)
        out.write("  br label %if_end\n")
        out.write("if_end:\n")
    
    else:
        print(f"Warning: No implementation for AST node {ast.data}")

def translate_expression(ast, out):
    """
    Traduce un nodo de tipo expresión o condición en el árbol de sintaxis abstracta.
    Devuelve el valor LLVM correspondiente.
    """
    if ast.data == "term":
        left = translate_expression(ast.children[0], out)
        if len(ast.children) > 1:
            operator = ast.children[1].value
            right = translate_expression(ast.children[2], out)
            return f"{left} {operator} {right}"
        return left

    elif ast.data == "factor":
        if ast.children[0].type == "NUMBER":
            return ast.children[0].value
        elif ast.children[0].type == "NAME":
            return f"%{ast.children[0].value}"

    elif ast.data == "expression":
        left = translate_expression(ast.children[0], out)  
        if len(ast.children) > 1:
            for i in range(1, len(ast.children), 2): 
                operator = ast.children[i].value
                right = translate_expression(ast.children[i + 1], out)
                left = f"{left} {operator} {right}"  
            return left
        return left

    raise NotImplementedError(f"No se puede traducir la expresión: {ast.data}")

parser = Lark(cmpl_grammar, start="start")

input_file = "program.src"
output_file = "program.ll"

try:
    with open(input_file, "r") as f:
        program = f.read()
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{input_file}'.")
    exit(1)


try:
    ast = parser.parse(program)
    print_ast(ast)
except Exception as e:
    print(f"Error al analizar el programa: {e}")
    exit(1)


try:
    with open(output_file, "w") as f:
        translate_program(ast, f)
    print(f"El archivo LLVM fue generado exitosamente en '{output_file}'.")
except Exception as e:
    print(f"Error al escribir el archivo LLVM: {e}")
