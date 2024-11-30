import json
import requests
from schema import Set, Set_Effect, Effect, Equipment, Weapon, Condition_Group, Condition
from typing import Dict, List

def parse_sets(sets_json):
    set_items = [None] * len(sets_json)
    for k,set in enumerate(sets_json['sets']):
        set_boni = [None] * len(set['effects'])
        for i,seteff in enumerate(set['effects']):
            partial_setbonus = [None] * len(seteff) 
            for j, stat in enumerate(seteff):
                partial_setbonus[j] = Effect(
                    name = stat['type']['name'],
                    int_minimum = stat['int_minimum']
                )
            set_boni[i] = Set_Effect(
                n_parts = j+2,
                stats = partial_setbonus
            )
        set_items[k] = Set(
            name = set['name'],
            set_bonus = set_boni               
        )
    return set_items

def condition_group_list_builder(tree_json, is_top_level = True):
    if tree_json.get('is_operand', False):
        new_condition = Condition(
            relation = tree_json['condition']['operator'],
            characteristic = tree_json['condition']['element']['name'],
            value = tree_json['condition']['int_value']
        )
        return [[new_condition]]

    condition_group_list = []
    for child in tree_json.get('children', []):
        child_conditions = condition_group_list_builder(child, is_top_level = False)
        if tree_json['relation'] == 'and':
            if not condition_group_list:
                condition_group_list = child_conditions
            else:
                condition_group_list = [ x+y for x in condition_group_list for y in child_conditions]
        elif tree_json['relation'] == 'or':
            condition_group_list.extend(child_conditions)

    if is_top_level:
        return [Condition_Group(conditions = group) for group in condition_group_list]
    
    return condition_group_list

def parse_equipment(equipment_json):
    equipment_items = [None] * len(equipment_json)
    for k,item in enumerate(equipment_json['items']):
        equipment_stats = []
        weapon_attack_stats = []
        condition_groups = condition_group_list_builder(item.get('condition_tree'))    # change to conditions on 3.0 release
        for eff in item['effects']:
            if eff['type']['name'] == '-special spell-':
                special_spell = eff['formatted']
            else:
                special_spell = None
            if eff['ignore_int_max']:
                maxval = None
            else:
                maxval = eff['int_maximum']
            new_eff = Effect(
                name = eff['type']['name'],
                int_minimum = eff['int_minimum'],
                int_maximum = maxval
            )
            if not eff['type']['is_active']:
                equipment_stats.append(new_eff)
            else:
                weapon_attack_stats.append(new_eff)
        if item['is_weapon']:
            new_item = Weapon(
                name = item['name'],
                level = item['level'],
                type = 'Weapon',
                condition_groups = condition_groups,
                combat_effect = special_spell,
                stats = equipment_stats,
                attack_effect = weapon_attack_stats,
                critical_chance = item['critical_hit_probability'],
                critical_effect = item['critical_hit_bonus'],
                attack_cost = item['ap_cost'],
                hits_per_turn = item['max_cast_per_turn'],
                range_min = item['range']['min'],
                range_max = item['range']['max']
            )
        else:
            new_item = Equipment(
                name = item['name'],
                level = item['level'],
                type = item['type']['name'],
                conditions = condition_groups,
                combat_effect = special_spell,
                stats = equipment_stats,
            )
        equipment_items[k] = new_item
    return equipment_items


if __name__ == '__main__':
    set_test_data = requests.get('https://api.dofusdu.de/dofus2/en/sets?sort%5Blevel%5D=asc&filter%5Bmin_highest_equipment_level%5D=190&filter%5Bmax_highest_equipment_level%5D=200&page%5Bsize%5D=1&page%5Bnumber%5D=1&fields%5Bset%5D=effects,equipment_ids')
    #print(json.dumps(set_test_data.json(), indent=3), '\n \n')
    #print(parse_sets(set_test_data.json()))
    equipment_test_data = requests.get('https://api.dofusdu.de/dofus2/en/items/equipment?sort%5Blevel%5D=desc&filter%5Btype_name%5D=sword&filter%5Bmin_level%5D=10&filter%5Bmax_level%5D=200&page%5Bsize%5D=1&page%5Bnumber%5D=1&fields%5Bitem%5D=description,conditions,effects,is_weapon,parent_set,critical_hit_probability,critical_hit_bonus,is_two_handed,max_cast_per_turn,ap_cost,range&filter%5Btype_enum%5D=sword')
    print(json.dumps(equipment_test_data.json(), indent = 3), '\n \n')
    print(parse_equipment(equipment_test_data.json()))


