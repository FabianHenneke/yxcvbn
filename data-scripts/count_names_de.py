#!/usr/bin/env python3

import os
import sys
import operator
import re

def usage():
    return '''
This script extracts given names used in German-speaking countries from the data
file distributed with Jörg Michael's 'gender.c'. To use, first obtain the
program archive '0717-182.zip' from

https://www.heise.de/ct/ftp/07/17/182/

Extract it and run the script as follows:

%s nam_dict.txt ../data/german_given_names.txt

german_given_names.txt will include one or three lines per name, depending on
whether the name contains umlauts:

name1
näme2
name2
naeme2
...
    ''' % sys.argv[0]

HAS_UMLAUTS_RE = re.compile(r'[äöüß]')

def skip_line(line):
    if len(line) != 88 or line[0] == '#':
        return True
    # Skip names repeated because of umlauts
    if line[29] == '+':
        return True
    # Only process names from Germany, Austria or Switzerland
    if line[42] == ' ' and line[43] == ' ' and line[44] == ' ':
        return True
    return False

def extract_name(line):
    full_name = line[3:28].rstrip()
    # Only keep the first part of the name
    first_space = full_name.find(' ')
    if first_space != -1:
        full_name = full_name[:first_space]
    return full_name

def extract_freq(line):
    max_freq = 0
    for i in range(3):
        if line[42 + i] != ' ':
            max_freq = max(max_freq, int(line[42 + i], base=16))
    return max_freq

def normalize(token):
    normalized = token.lower()
    normalized = (normalized
        .replace('é', 'e')
        .replace('è', 'e')
        .replace('ê', 'e')
        .replace('á', 'a')
        .replace('à', 'a')
        .replace('â', 'a'))
    if not HAS_UMLAUTS_RE.search(normalized):
        return [normalized]
    else:
        normalized_ae = (normalized
            .replace('ä', 'ae')
            .replace('ö', 'oe')
            .replace('ü', 'ue')
            .replace('ß', 'ss'))
        normalized_a = (normalized
            .replace('ä', 'a')
            .replace('ö', 'o')
            .replace('ü', 'u')
            .replace('ß', 's'))
        return [normalized, normalized_a, normalized_ae]

def main(nam_dict, output_filename):
    name_freq = [] # list of pairs
    for line in open(nam_dict, 'r', encoding='latin_1'):
        if (skip_line(line)):
            continue
        names = normalize(extract_name(line))
        freq = extract_freq(line)
        name_freq.extend([(name, freq) for name in names])
    name_freq.sort(key=operator.itemgetter(1), reverse=True)
    with open(output_filename, 'w', encoding='utf8') as f:
        prev_name = ''
        for name, freq in name_freq:
            if name != prev_name:
                f.write('{}\n'.format(name))
            prev_name = name

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(usage())
    else:
        main(*sys.argv[1:])
    sys.exit(0)
