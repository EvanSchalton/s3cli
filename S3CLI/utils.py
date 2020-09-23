import json

def loadConfig(configPath):
    with open(configPath) as inConfig:
        return json.load(inConfig)

def convertbyte(b:int, unit:str='byte'):
    unit = unit.lower()

    conversion = {
        'byte':0,
        'kb':1,
        'mb':2,
        'gb':3,
        'tb':4
    }

    conversionVal = conversion.get(unit, 'byte')

    return round(
        b*(.001**conversionVal), conversionVal)