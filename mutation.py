import ast
from colorama import *
init()
from alive_progress import alive_bar
import copy
import traceback

class Mutation:
    def __init__(self, fileName: str):
        self.filename = fileName
        self.srcStr = ""
        print()
        with alive_bar(2, title='Initializing') as initBar:
            print("Loading source from " + self.filename)
            self.__loadSource()
            initBar()

            print("Parsing source into tree")
            # It is possible to crash the Python interpreter with a sufficiently large/complex string due to stack depth limitations in Python’s AST compiler.
            self.tree = ast.parse(self.srcStr)
            initBar()
            #analyze tree - look for pieces of code the unit test actually covers



    # Loads Python source code from file. Returns that source code as a string
    def __loadSource(self):
        try:
            if not (self.filename.lower().endswith('.py')):
                raise Exception('This program only supports python source code in .py files')
            with open(self.filename, "r") as srcFile:
                self.srcStr = srcFile.read()

        except FileNotFoundError:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " File with name " + self.filename + " does not exist!" + Style.RESET_ALL)
            raise

        except Exception as ex:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " An exception of type " + type(ex).__name__ + " occured when trying to read file " + self.filename + ":" + Style.RESET_ALL)
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " " + str(ex) + Style.RESET_ALL)
            raise


    
    # Print out the source string
    def printSrc(self):
        if self.srcStr == "":
            print(Fore.YELLOW + "Cannot print source string. Invalid source code" + Style.RESET_ALL + "\n")

        else:
            print()
            print(Back.GREEN + "[From " + Style.BRIGHT + self.filename + Style.NORMAL + "]" + Style.RESET_ALL)
            print(self.srcStr + Style.RESET_ALL + "\n")



    # Print out the parse tree
    def printTree(self):
        if self.srcStr == "":
            print(Fore.YELLOW + "Cannot create tree. Invalid source code." + Style.RESET_ALL + "\n")

        else:
            print()
            print(Back.GREEN + "[Source file " + Style.BRIGHT + self.filename + Style.NORMAL + " as a tree]" + Style.RESET_ALL)
            print(ast.dump(self.tree, indent=2) + "\n")
    


    # Converts the parse tree back into code
    def __exportTreeAsSource(self, tree, destinationFilename):
        try:
            print("ahh")
            with alive_bar(2, title='Exporting Mutated Source') as exportBar:
                print("Converting from tree to source")
                # Some warnings about the unparse function from the library documentation:
                # Warning The produced code string will not necessarily be equal to the original code that generated the ast.AST object.
                # Trying to unparse a highly complex expression would result with RecursionError.
                src = ast.unparse(tree)
                exportBar()

                print("Writing to file " + destinationFilename)
                with open(destinationFilename, "w") as destFile:
                    destFile.write(src)
                exportBar()
                
                

        except Exception as ex:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " An exception of type " + type(ex).__name__ + " occured when trying to write file " + destinationFilename + ":" + Style.RESET_ALL)
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " " + str(ex) + Style.RESET_ALL)
            raise



    # Types of mutations to be called with mutation.mutation_types.TYPE
    class mutation_types():
        COMPLEMENT = 1
        RANDOM = 2

    # Valid operators that can be used in the mutation
    mutation_operators = {
        "unaryOps": ("UAdd", "USub", "Not", "Invert"),
        "binOps": ("Add", "Sub", "Mult", "Div", "FloorDiv", "Mod", "Pow", "LShift", "RShift", "BitOr", "BitXor", "BitAnd", "MatMult")
    }


    # Node transformer callback functions and info for visiting and modifying the AST
    class __astNodeTransformerCallbacks(ast.NodeTransformer, mutation_types):
        def __init__(self, operators: dict, mutationType):
            self.operators = operators
            self.mutationType = mutationType

        def visit_UnaryOp(self, node):
            return node

        
        def visit_BinOp(self, node):
            try:
                match self.mutationType:
                    case self.COMPLEMENT:
                        match node.op:
                            case ast.Add():
                                if "Sub" in self.operators["binOps"]:
                                    node.op = ast.Sub()

                            case ast.Sub():
                                if "Add" in self.operators["binOps"]:
                                    node.op = ast.Add()
                        
                            case ast.Mult():
                                if "Div" in self.operators["binOps"]:
                                    node.op = ast.Div()
                        
                            case ast.Div():
                                if "Mult" in self.operators["binOps"]:
                                    node.op = ast.Mult()
                                
                            case ast.LShift():
                                if "Rshift" in self.operators["binOps"]:
                                    node.op = ast.RShift()

                            case ast.RShift():
                                if "Lshift" in self.operators["binOps"]:
                                    node.op = ast.LShift()

                            
                            case _:
                                print("Operator of type ", type(node.op), " does not have a complementary operator.")

                    case self.RANDOM:
                        raise Exception('This mutation type is not yet implemented')

                    case _:
                        raise Exception('Unknown mutation type')

                return node

            except Exception:
                raise


        #def visit_Constant(self, node):
        #    newNode = ast.Constant(100)
        #    return ast.copy_location(newNode, node)

    # An abstraction to be able to call any type of mutation function from one function call
    def mutate(self, mutation_type, iterations, numMutations):
        try:
            with alive_bar(iterations, title='Mutating') as mutBar:
                for i in range(iterations):
                    mutatedTree = copy.deepcopy(self.tree)

                    if mutation_type == self.mutation_types.COMPLEMENT:
                        self.__mutateComplement(mutatedTree, numMutations)

                    elif mutation_type == self.mutation_types.RANDOM:
                        pass

                    else:
                        raise Exception('Unknown mutation type')
                    
                    mutatedTree = ast.fix_missing_locations(mutatedTree)
                    print(ast.unparse(mutatedTree))

                    ## run unit test
                    
                    mutBar()


        except Exception as ex:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " An exception of type " + type(ex).__name__ + " occured when trying to mutate:" + Style.RESET_ALL)
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " " + str(ex) + Style.RESET_ALL)
            raise
    
    

    def __mutateComplement(self, mutatedTree, numMutations):
        try:
            transformer = self.__astNodeTransformerCallbacks(self.mutation_operators, self.mutation_types.COMPLEMENT)
            mutatedTree = transformer.visit(mutatedTree)
        except Exception:
            raise




    # mutate
    # "recompile"
    # execute unit tests & save