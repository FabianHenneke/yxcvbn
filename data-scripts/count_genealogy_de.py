#!/usr/bin/env python3

import os
import sys
import operator
import re

def usage():
    return '''
This script extracts common German surnames from phone book data collected in 2002. To use, first
download, as .html files, the following three wiki pages (each batch contains 1000 names):

http://wiki-de.genealogy.net/Die_1000_h%C3%A4ufigsten_Familiennamen_in_Deutschland
http://wiki-de.genealogy.net/Die_2000_h%C3%A4ufigsten_Familiennamen_in_Deutschland
http://wiki-de.genealogy.net/Die_3000_h%C3%A4ufigsten_Familiennamen_in_Deutschland

Put those into a single directory and point it to this script:

%s genealogy_de_html_dir ../data/german_surnames.txt

german_surnames.txt will include one line per name, ordered by rank.
...
    ''' % sys.argv[0]

EXTRACT_RANK_AND_TOKEN_RE = re.compile(r'>([\s\d.]*)<a[^>]*\(Familienname\)[^>]*>([\w\s]+)</a>')

HAS_UMLAUTS_RE = re.compile(r'[äöüß]')

def parse_wiki_tokens(html_doc_str):
    results = []
    num_tokens = 0

    for rank_and_token_match in EXTRACT_RANK_AND_TOKEN_RE.finditer(html_doc_str):
        num_tokens += 1
        rank_match = rank_and_token_match.group(1)
        if rank_match:
            rank = int(rank_match.replace('.', ''))
        else:
            rank = num_tokens
        token = rank_and_token_match.group(2)
        new_records = [(normalized, rank) for normalized in resolve_umlauts(token)]
        results.extend(new_records)

    # Each batch has 1000 entries.
    assert 1000 == num_tokens
    return results

def resolve_umlauts(token):
    normalized = token.lower().replace(' ', '')
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


def main(genealogy_de_html_root, output_filename):
    token_rank = [] # list of pairs
    for filename in os.listdir(genealogy_de_html_root):
        path = os.path.join(genealogy_de_html_root, filename)
        with open(path, 'r', encoding='utf8') as f:
            token_rank.extend(parse_wiki_tokens(f.read()))
    token_rank.sort(key=operator.itemgetter(1))
    with open(output_filename, 'w', encoding='utf8') as f:
        for surname, _ in token_rank:
            f.write('{}\n'.format(surname))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(usage())
    else:
        main(*sys.argv[1:])
    sys.exit(0)
