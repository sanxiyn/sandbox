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

def make_evaluate(tree, letters):
    def inner(tree, args):
        if isinstance(tree, str):
            result = 0
            for letter in tree:
                index = letters.index(letter)
                result = result * 10 + args[index]
            return result
        if isinstance(tree, tuple):
            op, left, right = tree
            a = inner(left, args)
            b = inner(right, args)
            if op == '=':
                result = a == b
            if op == '+':
                result = a + b
            if op == '-':
                result = a - b
            return result
    def evaluate(*args):
        return inner(tree, args)
    return evaluate

def solve(problem):
    tree = parser.parse(problem)
    letters = sorted(get_letters(tree))
    first_letters = get_first_letters(tree)
    evaluate = make_evaluate(tree, letters)
    cp = constraint.Problem()
    digits = range(10)
    first_digits = range(1, 10)
    for letter in letters:
        if letter in first_letters:
            cp.addVariable(letter, first_digits)
        else:
            cp.addVariable(letter, digits)
    cp.addConstraint(constraint.AllDifferentConstraint())
    cp.addConstraint(evaluate, letters)
    return cp.getSolutions()

def substitute(problem, solution):
    result = problem
    for letter in solution:
        result = result.replace(letter, str(solution[letter]))
    return result

while True:
    problem = raw_input('> ')
    if not problem:
        break
    solutions = solve(problem)
    for solution in solutions:
        print substitute(problem, solution)
