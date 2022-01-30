# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from logging import getLogger
import os
import numpy as np
import torch

from .dataset import Dataset, ParallelDataset,TableDataset 
from .dictionary import BOS_WORD, EOS_WORD, PAD_WORD, UNK_WORD, MASK_WORD

logger = getLogger()

def process_binarized(data, params):
    """
    Process a binarized dataset and log main statistics.
    """
    dico = data['dico']
    assert ((data['sentences'].dtype == np.uint16) and (len(dico) < 1 << 16) or
            (data['sentences'].dtype == np.int32) and (1 << 16 <= len(dico) < 1 << 31))
    logger.info("%i words (%i unique) in %i sentences. %i unknown words (%i unique) covering %.2f%% of the data." % (
        len(data['sentences']) - len(data['positions']),
        len(dico), len(data['positions']),
        sum(data['unk_words'].values()), len(data['unk_words']),
        100. * sum(data['unk_words'].values()) / (len(data['sentences']) - len(data['positions']))
    ))
    if (data['sentences'].dtype == np.int32) and (len(dico) < 1 << 16):
        logger.info("Less than 65536 words. Moving data from int32 to uint16 ...")
        data['sentences'] = data['sentences'].astype(np.uint16)
    return data

def load_binarized(path, params):
    """
    Load a binarized dataset.
    """
    assert path.endswith('.pth')
    assert os.path.isfile(path), path
    logger.info("Loading data from %s ..." % path)
    data = torch.load(path)
    # data = process_binarized(data, params)
    return data

def set_dico_parameters(params, dico):
    """
    Update dictionary parameters.
    """
    bos_index = dico.index(BOS_WORD)
    eos_index = dico.index(EOS_WORD)
    pad_index = dico.index(PAD_WORD)
    unk_index = dico.index(UNK_WORD)
    mask_index = dico.index(MASK_WORD)

    if hasattr(params, 'bos_index'):
        assert params.bos_index == bos_index
        assert params.eos_index == eos_index
        assert params.pad_index == pad_index
        assert params.unk_index == unk_index
        assert params.mask_index == mask_index
    else:
        params.bos_index = bos_index
        params.eos_index = eos_index
        params.pad_index = pad_index
        params.unk_index = unk_index
        params.mask_index = mask_index


def load_table_data(data, params, table_path, split):
    """
    Load table data and labels.
    """
    table_data = load_binarized(table_path, params)
    print("Table Data")
    print(table_data)
    set_dico_parameters(params, table_data['dico'])
    if 'source_dico' in data:
        #assert data['source_dico'] == table_data['dico']
        #assert params.src_n_words == len(data['source_dico'])
        print("Valide")
    else:
        data['source_dico'] = table_data['dico']
        params.src_n_words = len(data['source_dico'])
            
    # create ParallelDataset
    dataset = TableDataset(
        table_data['positions'], table_data['table_entities'], table_data['table_types'], 
        table_data['table_values'], table_data['table_feats'], table_data['table_labels'], params
    )

    if 'cs' not in data:
        data['cs'] = {}
    data['cs'][split] = dataset
    logger.info("")

def load_summary_data(data, params, summary_path, split):
    """
    Load summary model.
    """
    summary_data = load_binarized(summary_path, params)
    set_dico_parameters(params, summary_data['dico'])

    if 'target_dico' in data:
        assert data['target_dico'] == summary_data['dico']
        assert params.tgt_n_words == len(data['target_dico'])
    else:
        data['target_dico'] = summary_data['dico']
        params.tgt_n_words = len(data['target_dico'])
            
    # create ParallelDataset
    dataset = Dataset(
        summary_data['positions'], summary_data['summaries'], summary_data['summary_labels'], params
    )

    if 'lm' not in data:
        data['lm'] = {}
    data['lm'][split] = dataset
    logger.info("")

def load_para_data(data, params, table_path, summary_path, split):
    """
    Load parallel data.
    """
    table_data = load_binarized(table_path, params)
    summary_data = load_binarized(summary_path, params)
    set_dico_parameters(params, table_data['dico'])
    set_dico_parameters(params, summary_data['dico'])

    if 'source_dico' in data:
        #assert data['source_dico'] == table_data['dico']
        #assert params.src_n_words == len(data['source_dico'])
        print("Valide")
    else:
        data['source_dico'] = table_data['dico']
        params.src_n_words = len(data['source_dico'])

    if 'target_dico' in data:
        #assert data['target_dico'] == summary_data['dico']
        #assert params.tgt_n_words == len(data['target_dico'])
        print("Valide")
    else:
        data['target_dico'] = summary_data['dico']
        params.tgt_n_words = len(data['target_dico'])

    # create ParallelDataset
    dataset = ParallelDataset(
        table_data['positions'], table_data['table_entities'], table_data['table_types'], 
        table_data['table_values'], table_data['table_feats'], table_data['table_labels'],
        summary_data['positions'], summary_data['summaries'], summary_data['summary_labels'],
        params
    )
    
    dataset.remove_empty_sentences()
    return dataset

def load_data(params):
    """
    Load monolingual data.
    The returned dictionary contains:
        - dico (dictionary)
        - vocab (FloatTensor)
        - train / valid / test (monolingual datasets)
    """
    data = {}

    # monolingual data summary
    logger.info('============ Data summary ============')
    if params.cs_step:
        load_table_data(data, params, params.train_cs_table_path, 'train')
        cs_data_set = data['cs']['train']
        logger.info('{: <18} - {: >10}'.format('Content-Selection Data', len(cs_data_set)))

    # parallel datasets
    if params.sm_step:
        dataset = load_para_data(data, params, params.train_sm_table_path, params.train_sm_summary_path, 'train')
        if params.sm_step:
            if 'sm' not in data:
                data['sm'] = {}
            data['sm']['train'] = dataset

        logger.info('{: <18} - {: >10}'.format('Para Data', len(dataset)))

    # generic language text
    if params.lm_step:
        load_summary_data(data, params, params.train_sm_summary_path, 'train')
        lm_data_set = data['lm']['train']
        logger.info('{: <18} - {: >10}'.format('Language model Data', len(lm_data_set)))

    if params.eval_bleu:
        dataset = load_para_data(data, params, params.valid_table_path, params.valid_summary_path, 'valid')
        if params.sm_step:
            if 'sm' not in data:
                data['sm'] = {}
                print("yes 1")
            data['sm']['valid'] = dataset
    elif params.eval_cs:
        load_table_data(data, params, params.valid_table_path, 'valid')
        cs_data_set = data['cs']['valid']
        logger.info('{: <18} - {: >10}'.format('Content-Selection Data', len(cs_data_set)))

    logger.info("")
    return data
