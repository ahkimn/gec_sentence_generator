# -*- coding: utf-8 -*-

# Filename: generate.py
# Date Created: 19/12/2019
# Description: Functions to generate parallel synthetic data
# Python Version: 3.7

import numpy as np
import math

from . import config
from . import languages
from . import parse
from . import util
from termcolor import colored

from .rules import CharacterRule, RuleList
from .sorted_tag_database import SortedTagDatabase

cfg = config.parse()

P_PARAMS = cfg['parser_params']


def gen_sentence_errors(sentence: str, stdb: SortedTagDatabase,
                        token_language: languages.Language,
                        tag_languages: list, rl: RuleList,
                        n_show=10, bias=0.5):

    delimiter = P_PARAMS['delimiter']
    parser = parse.default_parser()

    tokens, tags = parse.parse_full(
        sentence, parser, remove_delimiter=False,
        delimiter=delimiter)

    tokens = token_language.add_nodes(tokens)
    n_tokens = len(tokens)
    _temp = list()

    for j in range(len(tag_languages)):

        _temp.append(tag_languages[j].add_nodes(tags[j]))

    tags = np.vstack(_temp).swapaxes(0, 1)
    tags = tags[np.newaxis, ...]

    correct = \
        token_language.parse_indices(
            tokens).split(',')

    SG = SentenceGen(correct)

    for rule, idx in rl.iterate_rules('-1'):

        if isinstance(rule, CharacterRule):
            continue

        if n_tokens < rule.n_correct_tokens:
            continue

        match_array = np.ones((
            1, n_tokens - rule.n_correct_tokens + 1),
            dtype=np.bool)

        # Iterate over each syntactic tag index, restricting
        #   possible matches by indices with exact matching
        for i in range(rule.n_tags):

            # Syntactic tag matching leniency and tags of index i for
            #   each token
            index_mask = rule.tag_mask[:, i]
            index_tags = rule.correct_tags[:, i]

            # If there is leniency in the syntactic tag
            #    for all tokens, continue
            if np.all(index_mask != 1):

                pass

            else:

                match_array = np.logical_and(
                    match_array, util.search_template(
                        tags[:, :, i], np.argwhere(index_mask == 1),
                        index_tags, rule.n_correct_tokens))

        if np.sum(match_array) == 0:

            continue

        matches = np.argwhere(match_array.reshape(-1))[0]

        n_matches = len(matches)

        correct_tags = np.zeros((n_matches, rule.n_correct_tokens,
                                 tags.shape[2]),
                                dtype=tags.dtype)
        correct_token = np.zeros((n_matches, rule.n_correct_tokens),
                                 dtype=tags.dtype)
        error_tags = np.zeros((n_matches, rule.n_error_tokens,
                               tags.shape[2]),
                              dtype=tags.dtype)
        error_token = np.zeros((n_matches, rule.n_error_tokens),
                               dtype=tags.dtype)

        for i in range(n_matches):

            s = matches[i]
            correct_tags[i, :, :] = \
                tags[i, s:s + rule.n_correct_tokens]
            correct_token[i, :] = \
                tokens[s:s + rule.n_correct_tokens]

        valid_indices = rule.convert_phrases(
            correct_token, correct_tags, error_token, error_tags,
            token_language, tag_languages, stdb)

        for idx in range(n_matches):

            if idx not in valid_indices:

                continue

            original_phrase = list(token_language.parse_index(k) for k in
                                   correct_token[idx])

            generated_phrase = list(token_language.parse_index(k) for k in
                                    error_token[idx])

            last_edit = 0

            for j in range(min(rule.n_error_tokens, rule.n_correct_tokens)):

                if original_phrase[::-1][j] == generated_phrase[::-1][j]:
                    last_edit += 1

                else:
                    break

            # Don't want error phrase equal to correct
            if ''.join(original_phrase) == ''.join(generated_phrase):
                raise ValueError

            len_correct = rule.n_correct_tokens - last_edit
            len_error = rule.n_error_tokens - last_edit

            original_phrase = ''.join(original_phrase[:len_correct])
            generated_phrase = ''.join(generated_phrase[:len_error])

            bounds = [s, s + len_correct]

            SG.add_gen(rule, bounds, original_phrase, generated_phrase)

    c_sentences, e_sentences, sen_rules = SG.gen_all()

    n_created = len(c_sentences)

    if n_created == 0:
        print()
        print('WARNING: No errors generated')
        return

    lengths = [len(k) for k in sen_rules]
    sampler = LengthBiasSampler(lengths)

    perm = sampler.bias_permute(bias)

    start = 0
    iterations = int(n_created / n_show)

    print()
    print('Total pairs generated: %d' % n_created)
    print('\nGenerated pairs: \n')

    for i in range(iterations):

        end = min(start + n_show, n_created)

        for k in perm[start:end]:
            print('C: %s' % c_sentences[k])
            print('E: %s' % e_sentences[k])
            print('R: %s' % ', '.join(sen_rules[k]))
            print()

        show_more = input('Show %d more? (y / n): ' % n_show)
        if show_more == 'n':
            break
        start += n_show

class SentenceGen:

    def __init__(self, correct):

        self.correct = correct
        self.n_tokens = len(self.correct)

        self.rules = list()
        self.phrase_boundaries = list()

        self.correct_phrases = list()
        self.error_phrases = list()

        self.start_dict = dict()
        self.n_errors = 0

    def add_gen(self, rule, bounds, correction, error):

        correct_start = bounds[0]

        if correct_start not in self.start_dict:
            self.start_dict[correct_start] = []

        self.start_dict[correct_start].append(self.n_errors)

        self.rules.append(rule)
        self.phrase_boundaries.append(bounds)

        self.correct_phrases.append(correction)
        self.error_phrases.append(error)

        self.n_errors += 1

    def gen_all(self):

        correct_sentences = ['']
        error_sentences = ['']
        error_rules = []
        error_rules.append([])
        last_modified = [-1]

        for i in range(self.n_tokens):

            for j in range(len(correct_sentences)):

                correct = correct_sentences[j]
                error = error_sentences[j]

                rule_list = error_rules[j]

                if last_modified[j] >= i:
                    continue

                if i not in self.start_dict:
                    if last_modified[j] >= i:
                        continue

                else:
                    for k in self.start_dict[i]:
                        rule = self.rules[k].name
                        bounds = self.phrase_boundaries[k]
                        c_p = self.correct_phrases[k]
                        e_p = self.error_phrases[k]

                        new_correct = correct + colored(c_p, 'green')
                        new_error = error + colored(e_p, 'red')
                        new_list = rule_list[:]
                        new_list.append(rule)

                        correct_sentences.append(new_correct)
                        error_sentences.append(new_error)
                        last_modified.append(bounds[1] - 1)
                        error_rules.append(new_list)

                correct += self.correct[i]
                error += self.correct[i]
                last_modified[j] = i

                correct_sentences[j] = correct
                error_sentences[j] = error

        return correct_sentences, error_sentences, error_rules


class LengthBiasSampler:

    def __init__(self, lengths):

        self.lengths = lengths
        self.min = min(lengths)
        self.max = max(lengths)

        self.n = len(self.lengths)

        r = self.max - self.min
        self.rel_lengths = [((k - self.min) / r) for k in self.lengths]

    def bias_permute(self, bias):

        weights = np.array([math.exp((0.5 - k) * bias)
                            for k in self.rel_lengths])

        weights = weights / np.sum(weights)
        indices = []

        for i in range(self.n):

            j = np.random.choice(self.n, p=weights)
            indices.append(j)
            weights[j] = 0

            if np.sum(weights) == 0:
                break
            weights = weights / np.sum(weights)

        return indices
