# -*- coding: utf-8 -*-

# Filename: gen_sentence_errors.py
# Date Created: 28/06/2020
# Description: Script to generate all possible errors within a single sentence
# Python Version: 3.7

import argparse

from src import config
from src import generate
from src import kana
from src import languages
from src import rules

from src.sorted_tag_database import SortedTagDatabase

import numpy as np

cfg = config.parse()

L_PARAMS = cfg['language_params']
P_PARAMS = cfg['parser_params']
DB_PARAMS = cfg['database_params']

LANG_DIR = 'data/languages'
STDB_DIR = 'data/stdb'
RULE_FILE = 'data/rules.csv'
KANA_FILE = 'data/kana.csv'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Error Generation')

    parser.add_argument(
        '--length_bias', metavar='LENGTH_BIAS',
        type=float, help='Float between -1.0 and 1.0; 1.0 biases \
        towards the least-errored sentences and -1.0 biases towards \
        the most-errored sentences', default=0.0)

    parser.add_argument(
        '--n_show', metavar='N_SHOW',
        type=int, help='number of candidate sentences to show',
        required=False, default=10)

    args = parser.parse_args()

    lang_token_prefix = L_PARAMS['token_prefix']
    lang_syntactic_tag_prefix = L_PARAMS['syntactic_tag_prefix']
    lang_character_prefix = L_PARAMS['character_prefix']

    token_language, tag_languages, character_language = \
        languages.load_languages(LANG_DIR,
                                 lang_token_prefix,
                                 lang_syntactic_tag_prefix,
                                 lang_character_prefix)

    unk_token = token_language.unknown_token

    STDB = SortedTagDatabase(STDB_DIR,
                             DB_PARAMS['unique_token_prefix'],
                             DB_PARAMS['unique_syntactic_tag_prefix'],
                             DB_PARAMS['unique_form_prefix'],
                             DB_PARAMS['sort_tag_prefix'],
                             DB_PARAMS['sort_form_prefix'])

    KL = kana.KanaList(KANA_FILE)

    RL = rules.RuleList(RULE_FILE, character_language, token_language,
                        tag_languages, KL=KL)

    print('\nBeginning data synthesis')
    print(cfg['BREAK_LINE'])

    RS = np.random.RandomState(seed=0)

    valid = True

    while valid:

        sentence = input('Please enter a sentence: ').strip()
        generate.gen_sentence_errors(
            sentence, STDB, token_language, tag_languages, RL,
            n_show=args.n_show, bias=args.length_bias)

        cont = ''

        while cont != 'n' and cont != 'y':

            cont = input('\nContinue synthesis? (y / n): ').lower()

            if cont == 'n':
                valid = False
