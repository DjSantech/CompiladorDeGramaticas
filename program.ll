; ModuleID = 'program'

target triple = "x86_64-pc-linux-gnu"


Tree(Token('RULE', 'statement'), ['define dso_local i32 @suma(i32 %a, i32 %b) {\nTree(Token(\'RULE\', \'statement\'), ["  ret i32 Tree(Token(\'RULE\', \'expression\'), [Tree(Token(\'RULE\', \'term\'), [Tree(Token(\'RULE\', \'factor\'), [Token(\'NAME\', \'a\')])]), Tree(Token(\'RULE\', \'term\'), [Tree(Token(\'RULE\', \'factor\'), [Token(\'NAME\', \'b\')])])])\\n"])  ret i32 0\n}\n'])
Tree(Token('RULE', 'statement'), ['\n  ; Loop i\n  br label %loop_start\n\nloop_start:\n  %0 = phi i32 [0, %entry], [%2, %loop_body]\n  %cond = icmp slt i32 %0, 10\n  br i1 %cond, label %loop_body, label %loop_end\n\nloop_body:\nTree(Token(\'RULE\', \'statement\'), ["  call void @print_int(i32 Tree(Token(\'RULE\', \'function_call\'), [Token(\'NAME\', \'suma\'), Tree(Token(\'RULE\', \'arg_list\'), [Tree(Token(\'RULE\', \'expression\'), [Tree(Token(\'RULE\', \'term\'), [Tree(Token(\'RULE\', \'factor\'), [Token(\'NAME\', \'i\')])])]), Tree(Token(\'RULE\', \'expression\'), [Tree(Token(\'RULE\', \'term\'), [Tree(Token(\'RULE\', \'factor\'), [Token(\'NAME\', \'i\')])]), Tree(Token(\'RULE\', \'term\'), [Tree(Token(\'RULE\', \'factor\'), [Token(\'NUMBER\', \'1\')])])])])]))\\n"])\n  %2 = add i32 %0, 1\n  br label %loop_start\n\nloop_end:\n'])