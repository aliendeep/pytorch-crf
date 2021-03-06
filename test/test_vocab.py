"""Tests for Vocab object."""

import pytest
import torch

from pycrf.nn.utils import assert_equal


def test_labels(vocab):
    """Test that the target label attributes and methods work."""
    assert vocab.n_labels == 3
    assert vocab.labels_stoi["O"] == 0
    assert vocab.labels_itos[0] == "O"
    assert vocab.labels_stoi["B-NAME"] == 1
    assert vocab.labels_itos[1] == "B-NAME"
    assert vocab.labels_stoi["I-NAME"] == 2
    assert vocab.labels_itos[2] == "I-NAME"


def test_chars(vocab):
    """Check to make sure the vocab characters are initialized correctly."""
    assert vocab.chars_stoi[vocab.pad_char] == 0
    assert vocab.chars_stoi[vocab.unk_char] == 1
    assert vocab.chars_itos[0] == vocab.pad_char
    assert vocab.chars_itos[1] == vocab.unk_char
    assert vocab.n_chars == len(vocab.chars_stoi) == len(vocab.chars_itos)
    assert vocab.n_chars < 100


def test_words(vocab):
    """Check to make sure word dicts were initialized correctly."""
    assert vocab.n_words > 10000
    assert vocab.words_itos[vocab.words_stoi["hi"]] == "hi"


cases1 = [
    ["hi", "there"],
    ["hi", "there", "what", "is", "your", "name", "?"],
    ["hi"],
]


@pytest.mark.parametrize("sent", cases1)
def test_sent2tensor(vocab, sent):
    """Check that Vocab.sent2tensor has the correct output format."""
    char_tensors, word_lengths, word_idxs, word_tensors, context = \
        vocab.sent2tensor(sent)

    check_lens = [len(s) for s in sent]
    check_sorted_lens = sorted(check_lens, reverse=True)
    check_idxs = sorted(range(len(sent)), reverse=True, key=lambda i: check_lens[i])

    # Verify sizes.
    assert isinstance(char_tensors, torch.Tensor)
    assert list(char_tensors.size()) == [len(sent), max(check_lens)]
    assert isinstance(word_tensors, torch.Tensor)
    assert list(word_tensors.size()) == [len(sent)]

    # Verify order of word lengths and idxs.
    assert_equal(word_lengths, torch.tensor(check_sorted_lens))
    assert_equal(word_idxs, torch.tensor(check_idxs))

    for i, word_tensor in enumerate(char_tensors):
        check_word = sent[check_idxs[i]]
        check_word_tensor = torch.tensor(
            [vocab.chars_stoi[c] for c in check_word] + [0] * (max(check_lens) - len(check_word))
        )
        assert_equal(word_tensor, check_word_tensor)


cases2 = [
    (["O", "B-NAME", "I-NAME"], False, torch.tensor([0, 1, 2])),
    (["O", "B-FOO", "O"], True, torch.tensor([0, 0, 0])),
]


@pytest.mark.parametrize("labs, is_test, check", cases2)
def test_labs2tensor(vocab, labs, is_test, check):
    res = vocab.labs2tensor(labs, test=is_test)
    assert_equal(res, check)
