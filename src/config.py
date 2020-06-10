# -*- coding: utf-8 -*-

# Filename: config.py
# Date Created: 20/12/2019
# Description: Script to construct default parameters for repository
# Python Version: 3.7

import yaml
import os

HOME_DIR = os.path.expanduser("~")
PROJECT_DIR = os.path.join(
    HOME_DIR, 'Projects/gec_sentence_generator')
CONFIG_FILE = os.path.join(PROJECT_DIR, 'config.yml')


def parse():

    f_config = open(CONFIG_FILE, 'r')
    cfg = yaml.load(f_config, Loader=yaml.SafeLoader)
    f_config.close()

    return cfg


if __name__ == '__main__':

    cfg = dict()

    cfg['language_params'] = {

        'pad_token': '*',
        'pad_index': 0,
        'unknown_token': 'UNK',
        'unknown_index': 1,
        'start_token': 'START',
        'start_index': 2,
        'stop_token': 'STOP',
        'stop_index': 3,
        'index_node': 'in.pkl',
        'node_count': 'nc.pkl',
        'node_index': 'ni.pkl',
        'delimiter': '。',
        'token_prefix': 't',
        'syntactic_tag_prefix': 'st',
        'character_prefix': 'c'
    }

    cfg['database_params'] = {

        'sort_tag_prefix': 'stt',
        'sort_form_prefix': 'stf',
        'unique_token_prefix': 'ut',
        'unique_syntactic_tag_prefix': 'ust',
        'unique_form_prefix': 'uf'
    }

    cfg['parser_params'] = {

        'delimiter': '。',
        'dictionary_dir': '/usr/local/lib/mecab/dic/mecab-ipadic-neologd',
        'parse_indices': [0, 1, 4, 5, 6],
        'parse_labels':
        [
            'part-of-speech',
            'part-of-speech sub-category',
            'inflection',
            'conjugation',
            'root form'
        ]
    }

    cfg['rule_params'] = {

        'class': 'Rule Class',
        'subclass': 'Rule Subclass',
        'name': '#',
        'rule_type': 'Rule Type',
        'type_token': 'Token',
        'type_character': 'Character',
        'syntactic_tags_correct': 'Correct Phrase Syntactic Tags',
        'syntactic_tags_error': 'Error Phrase Syntactic Tags',
        'syntactic_tag_mask': 'Requisite Syntactic Tags',
        'template_correct_phrase': 'Template Correct Phrase',
        'template_error_phrase': 'Template Error Phrase',
        'mapping_inserted': 'Inserted',
        'mapping_modified': 'Modified',
        'mapping_preserved': 'Preserved',
        'mapping_substituted': 'Substituted',
        'mapping_deleted': 'Deleted'
    }

    cfg['seed'] = 23
    cfg['BREAK_LINE'] = '=====================\n'
    cfg['BREAK_SUBLINE'] = '\t=================\n'
    cfg['BREAK_HALFLINE'] = '\t\t=============\n'

    with open(CONFIG_FILE, 'w+') as f_config:
        yaml.dump(cfg, f_config)
