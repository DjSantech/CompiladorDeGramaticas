from lark import Lark, Transformer, Tree

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

function_definition: "function" NAME "(" param_list ")" "{" statement+ "}"
param_list: (NAME ("," NAME)*)?

function_call: NAME "(" arg_list ")"
arg_list: (expression ("," expression)*)?

print_statement: "print" "(" (function_call | expression) ")" ";"

conditional: "if" "(" condition ")" "{" statement+ "}" 
           | "if" "(" condition ")" "{" statement+ "}" "else" "{" statement+ "}"

loop: "for" NAME "in" "range" "(" NUMBER "," NUMBER "," NUMBER ")" "{" statement+ "}"

return_statement: "return" expression ";"

expression: term (("+" | "-" | "%") term)*

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

# Programa de ejemplo
program = """
function suma(a, b) {
    return a + b;
}

for i in range(0, 10, 1) {
    print(suma(i, i+1));  
}
"""

# Imprimir el árbol
tree = parser.parse(program)
print("Árbol de sintaxis generado:")
print(tree.pretty())

class CMPLTransformer(Transformer):
    def __init__(self):
        self.output = []
    
    def start(self, items):
        self.output.append("; ModuleID = 'program'\n")
        self.output.append("target triple = \"x86_64-pc-linux-gnu\"\n\n")
        
        # Convierte cada item en un string antes de agregarlo a la salida
        for item in items:
            self.output.append(str(item))  # Convertir cada elemento a cadena

        return "\n".join(self.output)
    
    def function_definition(self, items):
        function_name = str(items[0])  # Nombre de la función
        params = items[1]  # Parámetros
        body = "".join([str(item) for item in items[2:]])  # Extrae el texto de los statements
        
        # Construye la lista de parámetros como un string
        param_list = ", ".join([f"i32 %{param}" for param in params.children])
        return f"define dso_local i32 @{function_name}({param_list}) {{\n{body}  ret i32 0\n}}\n"
    
    def return_statement(self, items):
        return f"  ret i32 {items[0]}\n"
    
    def loop(self, items):
        loop_var = items[0]
        start = items[1]
        end = items[2]
        step = items[3]
        body = "".join([str(item) for item in items[4:]])  # Extrae el texto de los statements
        return f"""
  ; Loop {loop_var}
  br label %loop_start

loop_start:
  %0 = phi i32 [{start}, %entry], [%2, %loop_body]
  %cond = icmp slt i32 %0, {end}
  br i1 %cond, label %loop_body, label %loop_end

loop_body:
{body}
  %2 = add i32 %0, {step}
  br label %loop_start

loop_end:
"""

    def print_statement(self, items):
        return f"  call void @print_int(i32 {items[0]})\n"



# Generar el código LLVM
transformer = CMPLTransformer()
llvm_code = transformer.transform(tree)

# Guardar el archivo program.ll
with open("program.ll", "w") as llvm_file:
    llvm_file.write(llvm_code)

# Mostrar el código generado
print("Código LLVM generado:")
print(llvm_code)
