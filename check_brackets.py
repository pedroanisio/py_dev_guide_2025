def check_parentheses_balance(filename):
    stack = []
    line_numbers = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        for j, char in enumerate(line):
            if char in '([{':
                stack.append((char, i, j))
            elif char in ')]}':
                if not stack:
                    print(f"Extra closing bracket '{char}' at line {i}, column {j}")
                    return False
                
                opening, open_line, open_col = stack.pop()
                if (opening == '(' and char != ')') or \
                   (opening == '[' and char != ']') or \
                   (opening == '{' and char != '}'):
                    print(f"Mismatched brackets: '{opening}' at line {open_line}, column {open_col} and '{char}' at line {i}, column {j}")
                    return False
    
    if stack:
        print("Unclosed brackets:")
        for char, line, col in stack:
            print(f"  '{char}' at line {line}, column {col}")
        return False
    
    print("Brackets are balanced")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "guide/validation.py"
    
    check_parentheses_balance(filename) 