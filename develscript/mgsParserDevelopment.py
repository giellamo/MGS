import pyparsing as pp
import jinja2 as j2
import sys 

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 2:
        print ("Usage: %s <in idl file> " % sys.argv[0])
        sys.exit(0)
        
    _lcurl = pp.Suppress('{')
    _rcurl = pp.Suppress('}')
    _lquad = pp.Suppress('[')
    _rquad = pp.Suppress(']')
    _equal = pp.Suppress('=')
    _comma = pp.Suppress(',')
    _attributeIntroducer = pp.Suppress('@')
    _semicolon = pp.Suppress(';')
    identifier = pp.Word(pp.alphas,pp.alphanums+'_')
    attributes = _attributeIntroducer +identifier('attribute')
    integer = pp.Word(pp.nums)
    
    _enum = pp.Suppress('enum')
    enumValue = pp.Group(identifier('name') + pp.Optional(_equal + integer('value')))
    enumList = pp.Group(enumValue + pp.ZeroOrMore(_comma + enumValue))
    enum = _enum + identifier('enum') + _lcurl + enumList('list') + _rcurl
    
    _message = pp.Suppress(pp.Keyword('message'))
    messageValue = pp.Group(pp.Optional(identifier('mod')) + identifier('type') + identifier('name') + _semicolon)
    messageValue2 = pp.Group(identifier('type') + identifier('name') + _semicolon)
    messageValue3 = pp.Group(identifier('type') + _lquad + integer + _rquad+identifier('name') + _semicolon).setResultsName("Vector")
    messageList = pp.ZeroOrMore(messageValue | messageValue2 | messageValue3).setResultsName("MessageList")
    message = (_message + identifier('message')  + _lcurl + messageList + _rcurl)
        
    _messageHeader = pp.Keyword('messageHeader')
    messageHeader = _messageHeader + _lcurl + messageList + _rcurl
    
    parseTree =  attributes | message | messageHeader | enum 
    
    idlString = ""
    with open(sys.argv[1], 'r') as idlFile:
        idlString=idlFile.read()
###
    messageTemplate = j2.Template("class {{ message }} \n{\n{% for user in fields %}    {{ user[0] }} {{ user[1] }} {{ user[2] }};\n{% endfor %}  public:\n{% for user in fields %}    {{ user[0] }} {{ user[1] }} get{{ user[2]|capitalize }}();\n{% endfor %}}")
    
    enumTemplate = j2.Template('enum {{enum}}\n{\n}')
###
    for result, start, end in parseTree.scanString(idlString):
      print ("***\nFound {0} at [{1}:{2}]\n\n".format(result, start, end))
      resDict = result.asDict()
      print (resDict)
      try:
        if  result.message != '' :
            print ( messageTemplate.render(message=result.message, fields=resDict['MessageList']))
            print ("\n messageList: "  )
            print (resDict['MessageList'])
        elif result.enum != '':
            print ( enumTemplate.render(enum=result.enum))
            print ("\n enumList: "  )
            print (resDict['list'])
        elif result.messageHeader != '' :
            print (" Header: " + result.messageHeader)
            
            
      except:
        print (" Err")
        pass
      print ("\n***\n")
      
  
