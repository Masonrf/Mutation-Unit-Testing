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
        with alive_bar(3, title='Initializing') as initBar:
            # Load source from file
            print("Loading source from " + self.filename)
            self.__loadSource()
            initBar()

            # Parse source into tree
            print("Parsing source into tree")
            # It is possible to crash the Python interpreter with a sufficiently large/complex string due to stack depth limitations in Python’s AST compiler.
            self.tree = ast.parse(self.srcStr)
            initBar()


            # Analyze tree - look for pieces of code the unit test actually covers


            # Analyze tree - Count various operator types in the relevant piece of code
            print("Analyzing tree")
            self.__astNodeVisitorCallbacks_analyze(self.analysisInfo).visit(self.tree)
            print("Types and number of operators: ", self.analysisInfo)           
            initBar()


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


    # Information obtained from the analysis of the tree
    analysisInfo = {
        "unaryOps": [],
        "binOps": [],
        "boolOps": [],
        "compares": []
    }


    # Visit each node in the tree to obtain information on what mutatable source is in the tree
    # The information that is gathered is stored in analysisInfo
    class __astNodeVisitorCallbacks_analyze(ast.NodeVisitor):
        def __init__(self, analysis):
            self.analysis = analysis

        def visit_UnaryOp(self, node):
            self.analysis["unaryOps"].append((node.lineno, node.col_offset))
            self.generic_visit(node)
        
        def visit_BinOp(self, node):
            self.analysis["binOps"].append((node.lineno, node.col_offset))
            self.generic_visit(node)
        
        def visit_BoolOp(self, node):
            self.analysis["boolOps"].append((node.lineno, node.col_offset))
            self.generic_visit(node)
        
        def visit_Compare(self, node):
            self.analysis["compares"].append((node.lineno, node.col_offset))
            self.generic_visit(node)
    


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
        "binOps": ("Add", "Sub", "Mult", "Div", "FloorDiv", "Mod", "Pow", "LShift", "RShift", "BitOr", "BitXor", "BitAnd", "MatMult"),
        "boolOps": ("And", "Or"),
        "cmpOps": ("Eq", "NotEq", "Lt", "LtE", "Gt", "GtE", "Is", "IsNot", "In", "NotIn")
    }


    # Node transformer callback functions and info for mutating the AST
    class __astNodeTransformerCallbacks_mutate(ast.NodeTransformer, mutation_types):
        def __init__(self, operators: dict, mutationType, numRequestedMutations):
            self.operators = operators
            self.mutationType = mutationType
            self.numRequestedMutations = numRequestedMutations
            self.numMutated = 0

            # Initialize a list of operator line and column numbers that can be mutated based on mutationType
            # random.choices() function may also be helpful



        def shouldMutate(self, node):
            if self.numMutated >= self.numRequestedMutations:
                return False
            else:
                return True



        def visit_UnaryOp(self, node):
            if self.shouldMutate(node):
                try:
                    match self.mutationType:
                        case self.COMPLEMENT:
                            match node.op:
                                case ast.UAdd():
                                    if "USub" in self.operators["unaryOps"]:
                                        node.op = ast.USub()
                                        self.numMutated += 1

                                case ast.USub():
                                    if "UAdd" in self.operators["unaryOps"]:
                                        node.op = ast.UAdd()
                                        self.numMutated += 1
                                
                                case _:
                                    print("Operator of type ", type(node.op), " does not have a complementary operator.")

                        case self.RANDOM:
                            raise Exception('Mutation type not yet implemented')

                        case _:
                            raise Exception('Unknown mutation type')

                except Exception:
                    raise

            return node


        
        def visit_BinOp(self, node):
            if self.shouldMutate(node):
                try:
                    match self.mutationType:
                        case self.COMPLEMENT:
                            match node.op:
                                case ast.Add():
                                    if "Sub" in self.operators["binOps"]:
                                        node.op = ast.Sub()
                                        self.numMutated += 1

                                case ast.Sub():
                                    if "Add" in self.operators["binOps"]:
                                        node.op = ast.Add()
                                        self.numMutated += 1
                            
                                case ast.Mult():
                                    if "Div" in self.operators["binOps"]:
                                        node.op = ast.Div()
                                        self.numMutated += 1
                            
                                case ast.Div():
                                    if "Mult" in self.operators["binOps"]:
                                        node.op = ast.Mult()
                                        self.numMutated += 1
                                    
                                case ast.LShift():
                                    if "Rshift" in self.operators["binOps"]:
                                        node.op = ast.RShift()
                                        self.numMutated += 1

                                case ast.RShift():
                                    if "Lshift" in self.operators["binOps"]:
                                        node.op = ast.LShift()
                                        self.numMutated += 1

                                case _:
                                    print("Operator of type ", type(node.op), " does not have a complementary operator.")

                        case self.RANDOM:
                            raise Exception('This mutation type is not yet implemented')

                        case _:
                            raise Exception('Unknown mutation type')

                except Exception:
                    raise

            return node



        def visit_BoolOp(self, node):
            if self.shouldMutate(node):
                try:
                    match self.mutationType:
                        case self.COMPLEMENT:
                            match node.op:
                                case ast.And():
                                    if "Or" in self.operators["boolOps"]:
                                        node.op = ast.Or()
                                        self.numMutated += 1

                                case ast.Or():
                                    if "And" in self.operators["boolOps"]:
                                        node.op = ast.And()
                                        self.numMutated += 1
                                
                                case _:
                                    print("Operator of type ", type(node.op), " does not have a complementary operator.")

                        case self.RANDOM:
                            raise Exception('Mutation type not yet implemented')
                        
                        case _:
                            raise Exception('Unknown mutation type')

                except Exception:
                    raise

            return node
        

        #def visit_Constant(self, node):
        #    newNode = ast.Constant(100)
        #    return ast.copy_location(newNode, node)

    # An abstraction to be able to call any type of mutation function from one function call
    def mutate(self, mutation_type, iterations, numMutations):
        try:
            with alive_bar(iterations, title='Mutating') as mutBar:
                for i in range(iterations):
                    mutatedTree = copy.deepcopy(self.tree)

                    mutatedTree = self.__astNodeTransformerCallbacks_mutate(self.mutation_operators, mutation_type, numMutations).visit(mutatedTree)
                    
                    mutatedTree = ast.fix_missing_locations(mutatedTree)
                    print(ast.unparse(mutatedTree))

                    ## run unit test
                    
                    mutBar()


        except Exception as ex:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " An exception of type " + type(ex).__name__ + " occured when trying to mutate:" + Style.RESET_ALL)
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " " + str(ex) + Style.RESET_ALL)
            raise


    # mutate
    # "recompile"
    # execute unit tests & save