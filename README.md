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

## Exemple with Prosys Simulation Server

cf : www.prosysopc.com
these variables changes each second

<img width="291" alt="Capture d’écran 2023-03-12 à 21 01 16" src="https://user-images.githubusercontent.com/1449867/224570165-ed06f555-7e4f-4a14-a90f-7aeefabf88e1.png">


<img width="339" alt="Capture d’écran 2023-03-12 à 20 57 38" src="https://user-images.githubusercontent.com/1449867/224569971-9fae87ad-6dd0-4993-83ba-8b8fda603f90.png">
