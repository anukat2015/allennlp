# pylint: disable=invalid-name,no-self-use
import argparse
from typing import Iterator

from allennlp.common import Params
from allennlp.common.testing import AllenNlpTestCase
from allennlp.commands.train import Train, train_model, train_model_from_args
from allennlp.data import DatasetReader, Instance, InstanceCollection
from allennlp.data.dataset import LazyDataset

class TestTrain(AllenNlpTestCase):
    def test_train_model(self):
        params = Params({
                "model": {
                        "type": "simple_tagger",
                        "text_field_embedder": {
                                "tokens": {
                                        "type": "embedding",
                                        "embedding_dim": 5
                                }
                        },
                        "stacked_encoder": {
                                "type": "lstm",
                                "input_size": 5,
                                "hidden_size": 7,
                                "num_layers": 2
                        }
                },
                "dataset_reader": {"type": "sequence_tagging"},
                "train_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "validation_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "iterator": {"type": "basic", "batch_size": 2},
                "trainer": {
                        "num_epochs": 2,
                        "optimizer": "adam"
                }
        })

        train_model(params, serialization_dir=self.TEST_DIR)

    def test_train_with_test_set(self):
        params = Params({
                "model": {
                        "type": "simple_tagger",
                        "text_field_embedder": {
                                "tokens": {
                                        "type": "embedding",
                                        "embedding_dim": 5
                                }
                        },
                        "stacked_encoder": {
                                "type": "lstm",
                                "input_size": 5,
                                "hidden_size": 7,
                                "num_layers": 2
                        }
                },
                "dataset_reader": {"type": "sequence_tagging"},
                "train_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "test_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "validation_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "evaluate_on_test": True,
                "iterator": {"type": "basic", "batch_size": 2},
                "trainer": {
                        "num_epochs": 2,
                        "optimizer": "adam"
                }
        })

        train_model(params, serialization_dir=self.TEST_DIR)

    def test_train_args(self):
        parser = argparse.ArgumentParser(description="Testing")
        subparsers = parser.add_subparsers(title='Commands', metavar='')
        Train().add_subparser('train', subparsers)

        for serialization_arg in ["-s", "--serialization_dir", "--serialization-dir"]:
            raw_args = ["train", "path/to/params", serialization_arg, "serialization_dir"]

            args = parser.parse_args(raw_args)

            assert args.func == train_model_from_args
            assert args.param_path == "path/to/params"
            assert args.serialization_dir == "serialization_dir"

        # config is required
        with self.assertRaises(SystemExit) as cm:  # pylint: disable=invalid-name
            args = parser.parse_args(["train", "-s", "serialization_dir"])
            assert cm.exception.code == 2  # argparse code for incorrect usage

        # serialization dir is required
        with self.assertRaises(SystemExit) as cm:  # pylint: disable=invalid-name
            args = parser.parse_args(["train", "path/to/params"])
            assert cm.exception.code == 2  # argparse code for incorrect usage

@DatasetReader.register('lazy-test')
class LazyFakeReader(DatasetReader):
    # pylint: disable=abstract-method
    def __init__(self) -> None:
        self.reader = DatasetReader.from_params(Params({'type': 'sequence_tagging'}))

    def _generator_for_file(self, file_path: str):
        def generator() -> Iterator[Instance]:
            return (instance for instance in self.reader.read(file_path))

        return generator

    def read(self, file_path: str) -> InstanceCollection:
        """
        Actually reads some data from the `file_path` and returns a :class:`Dataset`.
        """
        return LazyDataset(self._generator_for_file(file_path))

    @classmethod
    def from_params(cls, params: Params) -> 'LazyTestReader':
        return LazyFakeReader()


class TestTrainOnLazyDataset(AllenNlpTestCase):
    def test_train_model(self):
        params = Params({
                "model": {
                        "type": "simple_tagger",
                        "text_field_embedder": {
                                "tokens": {
                                        "type": "embedding",
                                        "embedding_dim": 5
                                }
                        },
                        "stacked_encoder": {
                                "type": "lstm",
                                "input_size": 5,
                                "hidden_size": 7,
                                "num_layers": 2
                        }
                },
                "dataset_reader": {"type": "lazy-test"},
                "train_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "validation_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "iterator": {"type": "lazy-basic", "batch_size": 2},
                "trainer": {
                        "num_epochs": 2,
                        "optimizer": "adam"
                }
        })

        train_model(params, serialization_dir=self.TEST_DIR)

    def test_train_with_test_set(self):
        params = Params({
                "model": {
                        "type": "simple_tagger",
                        "text_field_embedder": {
                                "tokens": {
                                        "type": "embedding",
                                        "embedding_dim": 5
                                }
                        },
                        "stacked_encoder": {
                                "type": "lstm",
                                "input_size": 5,
                                "hidden_size": 7,
                                "num_layers": 2
                        }
                },
                "dataset_reader": {"type": "lazy-test"},
                "train_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "test_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "validation_data_path": 'tests/fixtures/data/sequence_tagging.tsv',
                "evaluate_on_test": True,
                "iterator": {"type": "lazy-basic", "batch_size": 2},
                "trainer": {
                        "num_epochs": 2,
                        "optimizer": "adam"
                }
        })

        train_model(params, serialization_dir=self.TEST_DIR)
