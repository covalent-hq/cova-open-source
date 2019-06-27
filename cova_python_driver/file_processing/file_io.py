import json

def read_data(path):
    try:
        with open(path, "rb") as fileRead:
            data  = fileRead.read()
            return data
    
    except:
        raise ValueError("Invalide File Path")

def read_routing_nodes_cred(path):
    lines = None

    with open(path, "r") as fileRead:
        lines = fileRead.read()
    
    routing_nodes_info = json.loads(lines)

#     for value in routing_nodes_info.itervalues():
#             routing_nodes.append(value)

#     print("routing_nodes",routing_nodes)
    return routing_nodes_info

def read_routing_nodes_cred_processed(path):
    routing_nodes_info = read_routing_nodes_cred(path)
    routing_nodes = list()

    for value in routing_nodes_info.itervalues():
            routing_nodes.append(value)

    return routing_nodes

def read_json_config_file(path): 
    data = None
    
    with open(path, "r") as fileRead:
        data = fileRead.read()

    return json.loads(data)

def get_routing_node_address(path):
    routing_nodes = read_routing_nodes_cred(path)

    if len(routing_nodes) == 0 :
            raise ValueError("Routing nodes must be greater than 0")

    nodes = routing_nodes[0]
    address_with_port = str(nodes["public_ip"])
    address = address_with_port.split(':')
    address += ":"

    return address


