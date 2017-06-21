'''
$ python cryptarithmetic.py
> SEND + MORE = MONEY
9567 + 1085 = 10652
> APPLE + LEMON = BANANA
67794 + 94832 = 162626
>
'''

import constraint
import parsimonious

grammar = '''
problem = expression equals expression
equals = "=" _
expression = variable op_variable*
op_variable = op _ variable
op = "+" / "-"
variable = ~"[A-Z]+" _
_ = ~r"\s*"
'''

class Parser(parsimonious.NodeVisitor):
    def __init__(self):
        self.grammar = parsimonious.Grammar(grammar)
    def visit_problem(self, node, children):
        left, _, right = children
        return '=', left, right
    def visit_expression(self, node, children):
        result, op_variables = children
        for op, variable in op_variables:
            result = op, result, variable
        return result
    def visit_op_variable(self, node, children):
        op, _, variable = children
        return op, variable
    def visit_op(self, node, children):
        return children[0].text
    def visit_variable(self, node, children):
        return children[0].text
    def generic_visit(self, node, children):
        return children or node

parser = Parser()

def get_letters(tree):
    def inner(tree, result):
        if isinstance(tree, str):
            for letter in tree:
                result.add(letter)
        if isinstance(tree, tuple):
            op, left, right = tree
            inner(left, result)
            inner(right, result)
    result = set()
    inner(tree, result)
    return result

def get_first_letters(tree):
    def inner(tree, result):
        if isinstance(tree, str):
            result.add(tree[0])
        if isinstance(tree, tuple):
            op, left, right = tree
            inner(left, result)
            inner(right, result)
    result = set()
    inner(tree, result)
    return result

def make_formula(tree, symbols):
    def inner(tree):
        if isinstance(tree, str):
            result = 0
            for letter in tree:
                symbol = symbols[letter]
                result = result * 10 + symbol
            return result
        if isinstance(tree, tuple):
            op, left, right = tree
            a = inner(left)
            b = inner(right)
            if op == '=':
                result = a.Equals(b)
            if op == '+':
                result = a + b
            if op == '-':
                result = a - b
            return result
    return inner(tree)

def solve(problem):
    from pysmt.shortcuts import AllDifferent, And, Symbol, get_model
    from pysmt.typing import INT
    tree = parser.parse(problem)
    letters = sorted(get_letters(tree))
    first_letters = get_first_letters(tree)
    symbols = {}
    for letter in letters:
        symbol = Symbol(letter, INT)
        symbols[letter] = symbol
    formula = make_formula(tree, symbols)
    clauses = []
    for letter in letters:
        symbol = symbols[letter]
        if letter in first_letters:
            clauses.append(1 <= symbol)
            clauses.append(symbol < 10)
        else:
            clauses.append(0 <= symbol)
            clauses.append(symbol < 10)
    clauses.append(AllDifferent(*symbols.values()))
    clauses.append(formula)
    cp = And(clauses)
    return get_model(cp)

def substitute(problem, solution):
    result = problem
    for symbol, constant in solution:
        name = symbol.symbol_name()
        value = constant.constant_value()
        result = result.replace(name, str(value))
    return result

while True:
    problem = raw_input('> ')
    if not problem:
        break
    solution = solve(problem)
    print substitute(problem, solution)
