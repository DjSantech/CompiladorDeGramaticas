Tree(Token('RULE', 'statement'), ['define dso_local i32 @constant(x) {\n    ret i32 x\n}'])
Tree(Token('RULE', 'statement'), ['  call i32 @constant(42)'])