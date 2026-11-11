# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack v3.4 contents
#Generation tool, datapack design, and resourcepack design by link2_thepast

from src.contents.datapack.v3.v3p3 import DatapackContents_v3p3

creeper_normal_entries = [
    {
        'type': 'minecraft:item',
        'modifier': [
            {
                'type': 'minecraft:set_count',
                'count': {'type': 'minecraft:uniform', 'max': 2, 'min': 0}
            },
            {
                'type': 'minecraft:enchanted_count_increase',
                'count': {'type': 'minecraft:uniform', 'max': 1.0, 'min': 0.0},
                'enchantment': 'minecraft:looting'
            }
        ],
        'name': 'minecraft:gunpowder'
    }
]

# vanilla discs: stays inline in creeper.json (not formatted by the generator)
creeper_vanilla_discs_entry = {
    'type': 'minecraft:tag',
    'weight': 1,
    'items': '#minecraft:creeper_drop_music_discs',
    'expand': True
}

# one per custom disc; these end up in music_discs.json
custom_disc_entry = {
    'type': 'minecraft:item',
    'weight': 1,
    'name': 'minecraft:music_disc_11',
    'modifier': [{
        'type': 'minecraft:set_components',
        'components': {
            'minecraft:item_model': '{pack_name}:{entry.internal_name}',
            'minecraft:jukebox_playable': '{pack_name}:{entry.internal_name}'
        }
    }]
}

# entries of the second pool are set by get_creeper_json
creeper_json = {
    'path': ['data', 'minecraft', 'loot_table', 'entities', 'creeper.json'],
    'repeat': 'single',
    'format_contents': False,
    'contents': {
        'type': 'minecraft:entity',
        'pools': [
            {'rolls': 1, 'entries': creeper_normal_entries},
            {'rolls': 1, 'entries': [], 'condition': {
                'type': 'minecraft:entity_properties',
                'entity': 'attacker',
                'predicate': {'minecraft:entity_type': '#minecraft:skeletons'}
            }}
        ],
        'random_sequence': 'minecraft:entities/creeper'
    }
}

class DatapackContents_v3p4(DatapackContents_v3p3):
    min_pack_format = 121
    max_pack_format = 999
    version_major = 3
    version_minor = 4

    def add_contents(self):
        super().add_contents()

    #creeper.json and music_discs.json
    def get_creeper_vanilla_discs_entry(self):
        return creeper_vanilla_discs_entry

    def get_custom_disc_entry(self):
        return custom_disc_entry

    def get_creeper_json(self, custom_discs_ref_entry: dict):
        creeper_json['contents']['pools'][1]['entries'] = [
            self.get_creeper_vanilla_discs_entry(),
            custom_discs_ref_entry
        ]
        return creeper_json
