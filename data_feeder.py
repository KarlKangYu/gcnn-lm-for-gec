from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import numpy as np
import codecs
#import sklearn


def read_lm_data(data_path, num_steps):
    lm_in_ids_list, lm_out_ids_list = [], []

    with codecs.open(data_path, "r") as f:
        for line in f.readlines():
            lm_in, lm_out = line.strip().split("#")
            lm_in_ids = lm_in.split()[:num_steps]
            lm_out_ids = lm_out.split()[:num_steps]
            lm_in_ids_list.append(lm_in_ids)
            lm_out_ids_list.append(lm_out_ids)

    return lm_in_ids_list, lm_out_ids_list


def read_phrase_data(data_path, num_steps):
    phrase_ids_list = []

    with codecs.open(data_path, "r") as f:
        for line in f.readlines():
            phrase_ids = line.strip().split()[:num_steps]
            phrase_ids_list.append(phrase_ids)

    return phrase_ids_list


def read_letter_data(data_path, num_steps, max_word_length):
    letter_ids_list = []
    letter_length_list = []

    with codecs.open(data_path, "r") as f:
        for line in f.readlines():
            letters = line.strip().split("#")[:num_steps]
            for letter_ids in letters:
                letter_ids_split = letter_ids.split()[:max_word_length]
                letter_ids_list.append(letter_ids_split + [0]*(max_word_length - len(letter_ids_split)))
                letter_length_list.append(len(letter_ids_split))

    return letter_ids_list, letter_length_list


def read_file(data_path, config, is_train=False):

    mode = "train" if is_train else "dev"

    lm_data_file = os.path.join(data_path, mode + "_in_ids_lm")
    # phrase_file = os.path.join(data_path, mode + "_ids_phrase")
    # letter_file = os.path.join(data_path, mode + "_in_ids_letters")

    # head_mask = config.data_utility.head_mask

    lm_in_data, lm_out_data = read_lm_data(lm_data_file, config.num_steps)

    # lm_in_data: [[<EOS>, in_id_11, in_id_12,...],[<EOS>, in_id_21, in_id_22, ...],....]
    # lm_out_data: [[<EOS>, out_id_11, out_id_12,...],[<EOS>, out_id_21, out_id_22, ...],....]

    # letter_data, letter_length = read_letter_data(letter_file, config.num_steps, config.max_word_length)

    # letter_data: [[char_ids_<EOS>], [<BOW>, char_ids_11], [<BOW>, char_ids_12], ......]
    # phrase_data = read_phrase_data(phrase_file, config.num_steps)
    assert len(lm_in_data) == len(lm_out_data)

    print(mode + " data size: ", len(lm_in_data))

    # phrase_data: [[phrase_id_<EOS>_11, phrase_id_11_12, ...],[phrase_id_<EOS>_21, phrase_id_21_22, ...],....]

    return [lm_in_data, lm_out_data]


def data_iterator(data, config):

    lm_unuesd_num = 1
    # phrase_unused_num = 2

    lm_in_data = data[0]
    lm_out_data = data[1]
    # letter_data = data[2]
    # letter_length = data[3]
    # phrase_data = data[4]
    # head_mask = data[5]

    num_steps = config.num_steps
    max_word_length = config.max_word_length
    batch_size = config.batch_size

    def flatten(lst):
        return [x for item in lst for x in item]

    def maskWeight(letter_num, letter, out_data):
        if letter_num == 1:
            return 10.0
        in_letters_id = letter[1: letter_num]
        in_letters = [config.data_utility.id2token_in_letters[int(id)] for id in in_letters_id]
        in_word = ''.join(in_letters)
        out_word = config.data_utility.id2token_out[int(out_data)]
        return 15.0 if in_word == out_word else 5.0

    while True:

        lm_in_epoch = flatten(lm_in_data)
        lm_out_epoch = flatten(lm_out_data)
        # phrase_epoch = flatten(phrase_data)

        # lm_in_epoch: [<EOS>, in_id_11, in_id_12,.....]
        # lm_out_epoch: [<EOS>, out_id_11, out_id_12,.....]
        # phrase_epoch: [phrase_id_<EOS>_11, phrase_id_11_12, .....]
        # letter_data: [[char_ids_<EOS>, pad, pad,...], [<BOW>, char_ids_11,pad, pad,...], ......]
        # letter_length: [len(word_11), len(word_12), ......]

        batch_length = len(lm_in_epoch) // batch_size
        valid_epoch_range = batch_size * batch_length

        lm_in_epoch = np.reshape(np.array(lm_in_epoch[:valid_epoch_range], dtype=np.int32), [batch_size, -1])
        lm_out_epoch = np.reshape(np.array(lm_out_epoch[:valid_epoch_range], dtype=np.int32), [batch_size, -1])

        # letter_epoch = np.reshape(np.array(letter_data[:valid_epoch_range], dtype=np.int32), [batch_size, -1, max_word_length])
        # letter_length = np.reshape(np.array(letter_length[:valid_epoch_range], dtype=np.int32), [batch_size, -1])
        #
        # phrase_epoch = np.reshape(np.array(phrase_epoch[:valid_epoch_range], dtype=np.int32), [batch_size, -1])
        # phrase_p_epoch = np.zeros_like(phrase_epoch, dtype=np.int32)
        # phrase_p_epoch[phrase_epoch > 1] = 1

        epoch_size = (batch_length - 1) // num_steps

        for i in range(epoch_size):

            lm_epoch_x = lm_in_epoch[:, i * num_steps:(i + 1) * num_steps]
            lm_epoch_y = lm_out_epoch[:, i * num_steps + 1:(i + 1) * num_steps + 1]

            lm_epoch_y_as_a_column = lm_epoch_y.reshape([-1])

            # phrase_logits_mask = np.reshape(np.array([head_mask[id] for id in lm_epoch_y_as_a_column],
            #                                          dtype=np.float32), [batch_size * num_steps, -1])
            #
            # letter_epoch_x = np.reshape(letter_epoch[:, i * num_steps + 1:(i + 1) * num_steps + 1, :], [-1, max_word_length])
            # letter_epoch_y = np.repeat(lm_epoch_y, max_word_length).reshape([-1, max_word_length])
            # letter_length_epoch = np.reshape(letter_length[:, i * num_steps + 1:(i + 1) * num_steps + 1], [-1])
            #
            # letter_mask_epoch = np.array([[1.0] * (length - 1) + [maskWeight(length, letter, word)]
            #                         + [0.0] * (max_word_length - length) if length > 0 else
            #                         [0.0] * max_word_length for (letter, length, word) in
            #                         zip(letter_epoch_x, letter_length_epoch, lm_epoch_y_as_a_column)])
            #
            # unused_letter_mask = (lm_epoch_y < lm_unuesd_num).reshape([-1])
            #
            # letter_mask_epoch[unused_letter_mask == True] = 0.0

            # phrase_p_epoch_y = phrase_p_epoch[:, i * num_steps + 1:(i + 1) * num_steps + 1]
            # phrase_epoch_y = phrase_epoch[:, i * num_steps + 1:(i + 1) * num_steps + 1]

            sequence_lengths = np.array([num_steps] * batch_size, dtype=np.int32)

            lm_mask = np.ones([batch_size, num_steps])
            lm_mask[lm_epoch_y < lm_unuesd_num] = 0.0

            # phrase_p_mask = np.ones([batch_size, num_steps])
            # phrase_p_mask[phrase_epoch_y == 0] = 0.0
            #
            # phrase_mask = np.ones([batch_size, num_steps])
            # phrase_mask[phrase_epoch_y < phrase_unused_num] = 0.0

            data_feed_to_lm_model = (lm_epoch_x, lm_epoch_y, lm_mask, sequence_lengths)
            # print("lm data epoch: lm_epoch_x, lm_epoch_y, lm_mask, sequence_lengths")
            # print(lm_epoch_x, lm_epoch_y, lm_mask, sequence_lengths)

            # data_feed_to_phrase_p = (phrase_p_epoch_y, phrase_p_mask)
            # # print("phrase p data epoch: phrase_p_epoch_y, phrase_p_mask")
            # # print(phrase_p_epoch_y, phrase_p_mask)
            #
            # data_feed_to_phrase = (phrase_epoch_y, phrase_mask, phrase_logits_mask)
            # # print("phrase epoch data: phrase_epoch_y, phrase_mask, phrase_logits_mask")
            # # print(phrase_epoch_y, phrase_mask, phrase_logits_mask)
            #
            # data_feed_to_letter_model = (letter_epoch_x, letter_epoch_y, letter_mask_epoch, letter_length_epoch)
            # # print("letter epoch data: letter_epoch_x, letter_epoch_y, letter_mask_epoch, letter_length_epoch")
            # # print(letter_epoch_x, letter_epoch_y, letter_mask_epoch, letter_length_epoch)

            yield epoch_size, data_feed_to_lm_model
