from keys import MandatoryKeys,checkMandatoryKeys
from argsparser import parse_argument
from fileio import readfile,readJson,writeFile
from xmlparser import parse_xml_message,wrap_message_attributes,wrap_message_root
import logging

logger = logging.getLogger(__name__)

configJsonFilePath="../config.json"

def checkIfMessagesConfiguredAreSupported(messageConfiguration:dict) -> bool:

    supportedMessagesCheckToBeUsed:bool = messageConfiguration.get(mandatoryKeys.supportedMessageTypes).get("check")

    areMessagesSupported:bool = False
    if supportedMessagesCheckToBeUsed == None or supportedMessagesCheckToBeUsed==True:
        logger.debug(f"Checking for supported messages")

        isMessageKeyPresent:bool = checkMandatoryKeys([
            {
                "parent": messageConfiguration.get(mandatoryKeys.supportedMessageTypes),
                "keys": [mandatoryKeys.types]
            }
        ])
        
        logger.debug(f"Checking mandatory keys: {mandatoryKeys.types}")

        if isMessageKeyPresent:

            logger.debug(f"Mandatory keys present")

            supportedMessages:list = list(messageConfiguration[mandatoryKeys.supportedMessageTypes][mandatoryKeys.types])
            configuredMessages:list = list(messageConfiguration[mandatoryKeys.messages].keys())

            areMessagesSupported:bool=True
            areArgsPassedMessagesSupported:bool=True

            for msg in configuredMessages:
                if msg not in supportedMessages:
                    areMessagesSupported=False
            
            for msg in messageTypes:
                if msg not in supportedMessages:
                    areArgsPassedMessagesSupported=False
            
            if not areMessagesSupported or not areArgsPassedMessagesSupported:
                print("Invalid Configuration")
                logger.debug("Invalid Configuration")
                print(f"Supported Messages are: {supportedMessages}")
                logger.debug(f"Supported Messages are: {supportedMessages}")
                print(f"Configured Messages are: {configuredMessages}")
                logger.debug(f"Configured Messages are: {configuredMessages}")
                print(f"Passed Messages are: {messageTypes}")
                logger.debug(f"Passed Messages are: {messageTypes}")
                exit(1)

    return areMessagesSupported
        
def checkConfiguration() -> None:
    global mandatoryKeys
    mandatoryKeys = MandatoryKeys()

    logger.debug(f"Checking mandatory keys: {mandatoryKeys.messageConfig,mandatoryKeys.supportedMessageTypes,mandatoryKeys.messages,mandatoryKeys.delimeter,mandatoryKeys.pattern}")
    keysExist:bool = checkMandatoryKeys([
            {
                "parent": configuration,
                "keys": [mandatoryKeys.messageConfig]
            },
            {
                "parent": configuration.get(mandatoryKeys.messageConfig),
                "keys": [mandatoryKeys.supportedMessageTypes,mandatoryKeys.messages,mandatoryKeys.delimeter]
            },
            {
                "parent": configuration.get(mandatoryKeys.messageConfig).get(mandatoryKeys.delimeter),
                "keys": [mandatoryKeys.pattern]
            } if configuration.get(mandatoryKeys.messageConfig) else None
           
    ])

    if keysExist:
        logger.debug(f"Mandatory keys exist.")
        messageConfiguration:dict = configuration[mandatoryKeys.messageConfig]

        checkIfMessagesConfiguredAreSupported(messageConfiguration)





def filter_messages(content:str,splitFilter:str,identifier:str,delimeter:str=",") -> dict:
    logger.debug("Filtering messages.")
    splittedMessages:[str] = content.split(delimeter)
    
    filteredMessages = {}

    for messageType in messageTypes:
        filteredMessages[messageType] = []


        for message in splittedMessages:
            
            actualMessage:list = message.split(splitFilter)

            if len(actualMessage)>1:
                actualMessage:str = actualMessage[1].strip()
            else:
                actualMessage:str = actualMessage[0].strip()
            
            messageIdentifier = f"<{identifier}>{messageType}</{identifier}>"
            # print(messageIdentifier)

            if  messageIdentifier in actualMessage:
                filteredMessages[messageType].append(actualMessage)
    logger.debug("Messages filtered.")
    
    

    return filteredMessages



def run():
    logger.debug("Inside run function")

    global messageTypes
    global filepath
    global configuration
    global outputFilepath

    filepath=None

    try:
        messageTypes,fileContent,outputFilepath = parse_argument()
        logger.debug(f"{messageTypes=}")
        logger.debug(f"{len(fileContent)=}")
        logger.debug(f"{outputFilepath=}")
    except Exception as e:
        logger.debug(f"Exception in unpacking arguments")
        return
    
    configuration = readJson(configJsonFilePath)
    logger.debug(f"configuration json file read.")

    if fileContent:
        checkConfiguration()

        delimeterObj:dict = configuration.get(mandatoryKeys.messageConfig).get(mandatoryKeys.delimeter)
        
        pattern:str = delimeterObj.get("pattern")
        count:int = delimeterObj.get("count")

        if count==None:
            count=1
        elif count < 1:
            raise Exception(f"delimeter count should be 1 or greater than 1.")
        
        filteredMessages:dict = {}

        for messageType in messageTypes:

            configuredMessages:list = list(configuration[mandatoryKeys.messageConfig][mandatoryKeys.messages].keys())
            
            if messageType not in configuredMessages:
                logger.debug(f"Invalid message type: {messageType}")
                raise Exception(f"Invalid message type: {messageType}")

            jsonMessages:dict = dict(configuration[mandatoryKeys.messageConfig][mandatoryKeys.messages])

            messageObj:dict = jsonMessages.get(messageType)
            executeProcessing:bool = messageObj.get('execute')

            
            if executeProcessing==None or executeProcessing==True:
                logger.debug("Processing message")
                hasSimilarConfig:str = messageObj.get('has-similar-config-to')
                
                parentKeyObjectList:list = []
                messageConfig:dict = {}

                if hasSimilarConfig is not None:
                    logger.debug(f"Message has similar configuration to {hasSimilarConfig}")
                    similarMessageType:str = hasSimilarConfig
                    similarMessageObject:dict = jsonMessages.get(similarMessageType)
                    
                    messageObj=similarMessageObject
                    messageConfig = similarMessageObject.get(mandatoryKeys.configuration)

                    for parentKeyObject in [{
                            "parent": similarMessageObject,
                            "keys": [mandatoryKeys.configuration,mandatoryKeys.filter,mandatoryKeys.messageIdentifierTag]
                    },
                    {
                            "parent": messageConfig,
                            "keys": [mandatoryKeys.identifierPath]
                    }]:
                        parentKeyObjectList.append(parentKeyObject)
                    

                    

                else:
                    messageConfig = messageObj.get(mandatoryKeys.configuration)

                    for parentKeyObject in [{
                            "parent": messageObj,
                            "keys": [mandatoryKeys.configuration,mandatoryKeys.filter,mandatoryKeys.messageIdentifierTag]
                    },{
                            "parent": messageConfig,
                            "keys": [mandatoryKeys.identifierPath]
                    }]:
                        parentKeyObjectList.append(parentKeyObject)

                areKeysPresent:bool = checkMandatoryKeys(parentKeyObjectList)
                logger.debug(f"Checking for mandatory keys: {mandatoryKeys.configuration,mandatoryKeys.filter,mandatoryKeys.identifierPath}")
                if not areKeysPresent:
                    return
                messageIdentifierTag:str = messageObj.get(mandatoryKeys.messageIdentifierTag)
                logger.debug("Mandatory keys are present")
                
                wrapAttributesObj:dict = messageConfig.get('wrap-attributes')
                wrappedMessages:list = None
                
                filteredMessages:dict = filter_messages(content=fileContent, splitFilter=messageObj.get(mandatoryKeys.filter)  ,delimeter=pattern*count,identifier=messageIdentifierTag)
                
                messages:list = filteredMessages[messageType]

               

                if wrapAttributesObj:
                    
                    executeWrapMessageAttribute:bool = wrapAttributesObj.get('execute')

                    if executeWrapMessageAttribute==None or executeWrapMessageAttribute==True:
                        logger.debug("Wrapping attributes")    

                        areKeysPresent:bool = checkMandatoryKeys([
                                {
                                    "parent": wrapAttributesObj,
                                    "keys": [mandatoryKeys.attributes]
                                }
                        ])

                        logger.debug(f"Checking mandatory keys: {mandatoryKeys.attributes}")

                        if areKeysPresent:
                            logger.debug(f"Mandatory keys present")
                            attributeConfigurations:list = wrapAttributesObj.get(mandatoryKeys.attributes)                            
                            wrappedMessages:list = wrap_message_attributes(messages,attributeConfigurations)
                        

                           
                if wrappedMessages:
                    messages=wrappedMessages

                for i,message in enumerate(messages):
                    # print(i)
                    wrapMessageRootElementWith:str = messageConfig.get("wrap-root-element-with")

                    if wrapMessageRootElementWith:
                        message = wrap_message_root(wrapperElement=wrapMessageRootElementWith,message=message)

                    identifierPath:list = messageConfig.get(mandatoryKeys.identifierPath)

                    parsedMessage,identifierValue = parse_xml_message(messageType,message,identifierPath)
                    
                    if identifierValue:
                        writeFile(filepath=f"{outputFilepath}/{messageType}_{identifierValue}.xml",content=parsedMessage)
               

def main():
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(filename='../logs/logs.log',format=FORMAT,level=logging.DEBUG)
    logger.debug("Started with message processing.")
    print("Started with message processing.")
    run()
    logger.debug("Finished with message processing.")
    print("Finished with message processing.")

if __name__ == "__main__":
    main()