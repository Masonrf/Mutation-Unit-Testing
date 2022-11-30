# Mutation-Unit-Testing
## A tool to test the effectiveness of unit tests by injecting mutations into Python source code

This tool turns Python source code into a parse tree, mutates an operator, generates the mutated version of the source code, runs the unit test on the mutated code, and then records if the unit test detected the mutation.

This process is repeated by mutating many operators with the results of each iteration being recorded.

This program outputs how many times the unit test failed to detect the source code mutations.

Current possible mutations consist of replacement of python boolean, binary, comparison, and unary operators.

## Installation
Clone this repo and install dependencies using
```
python3 -m pip install -r requirements.txt
```

## Usage
Create a script to run the mutation. See [the example](example/mutate-example.py) for more information.

It is highly recommended to save and back up your repository before running this program.

Results will be logged to the mutation-unit-test/ directory


## Mutation() class initialization parameters
### moduleNameToTest (str)
The file path of the module(s) to mutate and test. This can be a directory of .py files or a single .py file

### unitTestFileName (str)
The file path of the pytest test files. This can be a directory of .py files or single .py file

### verbose (bool; default: False)
Print out extra information to the terminal


## mutate() method parameters
### mutation_type (Mutation.mutation_types)
mutation_types.COMPLEMENT (Mutate an operator to its complement. I.e. "+" to "-", "*" to "/", etc)
mutation_types.RANDOM (Replace an operator with another random operator. Note: some random mutations may cause errors)

### iterations (int; must be > 0)
How many times to perform a set of mutations on and rerun the tests. Because random operators are chosen from the source to mutate on each run, you can choose to run the tests multiple times.

### numMutations (int; must be > 0)
How many operators should be mutated in each iteration.
If multiple modules are present, each module is mutated numMutation times.
If numMutations is greater than the number of mutatable operators, every operator will be mutated

### printSrcAfterMutate (bool; default: False)
Option to unparse the mutated AST into python source code and print it to the terminal

### removeBackup (bool; default: True)
Option to remove the backup of the original source after mutation is complete

## Other methods
### printSrc()
Print out the python source code loaded into the mutation object

### printTree()
Print out the python source code as an AST

## Attributes
### mutation_operators (dict; requires a specific structure)
The list of possible operators to use is based on the mutation_operators dictionary. This dictionary can be redefined in your program by following the structure given below. All possible operator types are given in this example
```
mutation_operators = {
    "unaryOps": [ast.UAdd, ast.USub, ast.Not, ast.Invert],
    "binOps": [ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult],
    "boolOps": [ast.And, ast.Or],
    "cmpOps": [ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn]
}
```
## Useful References
[Python Abstract Syntax Tree library](https://docs.python.org/3/library/ast.html)

[Better AST library guide](https://greentreesnakes.readthedocs.io/en/latest/)

[Into to ASTs in Python](https://pybit.es/articles/ast-intro/)
