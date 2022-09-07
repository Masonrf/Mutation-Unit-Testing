import ast
from colorama import *
init()
from alive_progress import alive_bar

class Mutation:
    def __init__(self, fileName: str):
        self.filename = fileName
        self.srcStr = "pass"
        with alive_bar(2) as bar:
            bar.title = 'Initializing'
            print("Loading source from " + self.filename)
            self.__loadSource()
            bar()

            print("Parsing source into tree")
            self.tree = ast.parse(self.srcStr)
            bar()
            #analyze tree
        
    # Loads Python source code from file. Returns that source code as a string
    def __loadSource(self):
        try:
            if not (self.filename.lower().endswith('.py')):
                raise Exception('This program only supports python source code in .py files')
            with open(self.filename, "r") as srcFile:
                self.srcStr = srcFile.read()

        except FileNotFoundError:
            print(Fore.RED + Style.BRIGHT + "\nFile with name " + self.filename + " does not exist!\n" + Style.RESET_ALL)

        except Exception as ex:
            print(Fore.RED + Style.BRIGHT)
            print(ex)
            print(Style.RESET_ALL)

        except:
            print(Fore.RED + Style.BRIGHT + "\nAn exception occured when trying to read file " + self.filename + "\n" + Style.RESET_ALL)

            
    
    # Print out the source string
    def printSrc(self):
        if self.srcStr == "pass":
            print(Fore.YELLOW + "Cannot print source string. Invalid source code" + Style.RESET_ALL + "\n")

        else:
            print(Back.GREEN + "[From " + Style.BRIGHT + self.filename + Style.NORMAL + "]" + Style.RESET_ALL)
            print(self.srcStr + Style.RESET_ALL + "\n")
    
    # Print out the parse tree
    def printTree(self):
        if self.srcStr == "pass":
            print(Fore.YELLOW + "Cannot create tree. Invalid source code." + Style.RESET_ALL + "\n")

        else:
            print(Back.GREEN + "[Source file " + Style.BRIGHT + self.filename + Style.NORMAL + " as a tree]" + Style.RESET_ALL)
            print(ast.dump(self.tree, indent=2) + "\n")
    
    #mutate
    #"recompile"
    #execute unit tests & save