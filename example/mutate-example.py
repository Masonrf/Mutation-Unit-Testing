import sys
sys.path.append('../')
from mutation import *



try:
    # Initialization
    m1 = Mutation("modulesToTest/", "testDir/", verbose=False)
    
    # Print out the source that was loaded
    m1.printSrc()
    
    # Print out the AST
    m1.printTree()

    # Specify which operators can be mutated
    #m1.mutation_operators = {
    #    "unaryOps": [ast.UAdd, ast.USub],
    #    "binOps": [ast.Add, ast.Sub, ast.Mult, ast.Div],
    #    "boolOps": [ast.And, ast.Or],
    #    "cmpOps": [ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE]
    #}

    # Perform the mutation and record results
    m1.mutate(mutation_types.COMPLEMENT, 2, 3, removeBackup = False, printSrcAfterMutate=True)

except Exception as ex:
    print(ex)

print("Finished!")