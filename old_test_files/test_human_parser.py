from nameparser import HumanName

"""
This script is only used to show what HumanName parser is capable of 
and what are the limitations
"""

if __name__ == '__main__':
    print("TEST HUMAN PARSER")

    name_list = ["gaël de léséleuc", "Sir de Léséleuc", "Miss de Léséleuc", "Sir",
                 "Alexandre", "Duval", "Alexandre Duval", "Mister Duval",
                 "mr Alexandre Duval", "Mr. Alexandre Duval", "Brother"]

    for name in name_list:
        print(name, "is parsed to", HumanName(name).as_dict())


