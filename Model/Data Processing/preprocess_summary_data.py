#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


"""
Example: python data/vocab.txt data/train.txt
vocab.txt: 1stline=word, 2ndline=count
"""

import os
import numpy as np
import sys
import argparse
import torch

from Model.Train.src.dictionary import Dictionary

def print_args(args):
    print("summary:\t{}".format(args.summary))
    print("summary_label:\t{}".format(args.summary_label))
    print("summary_vocab:\t{}".format(args.summary_vocab))
    print("summary_max_length:\t{}".format(args.summary_max_length))

if __name__ == '__main__':
    readme = ""
    # parser = argparse.ArgumentParser(description=readme)
    # parser.add_argument('--summary', help = "summary data")
    # parser.add_argument('--summary_vocab', help = "summary data vocab")
    # parser.add_argument('--summary_label', help = "summary data label")
    # parser.add_argument('--summary_max_length', type=int, default=600, help = "summmary maximum length")
    # args = parser.parse_args()

    # if args.summary_vocab is None:
    #     args.summary_vocab = args.summary + "_vocab"
    # if args.summary_label is None:
    #     args.summary_label = args.summary + "_label"

    # assert os.path.isfile(args.summary)
    # assert os.path.isfile(args.summary_vocab)
    # assert os.path.isfile(args.summary_label)

    # print_args(args)

    summary_dico = Dictionary.read_vocab("valid.summary_vocab")
    summary_data = Dictionary.index_summary("valid.summary", "valid.summary_label", summary_dico,
                                            "valid.summary.pth", max_len=600)

