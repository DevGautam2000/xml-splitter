import os
import argparse
import shutil
import json

PROPERTIES_FILE_LOCATION:str = "/home/budhadityac/TKTN/regression_suite/master_data/jenkins/TKTN-properties.json"
jsonPropFp = open(PROPERTIES_FILE_LOCATION,'r')
jsonObject = json.load(jsonPropFp)

def parse_argument() -> tuple:
    parser = argparse.ArgumentParser(description='Script to handle message types')

    parser.add_argument('-d', '--inputDirectory', type=str, help='filepath from which messages are to be processed')

    args = parser.parse_args()

    if args.inputDirectory:
        
        try:
            inject_to_file(args.inputDirectory)
        except Exception as e:
            print(e)
    else:
        print("Error: Missing positional arguments. Use -h for help.")


def copyNecessaryFilesToInputDirectory(inputDirectory:str) -> None:
    shutil.copy(f"{jsonObject['home']}{jsonObject['XmlComparatorGeneral']['XmlSplitterLocation']}/scripts/main.js",f"{inputDirectory}/main.js")
    shutil.copy(f"{jsonObject['home']}{jsonObject['XmlComparatorGeneral']['XmlSplitterLocation']}/scripts/style.css",f"{inputDirectory}/style.css")

def inject_to_file(inputDirectory:str) -> None:
    for filename in os.listdir(inputDirectory):
        if filename.endswith('.html'):
            if "summary" not in filename:
                fp = open(f"{inputDirectory}/{filename}",'r')
                
                newLines = []
                line = fp.readline()
                while line:
                    newLines.append(line)

                    if "<head>" in line:
                    
                        cssLine = f'<link rel="stylesheet" href="style.css">'
                        scriptLine = f'<script src="main.js" defer></script>'
                        newLines.append(cssLine)
                        newLines.append(scriptLine)

                        

                    line = fp.readline()

                
                fpw = open(f"{inputDirectory}/{filename}",'w')
                fpw.writelines(newLines)
                fpw.close()
                copyNecessaryFilesToInputDirectory(inputDirectory)
                

if __name__ == "__main__":
	parse_argument()
