from opcua import Client
from opcua import ua
from opcua import Node
import logging
import argparse
import json
import time
from jsonpath_ng  import jsonpath, parse

json_opcua_mapping = {}
json_result = {}
        

def get_node_path_display_name(node: Node):
    return '/'.join(node.get_display_name().Text for node in node.get_path(200000))

def getOpcuaToJson(node: Node, rep, sub, json_opcua_mapping):
    json_result = {}

    children = node.get_children()
    
    for child in children:
        itemName = child.get_display_name().Text
        child_class = child.get_node_class()
        path = get_node_path_display_name(child)
        if ( 
                  (len(path) <= len(rep) and rep.startswith(path))
               or (len(path) > len(rep) and path.startswith(rep))
            ):

                json_opcua_mapping[child] = path.replace("/",".")
                if child_class == ua.NodeClass.Variable:
                    try:
                        value = child.get_value()
                        display_name = child.get_display_name().Text 
                        sub.subscribe_data_change(child)
                    except:
                        value = ""
                    
                    json_result[itemName]=value
                if child_class == ua.NodeClass.Object:
                    json_child = getOpcuaToJson(child, rep, sub, json_opcua_mapping)
                    json_result[itemName]=json_child
    return json_result

class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another 
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        # print("Python: New data change event", node, val)
        json_path = "$." + json_opcua_mapping[node]
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
        root = client.get_root_node()
        handler = SubHandler()
        sub = client.create_subscription(1000, handler)
        
        # crawl and subscribe
        json_result = {"Root" : getOpcuaToJson(root,  args.opcua_path, sub, json_opcua_mapping)}
        
        # 
        sub.subscribe_events()
        
        while True:
            json_formatted_str = json.dumps(json_result, indent=2)
            print(json_formatted_str)
            args.output
            # Writing to sample.json
            with open(args.output, "w") as outfile:
                outfile.write(json_formatted_str)
            time.sleep(int(args.opcua_delay_s))
    finally:
            client.disconnect()
            print(json_opcua_mapping)
