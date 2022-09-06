import ast
from typing import final

class Mutation:
    def __init__(self, fileName: str):
        self.filename = fileName
        self.srcStr = "{Invalid source string}"
        try:
            self.srcStr = self.__loadSource()
        except:
            print("An exception occured")
        
    # Loads Python source code from file. Returns that source code as a string
    def __loadSource(self):
        try:
            if not (self.filename.lower().endswith('.py')):
                raise Exception('This program only supports python source in .py files')

            srcFile = open(self.filename, "r")
            srcString = srcFile.read()

        except FileNotFoundError:
            print("File with name " + self.filename + " does not exist!")

        except Exception as ex:
            print(ex)

        finally:
            srcFile.close()
            return srcString
    
    # Print out the source string
    def printSrc(self):
        print("[From " + self.filename + ":]\n" + self.srcStr)