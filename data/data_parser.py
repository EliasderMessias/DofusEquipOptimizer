import schema
import json
import requests
from schema import Set, Set_Effect, Effect
from typing import Dict, List

def parse_sets(sets_json):
    set_item = None
    for set in sets_json['sets']:
        #print(json.dumps(sets))
        set_boni = dict.fromkeys((range(len(set['effects']))))
        for i,seteffect in enumerate(set['effects']):
            print(i)
            partial_setbonus = [None] * len(seteffect)  # captures the bonus the set gives for the element 
            for j, stat in enumerate(seteffect):
                print(j)
                partial_setbonus[j] = Effect(
                    name = stat['type']['name'],
                    int_minimum = stat['int_minimum']
                )
            set_boni[i] = (seteffect[0]['item_combination'], partial_setbonus)
        print(set_boni)




if __name__ == '__main__':
    data = requests.get('https://api.dofusdu.de/dofus2/en/sets?sort%5Blevel%5D=asc&filter%5Bmin_highest_equipment_level%5D=190&filter%5Bmax_highest_equipment_level%5D=200&page%5Bsize%5D=20&page%5Bnumber%5D=1&fields%5Bset%5D=effects')
    #print(json.dumps(data.json()), '\n \n')
    parse_sets(data.json())