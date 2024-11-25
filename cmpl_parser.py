from lark import Lark, Transformer, Tree
import sys

# Gramática de CMPL
cmpl_grammar = """
start: statement+

statement: function_definition
         | conditional
         | loop
         | print_statement 
         | return_statement
         | expression ";"
         | function_call ";"

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

# Parser para CMPL
parser = Lark(cmpl_grammar, start="start")

# Verificar si se pasó el nombre de archivo como argumento
if len(sys.argv) != 2:
    print("Uso: python cmpl_parser.py <archivo_de_entrada>")
    sys.exit(1)

input_file = sys.argv[1]

# Leer el archivo de entrada
try:
    with open(input_file, "r") as f:
        program = f.read()
except FileNotFoundError:
    print(f"Error: El archivo '{input_file}' no existe.")
    sys.exit(1)

# Imprimir el árbol de sintaxis generado
tree = parser.parse(program)
print("Árbol de sintaxis generado:")
print(tree.pretty())

class CMPLTransformer(Transformer):
    def __init__(self):
        self.output = []
        self.temp_counter = 0  # Contador para variables temporales

    def get_temp(self):
        temp = f"%t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def start(self, items):
        # Asegurarnos de que todo en items se convierta a cadenas
        for item in items:
            self.output.append(str(item))  # Convertir item a string aquí
        return "\n".join(self.output)

    def function_definition(self, items):
        function_name = str(items[0])  # Función (como @constant)
        param_list = ', '.join([str(param) for param in items[1]])  # Parámetros
        body = str(items[2])  # Cuerpo de la función
        return f"define dso_local i32 @{function_name}({param_list}) {{\n  {body}\n}}"

    def return_statement(self, items):
        value = str(items[0])  # Valor de retorno
        return f"  ret i32 {value}"

    def function_call(self, items):
        function_name = str(items[0])  # Función (como @constant)
        
        # Aquí procesamos los argumentos de forma similar
        args = ", ".join([str(arg) for arg in items[1]])  # Argumentos
        return f"  call i32 @{function_name}({args})"

    def expression(self, items):
        if len(items) == 1:  # Caso de expresión simple
            return str(items[0])
        else:
            left = str(items[0])
            operator = str(items[1])
            right = str(items[2])

            # Operadores mapeados a LLVM
            llvm_op = {"+" : "add", "-" : "sub", "*" : "mul", "/" : "sdiv"}[operator]
            temp = self.get_temp()
            self.output.append(f"  {temp} = {llvm_op} i32 {left}, {right}")
            return temp

    def NAME(self, token):
        return str(token)

    def NUMBER(self, token):
        return str(token)

    def param_list(self, items):
        return items

    def arg_list(self, items):
        return items

    def term(self, items):
        return str(items[0])  # Devolver el valor procesado

    def factor(self, items):
        return str(items[0])  # Devolver el valor procesado


# Generar el código LLVM
transformer = CMPLTransformer()
llvm_code = transformer.transform(tree)

# Guardar el archivo program.ll
with open("program.ll", "w") as llvm_file:
    llvm_file.write(llvm_code)

# Mostrar el código generado
print("Código LLVM generado:")
print(llvm_code)
