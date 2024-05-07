class MandatoryKeys:

    def __init__(self):
        self.messageConfig:str ="message-config"
        self.supportedMessageTypes:str ="supported-message-types"
        self.messages:str ="messages"
        self.types:str="types"
        self.configuration:str="configuration"
        self.identifierPath:str="identifier-path"
        self.delimeter:str="delimeter"
        self.pattern:str="pattern"
        self.attributes:str="attributes"
        self.filter:str="filter"
        self.name:str="name"
        self.parent:str="parent"
        self.terminator:str="terminator"
        self.messageIdentifierTag="message-identifier-tag"

def checkMandatoryKeys(parentKeyList: [{}] ) -> bool:

    missingKeyList:list = []

    def checkKeysInObject(keys:[str],object:[str]):
        for key in keys:
            if  key not in object.keys():
                missingKeyList.append(key)
                raise Exception(f"Missing configuration :: key [{key}] not found.")

    
    for parentKey in parentKeyList:
        if parentKey.get("parent"):
            checkKeysInObject(parentKey.get("keys"),parentKey.get("parent"))

    return len(missingKeyList) == 0
