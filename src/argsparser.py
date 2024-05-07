import argparse
from fileio import readfile

def parse_argument() -> tuple:
    parser = argparse.ArgumentParser(description='Script to handle message types')

    parser.add_argument('-t', '--messageTypes', type=str, help='Comma-separated strings : [ example: "m1,m2"]')
    parser.add_argument('-f', '--inputFilepath', type=str, help='filepath from which messages are to be processed')
    parser.add_argument('-o', '--outputFilepath', type=str, help='filepath to which messages are to be dumped')

    args = parser.parse_args()

    if args.messageTypes and args.inputFilepath and args.outputFilepath:
        
        try:
            messageTypes:[str] = [ msg.strip() for msg in args.messageTypes.split(',') ]
            return (messageTypes , readfile(args.inputFilepath), args.outputFilepath)
        except Exception as e:
            print(e)
    else:
        print("Error: Missing positional arguments. Use -h for help.")