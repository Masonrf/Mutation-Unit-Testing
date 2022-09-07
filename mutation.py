import ast
from colorama import *
init()
from typing import final

class Mutation:
    def __init__(self, fileName: str):
        self.filename = fileName
        self.srcStr = Fore.YELLOW + Style.BRIGHT + "{Invalid source string}" + Style.RESET_ALL
        self.__loadSource()
        
    # Loads Python source code from file. Returns that source code as a string
    def __loadSource(self):
        try:
            if not (self.filename.lower().endswith('.py')):
                raise Exception('This program only supports python source code in .py files')
            with open(self.filename, "r") as srcFile:
                self.srcString = srcFile.read()

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
        print(Back.GREEN + "[From " + Style.BRIGHT + self.filename + Style.NORMAL + ":]" + Style.RESET_ALL)
        print(self.srcStr + Style.RESET_ALL)