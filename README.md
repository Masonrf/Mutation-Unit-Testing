# Mutation-Unit-Testing
## A tool to test the effectiveness of unit tests by injecting mutations into Python source code

This tool turns Python source code into a parse tree, mutates an operator, generates the mutated version of the source code, runs the unit test on the mutated code, and then records if the unit test detected the mutation.

This process is repeated by mutating many operators with the results of each iteration being recorded.

This program outputs how many times the unit test failed to detect the source code mutations.

Mutations consist of arithmetic, assignment, conditional, and relational operator replacements.

## Useful References
[Python Abstract Syntax Tree library](https://docs.python.org/3/library/ast.html)

[Better AST library guide](https://greentreesnakes.readthedocs.io/en/latest/)
