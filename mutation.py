import sys
sys.dont_write_bytecode = True
import ast
from colorama import *
init()
import copy
import traceback
import random
from coverage import CoverageData
from pathlib import Path
from shutil import rmtree, copytree
import subprocess
from junitparser import *

# Types of mutations to be called with mutation.mutation_types.TYPE
class mutation_types():
    COMPLEMENT = 1
    RANDOM = 2

# Information obtained from the analysis of the tree
class analysisInfo():
    def __init__(self, fileName, tree, coverageLineNums):
        self.fileName = fileName
        self.tree = tree
        self.coverageLineNums = coverageLineNums
        self.operatorDict = {
            "unaryOps": [],
            "binOps": [],
            "boolOps": [],
            "cmpOps": []
        }
    
    def __str__(self):
        printStr = "Filename: " + str(self.fileName) + "\n"
        printStr += "Tree: " + str(self.tree) + "\n"
        printStr += "Coverage Lines: " + str(self.coverageLineNums) + "\n"
        printStr += "Operators: " + str(self.operatorDict) + "\n"
        return printStr



class Mutation():
    def __init__(self, moduleNameToTest: str, unitTestFileName: str):
        self.unitTestFileName = unitTestFileName
        self.moduleNameToTest = moduleNameToTest

        self.logDir = Path(self.__getMutationDirName() + "/pytest-logs")

        # List of analysisInfo() objects
        self.analysisInfoList = []
        try:
            if self.logDir.exists():
                print("Overwriting old logs")
                rmtree(str(self.logDir))

            # (Re)make the mutation-unit-test/ folder
            self.logDir.mkdir(parents=True, exist_ok=True)

            print("\nRunning initial pytest tests")
            with open(str(self.logDir) + "/initial-pytest-log.txt", "w+") as covReportLog:
                # Analyze tree - look for pieces of code the unit test actually covers
                print("\nRunning a code coverage report on the given unit test file")
                p_init = subprocess.Popen("python3 -m pytest --junit-xml=\"" + self.__getMutationDirName() + "/initial-report.xml\" --cov-report term-missing --cov=" + self.moduleNameToTest + " " + self.unitTestFileName, stdout=covReportLog, stderr=covReportLog)
                p_init.wait()

            # Check the pytest xml to see if any tests failed on default
            initialXML = JUnitXml.fromfile(self.__getMutationDirName() + "/initial-report.xml")
            for suite in initialXML:
                print("Suite " + str(suite.name) + " ran " + str(suite.tests) + " tests in " + str(suite.time) + " s")
                if suite.errors == 0 and suite.failures == 0 and suite.skipped == 0:
                    print("All tests passed.\n")
                else:
                    if suite.errors > 0:
                        print(Fore.WHITE + Back.YELLOW + "[WARNING]" + Back.RESET + Style.BRIGHT + Fore.YELLOW + str(suite.errors) + " initial test(s) threw an error! Mutation results may not be useful." + Style.RESET_ALL)
                    if suite.failures > 0:
                        print(Fore.WHITE + Back.YELLOW + "[WARNING]" + Back.RESET + Style.BRIGHT + Fore.YELLOW + str(suite.failures) + " initial test(s) failed! Mutation results may not be useful." + Style.RESET_ALL)
                    if suite.skipped > 0:
                        print(Fore.WHITE + Back.YELLOW + "[WARNING]" + Back.RESET + Style.BRIGHT + Fore.YELLOW + str(suite.skipped) + " initial test(s) were skipped! Mutation results may not be useful." + Style.RESET_ALL)


            # Parse coverage data
            print("\nParsing coverage report data")
            report = CoverageData()
            report.read()
            print("In data file: ", report.base_filename())
            print("Measured files: ", report.measured_files())
            for i in report.measured_files():
                print("File: ", i)
                print("Line numbers: ", report.lines(i))

            # Load source(s) from file(s) and parse into tree(s)
            print()
            for srcFileName in report.measured_files():
                print("Loading and parsing source from " + str(srcFileName))
                # It is possible to crash the Python interpreter with a sufficiently large/complex string due to stack depth limitations in Python’s AST compiler.
                srcString = self.__loadSource(srcFileName)
                tree = ast.parse(srcString)

                self.analysisInfoList.append(analysisInfo(srcFileName, tree, report.lines(srcFileName)))

                
            # Analyze tree - Count various operator types in the relevant piece of code
            for item in self.analysisInfoList:
                print("\nAnalyzing tree at: ", item.fileName)
                self.__astNodeVisitorCallbacks_analyze(item).visit(item.tree)
                print("Types and number of operators: ", item)           
            
        except Exception as ex:
            traceback.print_exc()
            raise


    # Loads Python source code from file. Returns that source code as a string
    def __loadSource(self, srcFileName: str):
        try:
            if not (srcFileName.lower().endswith('.py')):
                raise Exception('This program only supports python source code in .py files')
            with open(srcFileName, "r") as srcFile:
                srcStr = srcFile.read()
            
            return srcStr

        except FileNotFoundError:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " File with name " + self.srcFileName + " does not exist!" + Style.RESET_ALL)
            raise

        except Exception as ex:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " An exception of type " + type(ex).__name__ + " occurred when trying to read file " + self.srcFileName + ":" + Style.RESET_ALL)
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " " + str(ex) + Style.RESET_ALL)
            traceback.print_exc()
            raise




    # Visit each node in the tree to obtain information on what mutatable source is in the tree
    # The information that is gathered is stored in analysisInfo
    class __astNodeVisitorCallbacks_analyze(ast.NodeVisitor):
        def __init__(self, analysis: analysisInfo):
            self.analysis = analysis

        def visit_UnaryOp(self, node):
            self.analysis.operatorDict["unaryOps"].append((node.lineno, node.col_offset, type(node.op)))
            self.generic_visit(node)
        
        def visit_BinOp(self, node):
            self.analysis.operatorDict["binOps"].append((node.lineno, node.col_offset, type(node.op)))
            self.generic_visit(node)
        
        def visit_BoolOp(self, node):
            self.analysis.operatorDict["boolOps"].append((node.lineno, node.col_offset, type(node.op)))
            self.generic_visit(node)
        
        def visit_Compare(self, node):
            self.analysis.operatorDict["cmpOps"].append((node.lineno, node.col_offset, [type(item) for item in node.ops]))
            self.generic_visit(node)
    


    # Print out the source string
    def printSrc(self):
        for item in self.analysisInfoList:
            srcStr = self.__loadSource(item.fileName)
            print()
            print(Back.GREEN + "[From " + Style.BRIGHT + item.fileName + Style.NORMAL + "]" + Style.RESET_ALL)
            print(srcStr + Style.RESET_ALL + "\n\n\n")



    # Print out the parse tree
    def printTree(self):
        for item in self.analysisInfoList:
            srcStr = ast.dump(item.tree, indent=2)
            print()
            print(Back.GREEN + "[Source file " + Style.BRIGHT + item.fileName + Style.NORMAL + " as a tree]" + Style.RESET_ALL)
            print(srcStr + "\n\n\n")
    


    # Converts the parse tree back into code
    def __exportTreeAsSource(self, tree, destinationFilename, printSrc=False):
        try:
            print("Converting from tree to source")
            # Some warnings about the unparse function from the library documentation:
            # Warning The produced code string will not necessarily be equal to the original code that generated the ast.AST object.
            # Trying to unparse a highly complex expression would result with RecursionError.
            src = ast.unparse(tree)
            if printSrc:
                print("\n", src)

            print("Writing to file " + destinationFilename)
            with open(destinationFilename, "w+") as destFile:
                destFile.write(src)

        except Exception as ex:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " An exception of type " + type(ex).__name__ + " occurred when trying to write file " + destinationFilename + ":" + Style.RESET_ALL)
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " " + str(ex) + Style.RESET_ALL)
            #traceback.print_exc()
            raise



    # Valid operators that can be used in the mutation
    mutation_operators = {
        "unaryOps": [ast.UAdd, ast.USub, ast.Not, ast.Invert],
        "binOps": [ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult],
        "boolOps": [ast.And, ast.Or],
        "cmpOps": [ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn]
    }


    # Node transformer callback functions and info for mutating the AST
    class __astNodeTransformerCallbacks_mutate(ast.NodeTransformer, mutation_types):
        def __init__(self, operators: dict, mutationType, numRequestedMutations, analysisInfoNode: analysisInfo):
            validComplementaryOpsList = [ast.UAdd, ast.USub, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.LShift, ast.RShift, ast.And, ast.Or, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn]
            self.operators = operators
            self.mutationType = mutationType
            self.numMutated = 0

            # Initialize a list of operator line and column numbers that can be mutated based on mutationType
            # random.choices() function may also be helpful
            self.opsToMutate = []
            
            analysisDict = analysisInfoNode.operatorDict

            for key in analysisDict:
                for item in range(len(analysisDict[key])):
                    match self.mutationType:
                        case mutation_types.COMPLEMENT:
                            # Check both the valid complementary operator list and the given list of operators that are acceptable to mutate
                            # Comparisons have lists of operators
                            if type(analysisDict[key][item][2]) is list:
                                for op in range(len(analysisDict[key][item][2])):
                                    # Check that the operator is in the valid complementary operators list and provided list of operators to use. Also make sure the line number matches a coverage line number
                                    if (analysisDict[key][item][2][op] in validComplementaryOpsList) and (analysisDict[key][item][2][op] in self.operators[key]) and (analysisDict[key][item][0] in analysisInfoNode.coverageLineNums):
                                        # Split up lists into single operators
                                        self.opsToMutate.append((analysisDict[key][item][0], analysisDict[key][item][1], analysisDict[key][item][2][op]))
                                        print("Found valid operator in list: ", self.opsToMutate[-1])

                            # Non comparison
                            # Check that the operator is in the valid complementary operators list and provided list of operators to use. Also make sure the line number matches a coverage line number
                            elif (analysisDict[key][item][2] in validComplementaryOpsList) and (analysisDict[key][item][2] in self.operators[key]) and (analysisDict[key][item][0] in analysisInfoNode.coverageLineNums):
                                self.opsToMutate.append(analysisDict[key][item])
                                print("Found valid operator: ", self.opsToMutate[-1])

                        # Some mutations with RANDOM do not make sense/will probably not be allowed by the interpreter. Will need to fix those in the future.
                        case mutation_types.RANDOM:
                            # Comparisons have lists of operators
                            if type(analysisDict[key][item][2]) is list:
                                for op in range(len(analysisDict[key][item][2])):
                                    # Check that the operator is in the provided list of operators to use. Also make sure the line number matches a coverage line number
                                    if (analysisDict[key][item][2][op] in self.operators[key]) and (analysisDict[key][item][0] in analysisInfoNode.coverageLineNums):
                                        # Split up lists into single operators
                                        self.opsToMutate.append((analysisDict[key][item][0], analysisDict[key][item][1], analysisDict[key][item][2][op]))
                                        print("Found valid operator in list: ", self.opsToMutate[-1])

                            # Non comparison
                            # Check that the operator is in the provided list of operators to use. Also make sure the line number matches a coverage line number
                            elif (analysisDict[key][item][2] in self.operators[key]) and (analysisDict[key][item][0] in analysisInfoNode.coverageLineNums):
                                self.opsToMutate.append(analysisDict[key][item])
                                print("Found valid operator: ", self.opsToMutate[-1])
                        
                        case _:
                            raise Exception('Unknown mutation type!')

            self.numOps = len(self.opsToMutate)
            print("Total number of valid operators found: ", self.numOps, "\nNumber of operators that the user requested be mutated: ", numRequestedMutations)
            
            if numRequestedMutations > self.numOps:
                numRequestedMutations = self.numOps
                print(Back.YELLOW + "[WARNING]" + Back.RESET + Style.BRIGHT + Fore.YELLOW + " Number of requested mutations is larger than the number of mutatable operators! This will mutate all operators." + Style.RESET_ALL)
            
            # Randomly remove ops from list to get to the number of requested mutations
            for i in range(self.numOps - numRequestedMutations):
                self.opsToMutate.pop(random.randrange(len(self.opsToMutate)))
            
            print("Operators that will be mutated: ", self.opsToMutate)
            
            self.numOps = len(self.opsToMutate)



        # Check the list to see if the node should be mutated
        def shouldMutate(self, lineNum, ColNum, Ops):
            nodeInfo = (lineNum, ColNum, type(Ops))
            #print(nodeInfo)
            if self.numMutated >= self.numOps:
                # Something went wrong if this happens...
                return False

            # check if op in list of ops to mutate
            elif nodeInfo in self.opsToMutate:
                return True 

            else:
                return False



        # Mutate Unary Operators:
        # UnaryOps: ast.UAdd, ast.USub, ast.Not, ast.Invert
        def visit_UnaryOp(self, node):
            self.generic_visit(node)
            if self.shouldMutate(node.lineno, node.col_offset, node.op):
                try:
                    match self.mutationType:
                        case mutation_types.COMPLEMENT:
                            if isinstance(node.op, ast.UAdd):
                                node.op = ast.USub()
                                self.numMutated += 1

                            elif isinstance(node.op, ast.USub):
                                node.op = ast.UAdd()
                                self.numMutated += 1
                                
                            else:
                                print("Operator of type ", type(node.op), " does not have a complementary operator.")

                        case mutation_types.RANDOM:
                            # Make sure a different operator is chosen
                            tmpOps = copy.deepcopy(self.operators["unaryOps"])
                            tmpOps.remove(type(node.op))
                            node.op = (random.choice(tmpOps))()

                        case _:
                            raise Exception('Unknown mutation type')

                except Exception:
                    raise

            return node


        
        # Mutate Binary Operators
        # BinOps: ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult
        def visit_BinOp(self, node):
            self.generic_visit(node)
            if self.shouldMutate(node.lineno, node.col_offset, node.op):
                try:
                    match self.mutationType:
                        case mutation_types.COMPLEMENT:
                            if isinstance(node.op, ast.Add):
                                node.op = ast.Sub()
                                self.numMutated += 1

                            elif isinstance(node.op, ast.Sub):
                                node.op = ast.Add()
                                self.numMutated += 1       

                            elif isinstance(node.op, ast.Mult):
                                node.op = ast.Div()
                                self.numMutated += 1
                            
                            elif isinstance(node.op, ast.Div):
                                node.op = ast.Mult()
                                self.numMutated += 1

                            elif isinstance(node.op, ast.LShift):
                                node.op = ast.RShift()
                                self.numMutated += 1

                            elif isinstance(node.op, ast.RShift):
                                node.op = ast.LShift()
                                self.numMutated += 1

                            else:
                                print("Operator of type ", type(node.op), " does not have a complementary operator.")

                        case mutation_types.RANDOM:
                            tmpOps = copy.deepcopy(self.operators["binOps"])
                            tmpOps.remove(type(node.op))
                            node.op = (random.choice(tmpOps))()

                        case _:
                            raise Exception('Unknown mutation type')

                except Exception:
                    raise

            return node



        # Mutate the Boolean operators
        # BoolOps: ast.And, ast.Or
        def visit_BoolOp(self, node):
            self.generic_visit(node)
            if self.shouldMutate(node.lineno, node.col_offset, node.op):
                try:
                    match self.mutationType:
                        case mutation_types.COMPLEMENT:
                            if isinstance(node.op, ast.And):
                                node.op = ast.Or()
                                self.numMutated += 1

                            elif isinstance(node.op, ast.Or):
                                node.op = ast.And()
                                self.numMutated += 1
                                
                            else:
                                print("Operator of type ", type(node.op), " does not have a complementary operator.")

                        case mutation_types.RANDOM:
                            # Make sure a different operator is chosen
                            tmpOps = copy.deepcopy(self.operators["boolOps"])
                            tmpOps.remove(type(node.op))
                            node.op = (random.choice(tmpOps))()
                        
                        case _:
                            raise Exception('Unknown mutation type')

                except Exception:
                    raise

            return node
        


        # Mutate comparison operators. This one is annoying because operators are in a list in the parse tree
        # CmpOps: ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn
        def visit_Compare(self, node):
            self.generic_visit(node)
            for op in range(len(node.ops)):
                if self.shouldMutate(node.lineno, node.col_offset, node.ops[op]):
                    try:
                        match self.mutationType:
                            case mutation_types.COMPLEMENT:
                                if isinstance(node.ops[op], ast.Eq):
                                    node.ops[op] = ast.NotEq()
                                    self.numMutated += 1

                                elif isinstance(node.ops[op], ast.NotEq):
                                    node.ops[op] = ast.Eq()
                                    self.numMutated += 1
                                
                                elif isinstance(node.ops[op], ast.Lt):
                                    node.ops[op] = ast.Gt()
                                    self.numMutated += 1
                                
                                elif isinstance(node.ops[op], ast.LtE):
                                    node.ops[op] = ast.GtE()
                                    self.numMutated += 1
                                
                                elif isinstance(node.ops[op], ast.Gt):
                                    node.ops[op] = ast.Lt()
                                    self.numMutated += 1
                                
                                elif isinstance(node.ops[op], ast.GtE):
                                    node.ops[op] = ast.LtE()
                                    self.numMutated += 1
                                
                                elif isinstance(node.ops[op], ast.Is):
                                    node.ops[op] = ast.IsNot()
                                    self.numMutated += 1
                                
                                elif isinstance(node.ops[op], ast.IsNot):
                                    node.ops[op] = ast.Is()
                                    self.numMutated += 1
                                
                                elif isinstance(node.ops[op], ast.In):
                                    node.ops[op] = ast.NotIn()
                                    self.numMutated += 1
                                
                                elif isinstance(node.ops[op], ast.NotIn):
                                    node.ops[op] = ast.In()
                                    self.numMutated += 1
                                    
                                else:
                                    print("Operator of type ", type(node.ops[op]), " does not have a complementary operator.")

                            case mutation_types.RANDOM:
                                # Make sure a different operator is chosen
                                tmpOps = copy.deepcopy(self.operators["cmpOps"])
                                tmpOps.remove(type(node.ops[op]))
                                node.ops[op] = (random.choice(tmpOps))()
                            
                            case _:
                                raise Exception('Unknown mutation type')

                    except Exception:
                        raise

            return node


    def __getMutationDirName(self) -> str:
        return str(Path().resolve()) + "/mutation-unit-test"
    
    def __getFullModulesToTestPath(self) -> str:
        return str(Path().resolve()) + "/" + self.moduleNameToTest


    # An abstraction to be able to call any type of mutation function from one function call
    def mutate(self, mutation_type: mutation_types, iterations: int, numMutations: int, printTreeAfterMutate=False, removeBackup=True):
        try:
            if iterations < 1:
                raise Exception('Number of iterations cannot be less than 1!')
            if numMutations < 1:
                raise Exception('Number of mutations cannot be less than 1!')

            # Remove old backup if it exists
            backupPath = Path(self.__getMutationDirName() + "/backup-" + self.moduleNameToTest)
            if backupPath.exists():
                print("Overwriting old backup")
                rmtree(str(backupPath))
            
            # Backup files that are going to be overwritten on mutate
            copytree(self.__getFullModulesToTestPath(), str(backupPath))

            # Start mutation
            for i in range(iterations):
                # Each python file
                for item in self.analysisInfoList:
                    mutatedTree = copy.deepcopy(item.tree)
                    mutatedTree = self.__astNodeTransformerCallbacks_mutate(self.mutation_operators, mutation_type, numMutations, item).visit(mutatedTree)
                    mutatedTree = ast.fix_missing_locations(mutatedTree)

                    if printTreeAfterMutate:
                        print(ast.unparse(mutatedTree))
                    
                    self.__exportTreeAsSource(mutatedTree, item.fileName)

                print("\nRunning pytest on iteration " + str(i))
                with open(str(self.logDir) + "/pytest-log-iteration-" + str(i) + ".txt", "w+") as iterationLog:
                    p_mut = subprocess.Popen("python3 -m pytest --junit-xml=\"" + self.__getMutationDirName() + "/report-iteration-" + str(i) + ".xml\" " + self.unitTestFileName, stdout=iterationLog, stderr=iterationLog)
                    p_mut.wait()

                # Get results from xml file
                print("Results:")
                iterationXML = JUnitXml.fromfile(self.__getMutationDirName() + "/report-iteration-" + str(i) + ".xml")
                for suite in iterationXML:
                    print("Suite " + str(suite.name) + " ran " + str(suite.tests) + " tests in " + str(suite.time) + " s")
                    if suite.errors > 0:
                        print(Fore.WHITE + Back.YELLOW + "[WARNING]" + Back.RESET + Style.BRIGHT + Fore.YELLOW + str(suite.errors) + " mutated test(s) threw an error! Mutation results may not be useful." + Style.RESET_ALL)
                    if suite.skipped > 0:
                        print(Fore.WHITE + Back.YELLOW + "[WARNING]" + Back.RESET + Style.BRIGHT + Fore.YELLOW + str(suite.skipped) + " mutated test(s) were skipped! Mutation results may not be useful." + Style.RESET_ALL)

                    for testcase in suite:
                        if len(testcase.result) > 1:
                            raise Exception('Unexpected number of results from xml file')
                        result = testcase.result[0]
                        resultTypeStr = ""

                        if len(testcase.result) == 0:
                            resultTypeStr = "Passed"
                            print(str(testcase.classname) + ": " + str(testcase.name) + " -> " + resultTypeStr)
                        else:
                            if type(result) is junitparser.Failure:
                                resultTypeStr = "failure"
                            elif type(result) is junitparser.Error:
                                resultTypeStr = "error"
                            elif type(result) is junitparser.Skipped:
                                resultTypeStr = "skipped"
                            else:
                                resultTypeStr = "UNKNOWN!"

                            print(str(testcase.classname) + ": " + str(testcase.name) + " -> " + resultTypeStr + " (" + result.message.replace('\n', ' ') + ")")

                # Append results to report in mutation-unit-test/
                
            # Copy backup back to original location
            rmtree(self.__getFullModulesToTestPath())
            copytree(str(backupPath), self.__getFullModulesToTestPath())

            # Remove iteration directory
            if removeBackup:
                rmtree(str(backupPath))


        except Exception as ex:
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " An exception of type " + type(ex).__name__ + " occurred when trying to mutate:" + Style.RESET_ALL)
            print(Fore.WHITE + Back.RED + "[Error]" + Back.RESET + Style.BRIGHT + Fore.RED + " " + str(ex) + Style.RESET_ALL)
            traceback.print_exc()

            # Copy backup back to original location
            print(Fore.WHITE + Back.YELLOW + "[WARNING]" + Back.RESET + Style.BRIGHT + Fore.YELLOW + " Restoring from backup due to exception in mutate()." + Style.RESET_ALL)
            rmtree(self.__getFullModulesToTestPath())
            copytree(str(backupPath), self.__getFullModulesToTestPath())
            raise



# make into package and require dependencies

# append result of run to result file in mutation-unit-test folder
