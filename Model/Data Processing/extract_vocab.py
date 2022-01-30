#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import argparse

number_words = set(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
                    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand"])

if __name__ == '__main__':
    readme = """
    """
    # parser = argparse.ArgumentParser(description=readme)
    # parser.add_argument("-t", '--table', dest = 'table', help = "table data")
    # parser.add_argument("-s", '--summary', dest = 'summary', help = "summary data")
    # args = parser.parse_args()

    if True:
        table_vocab = {}
        for line in open("valid.gtable", 'r', encoding="utf-8"):
            items = line.strip().split()
            for item in items:
                elements = item.split('|')
                assert len(elements) == 4
                for element in elements:
                    if element not in table_vocab: table_vocab[element] = 1
                    else: table_vocab[element] += 1

        sorted_table_vocab = sorted(table_vocab.items(), key = lambda x:x[1], reverse=True)
        table_outf = open("valid.gtable_vocab", 'w', encoding="utf-8")
        for (w, c) in sorted_table_vocab:
            table_outf.write("{}\t{}\n".format(w, c))
        table_outf.close()

    if True:
        summary_word_count = {}
        for line in open("valid.summary", 'r', encoding="utf-8"):
            words = line.strip().split()
            for w in words:
                # if w in table_vocab: continue
                if w not in summary_word_count:
                    summary_word_count[w] = 1
                else:
                    summary_word_count[w] += 1

        sorted_summary_word_count = sorted(summary_word_count.items(), key = lambda x:x[1], reverse=True)
        summary_outf = open("valid.summary_vocab", 'w', encoding="utf-8")
        # for (w, c) in sorted_table_vocab:
        #     summary_outf.write("{}\t{}\n".format(w, c))
        for (w, c) in sorted_summary_word_count:
            summary_outf.write("{}\t{}\n".format(w, c))
        summary_outf.close()