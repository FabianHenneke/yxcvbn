#!/usr/bin/env python3
import sys

def usage():
    return '''
This script converts surname/name data from the US 1990 census into a format zxcvbn
recognizes. To use, first obtain the census files:

https://www2.census.gov/topics/genealogy/1990surnames

download dist.all.last, dist.female.first and dist.male.first

Then run:

%s dist.all.lst      ../data/surnames.txt
%s dist.female.first ../data/female_names.txt
%s dist.male.names   ../data/male_names.txt

for each file.
''' % [sys.argv[0]] * 3

def main(input_filename, output_filename):
    with open(output_filename, 'w', encoding='utf8') as f:
        for line in open(input_filename, 'r', encoding='utf8'):
            if line.strip():
                name = line.split()[0].lower()
                f.write(name+'\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(usage())
    else:
        main(*sys.argv[1:])
    sys.exit(0)
