
import bs4 as bs
from fileio import writeFile
from keys import MandatoryKeys,checkMandatoryKeys
import logging

bs4Config = {
    "parser":"lxml"
}

attributeWhiteList = ['Ccy']

mandatoryKeys = MandatoryKeys()
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename='../logs/logs.log',format=FORMAT,level=logging.DEBUG)

def parse_xml_message(messageType:str,message:str,identifierPath:[str]) -> tuple:
    identifierNodeList = []
    for path in identifierPath:
        soup:bs.BeautifulSoup = bs.BeautifulSoup(message,bs4Config.get("parser"))
        identifierPathRaw = path
        identifierSelector:str = " ".join(path.strip().lower().split("/"))

        identifierSelectorList = soup.select(f"{identifierSelector}")
       
        if len(identifierSelectorList)>0:
            identifierNodeList.append(identifierSelectorList[0])
            # print(identifierNodeList)


    if len(identifierNodeList) == 1:
        identifierValue:str = identifierNodeList[0].text
        logger.debug(f"{identifierValue=}")
        return (message,identifierValue)
    else:
        logger.debug(f"Error parsing XML :: invalid identifier : {identifierPathRaw}")
        raise Exception(f"Error parsing XML :: invalid identifier : {identifierPathRaw}")


def wrap_message_attributes(messages:list,attributeCongiurations:list) -> list:

    logger.debug("Wrapping started")
    for msg_index,message in enumerate(messages):
        
        for attribute in attributeCongiurations:

            areKeysPresent:bool = checkMandatoryKeys([
                {
                    "parent": attribute,
                    "keys": [mandatoryKeys.name,mandatoryKeys.parent,mandatoryKeys.terminator]
                }
            ])

            attr:str = attribute["name"].strip()
            wrapper:str =  attribute.get("wrapper")
            wrapperLeft:str =  attribute.get("wrapper-left")
            wrapperRight:str =  attribute.get("wrapper-right")
            parent:str = attribute.get("parent")
            changeNameOfAttrTo:str = attribute.get("change-attr-name-to")
            # ignore:list =attribute.get("ignore")

            
            
            newMessage:[str] = []

            if wrapper:
                if wrapperLeft != None or wrapperRight != None:
                    logger.debug("Cannot use wrapper-left or wrapper-right with wrapper")
                    raise Exception("Cannot use wrapper-left or wrapper-right with wrapper")
                
            else:
                if wrapperLeft == None or wrapperRight == None:
                    logger.debug("Missing wrapper-left or wrapper-right")
                    raise Exception("Missing wrapper-left or wrapper-right")
            
                
            terminator:str = attribute["terminator"]

            lines:list = message.splitlines()
            
            
            for line_index,line in enumerate(lines):
                if parent in line and attr in line :
                   
                    # if parent != "*" and parent not in line:
                    #     continue

                    
                    # if ignore != None:
                    #     ignoreList = "".join(["1" if tag in line else "0" for tag in ignore])
                    #     print(ignoreList)
                    #     if "1" in ignoreList:
                    #         print("ignored")
                    #         continue
                    

                    lenAttr:int = len(attr)
                    attrIndStart:int = line.index(attr)
                    endIndAttr:int =  attrIndStart + lenAttr
                    indOfClosingTag:int = line.index(terminator)
                    
                    startOfWrapper:int = endIndAttr + 1
                    endOfWrapper:int = indOfClosingTag

                    attrValue:str = line[startOfWrapper:endOfWrapper]

                    if changeNameOfAttrTo != None:
                        line = line[:attrIndStart] + changeNameOfAttrTo + line[endIndAttr:]

                        startOfWrapper = line.index(changeNameOfAttrTo) + len(changeNameOfAttrTo)+1
                        endOfWrapper = line.index(terminator)

                        #print(line[:startOfWrapper])
                        
                    if wrapper != None:

                        line = line[:startOfWrapper] + wrapper.strip() + attrValue + wrapper.strip() + line[endOfWrapper:]
                    elif wrapperLeft != None and wrapperRight != None:
                        line = line[:startOfWrapper] + wrapperLeft.strip() + attrValue + wrapperRight.strip() + line[endOfWrapper:]
                    
                newMessage.append(line)

            message = "\n".join(newMessage)

        messages[msg_index] = message

    logger.debug("Wrapping done")
    return messages


def wrap_message_root(wrapperElement:str,message:str) -> str:
    
    logger.debug(f"Wrapping root element with: <{wrapperElement}>...</{wrapperElement}>")
    wrappedMessage = f"<{wrapperElement}>{message}</{wrapperElement}>"
    return wrappedMessage
