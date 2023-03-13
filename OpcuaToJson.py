from opcua import Client
from opcua import ua
from opcua import Node
import logging
import argparse
import json
import time
from jsonpath_ng  import jsonpath, parse

jsonOpcuaMapping = {}
json_result = {}
        

def get_node_path_display_name(node: Node):
    return '/'.join(node.get_display_name().Text for node in node.get_path(200000))

def getOpcuaToJson(parentNode: Node, prefixPath, opcuaSubscription, jsonOpcuaMapping):
    resultJSON = {}

    for childNode in parentNode.get_children():
        itemName = childNode.get_display_name().Text
        childNodeClass = childNode.get_node_class()
        childPath = get_node_path_display_name(childNode)
        
        # if the current crawled path starts with the correct prefix
        if ( 
                  (len(childPath) <= len(prefixPath) and prefixPath.startswith(childPath))
               or (len(childPath) > len(prefixPath) and childPath.startswith(prefixPath))
            ):

                # store in dict node -> jsonpath
                jsonOpcuaMapping[childNode] = childPath.replace("/",".")
                
                # this is a variable : save the value
                if childNodeClass == ua.NodeClass.Variable:
                    try:
                        value = childNode.get_value()
                        display_name = childNode.get_display_name().Text 
                        opcuaSubscription.subscribe_data_change(childNode)
                    except:
                        value = ""  
                    resultJSON[itemName]=value
                
                # this is an object : get the content recursively
                if childNodeClass == ua.NodeClass.Object:
                    jsonChild = getOpcuaToJson(childNode, prefixPath, opcuaSubscription, jsonOpcuaMapping)
                    resultJSON[itemName]=jsonChild
                    
    return resultJSON

class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another 
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        # print("Python: New data change event", node, val)
        json_path = "$." + jsonOpcuaMapping[node]
        jsonpath_expression = parse(json_path)
        jsonpath_expression.update(json_result, val)
        return

    def event_notification(self, event):
        # print("Python: New event", event)
        return


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--opcua", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("-p", "--opcua_path", required=True)
    parser.add_argument("-d", "--opcua_delay_s", required=True)
    args = parser.parse_args()
    
    client = Client(args.opcua)
    try:
        client.connect()
        client.load_type_definitions()  # load definition of server specific structures/extension objects
        root    = client.get_root_node()
        handler = SubHandler()
        sub     = client.create_subscription(1000, handler)
        
        # crawl and subscribe
        json_result = {"Root" : getOpcuaToJson(root,  args.opcua_path, sub, jsonOpcuaMapping)}
        
        # 
        sub.subscribe_events()
        
        while True:
            json_formatted_str = json.dumps(json_result, indent=2)
            print(json_formatted_str)
            # Writing to sample.json
            with open(args.output, "w") as outfile:
                outfile.write(json_formatted_str)
            time.sleep(int(args.opcua_delay_s))
    finally:
            client.disconnect()
            print(jsonOpcuaMapping)
