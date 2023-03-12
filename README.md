# OpcuaToJson

## Installation 

```
sudo apt install python3-venv
python3 -m venv ./env
source ./env/bin/activate
pip install opcua jsonpath_ng cryptography

```

## Run

- Convert an OPCUA folder of nodes to a JSON file
- Subscribe to each variable and update JSON file


```

source ./env/bin/activate
python OpcuaToJson.py -u opc.tcp://MacBook-Air-M1.local:53530/OPCUA/SimulationServer -p "Root/Objects/Simulation" -o ./export_opcua.json -d 2

```
