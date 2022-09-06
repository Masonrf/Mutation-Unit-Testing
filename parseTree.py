import ast
from typing import final

# Loads Python source code from file. Returns that source code as a string
def loadSource(filename: str):
    
    try:
        if not (filename.lower().endswith('.py')):
            raise Exception('This program only supports python source in .py files')
        
        srcFile = open(filename, "r")
        srcString = srcFile.read()

    except FileNotFoundError:
        print("File with name " + filename + " does not exist!")
    except Exception as ex:
        print(ex)

    finally:
        srcFile.close()
        return srcString