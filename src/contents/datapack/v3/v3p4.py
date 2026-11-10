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

creeper_music_entries = []

music_discs_json = {
    'path': ['data', '{pack_name}', 'loot_table', 'music_discs.json'],
    'repeat': 'single',
    'format_contents': False,
    'contents': {
        'type': 'minecraft:generic',
        'pools': [{'rolls': 1, 'entries': []}]
    }
}

# vanilla discs, stays inside creeper.json (not formatted by the generator)
creeper_vanilla_discs_entry = {
    'type': 'minecraft:tag',
    'weight': 1,
    'items': '#minecraft:creeper_drop_music_discs',
    'expand': True
}

# appended once by the generator; reference to the custom disc table
creeper_music_entry_base = {
    'type': 'minecraft:loot_table',
    'weight': '(int){dp_num_discs}',
    'value': '{pack_name}:music_discs'
}

# appended to chest loot tables by the generator
chest_music_entry_base = {
    'entries': [
        {
            'type': 'minecraft:loot_table',
            'value': '{pack_name}:music_discs'
        }
    ],
    'rolls': 1
}

# appended once per disc; these end up in music_discs.json
creeper_music_entry_custom = {
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

creeper_json = {
    'path': ['data', 'minecraft', 'loot_table', 'entities', 'creeper.json'],
    'repeat': 'single',
    'format_contents': False,
    'contents': {
        'type': 'minecraft:entity',
        'pools': [
            {'rolls': 1, 'entries': creeper_normal_entries},
            {'rolls': 1, 'entries': creeper_music_entries, 'condition': {
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
        self.music_discs = music_discs_json

    def get_creeper_music_entry_base(self):
        return creeper_music_entry_base

    def get_chest_music_entry_base(self):
        return chest_music_entry_base

    def get_creeper_music_entry_custom(self):
        return creeper_music_entry_custom

    def get_creeper_json(self, creeper_music_entries: list):
        ref, discs = creeper_music_entries[0], creeper_music_entries[1:]
        music_discs_json['contents']['pools'][0]['entries'] = discs
        creeper_json['contents']['pools'][1]['entries'] = [creeper_vanilla_discs_entry, ref]
        return creeper_json
