from itertools import chain
from typing import List, Generator, Any, Tuple

import spacy
from spacy.lang.en import English

from logger import logger


class StreamSpacyTokenizer:
    """
    Tokenize or lemmatize a list of documents.
    Return list of tokens or lemmas, without sentencizing.
    Works only for English language.
    """

    def __init__(self, disable: list = None, stopwords: list = None, batch_size: int = None,
                 ngram_range: Tuple[int, int] = None, lemmas=False, n_threads: int = None,
                 lowercase: bool = None):
        """
        :param disable: pipeline processors to omit; if nothing should be disabled,
         pass an empty list
        :param stopwords: a set of words to skip
        :param batch_size: a batch size for internal spaCy multi-threading
        :param ngram_range: range for producing ngrams, ex. for unigrams + bigrams should be set to
        (1, 2), for bigrams only should be set to (2, 2)
        :param lemmas: weather to perform lemmatizing or not while tokenizing, currently works only
        for the English language
        :param n_threads: a number of threads for internal spaCy multi-threading
        """
        if disable is None:
            disable = ['parser', 'ner']
        self.stopwords = stopwords or []
        self.model = spacy.load('en', disable=disable)
        self.model.add_pipe(self.model.create_pipe('sentencizer'))
        self.tokenizer = English().Defaults.create_tokenizer(self.model)
        self.batch_size = batch_size
        self.ngram_range = ngram_range
        self.lemmas = lemmas
        self.n_threads = n_threads
        self.lowercase = lowercase

    def tokenize(self, data: List[str], ngram_range=(1, 1), batch_size=10000, n_threads=1,
                  lowercase=True) -> Generator[List[str], Any, None]:
        """
        Tokenize a list of documents.
        :param data: a list of documents to process
        :param ngram_range: range for producing ngrams, ex. for unigrams + bigrams should be set to
        (1, 2), for bigrams only should be set to (2, 2)
        :param batch_size: the number of documents to process at once;
        improves the spacy 'pipe' performance; shouldn't be too small
        :param n_threads: a number of threads for parallel computing; doesn't work good
         on a standard Python
        :param lowercase: whether to perform lowercasing or not
        :return: a single processed doc generator
        """

        size = len(data)

        _batch_size = self.batch_size or batch_size
        _ngram_range = self.ngram_range or ngram_range
        _n_threads = self.n_threads or n_threads

        if self.lowercase is None:
            _lowercase = lowercase
        else:
            _lowercase = self.lowercase

        for i, doc in enumerate(
                self.tokenizer.pipe(data, batch_size=_batch_size, n_threads=_n_threads)):
            logger.info("Tokenize doc {} from {}".format(i, size))
            if _lowercase:
                tokens = [t.lower_ for t in doc]
            else:
                tokens = [t.text for t in doc]
            processed_doc = self.ngramize(tokens, ngram_range=_ngram_range)
            yield from processed_doc

    def lemmatize(self, data: List[str], ngram_range=(1, 1), batch_size=10000, n_threads=1) -> \
            Generator[List[str], Any, None]:
        """
        Lemmatize a list of documents.
        :param data: a list of documents to process
        :param ngram_range: range for producing ngrams, ex. for unigrams + bigrams should be set to
        (1, 2), for bigrams only should be set to (2, 2)
        :param batch_size: the number of documents to process at once;
        improves the spacy 'pipe' performance; shouldn't be too small
        :param n_threads: a number of threads for parallel computing; doesn't work good
         on a standard Python
        :return: a single processed doc generator
        """

        size = len(data)

        _batch_size = self.batch_size or batch_size
        _ngram_range = self.ngram_range or ngram_range
        _n_threads = self.n_threads or n_threads

        for i, doc in enumerate(
                self.model.pipe(data, batch_size=_batch_size, n_threads=_n_threads)):
            logger.info("Lemmatize doc {} from {}".format(i, size))
            lemmas = chain.from_iterable([sent.lemma_.split() for sent in doc.sents])
            processed_doc = self.ngramize(lemmas, ngram_range=_ngram_range)
            yield from processed_doc

    def ngramize(self, items: List[str], ngram_range=(1, 1)) -> Generator[List[str], Any, None]:
        """
        :param items: list of tokens, lemmas or other strings to form ngrams
        :param ngram_range: range for producing ngrams, ex. for unigrams + bigrams should be set to
        (1, 2), for bigrams only should be set to (2, 2)
        :return: ngrams (as strings) generator
        """
        _ngram_range = self.ngram_range or ngram_range

        filtered = list(
            filter(lambda x: x.isalpha() and x not in self.stopwords, items))

        ngrams = []
        ranges = [(0, i) for i in range(_ngram_range[0], _ngram_range[1] + 1)]
        for r in ranges:
            ngrams += list(zip(*[filtered[j:] for j in range(*r)]))

        formatted_ngrams = [' '.join(item) for item in ngrams]

        yield formatted_ngrams

    def set_stopwords(self, stopwords):
        self.stopwords = stopwords
