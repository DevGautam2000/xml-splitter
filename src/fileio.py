import json as js

def readfile(filepath:str,returnFilePointer=False)->str or TextIOWrapper:
   
    filePointer=open(filepath,'r')

    if returnFilePointer:
        return filePointer

    content=filePointer.read()
    filePointer.close()
    return content.strip()

def readJson(filepath:str) -> dict:
    jsonRaw = readfile(filepath,returnFilePointer=True)
    return js.load(jsonRaw)

def writeFile(filepath:str,content:str) -> None:
    fp=open(f"{filepath}",'w')
    fp.write(content)           
    fp.close() 