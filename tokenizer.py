import logging
from itertools import chain
from typing import List

import spacy
from spacy.lang.en import English

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)


class SpacyTokenizer:
    """
    Tokenize or lemmatize a list of documents.
    Return list of tokens or lemmas, without sentencizing.
    Works only for English language.
    """
    def __init__(self, disable=None, stopwords=None):
        """
        :param disable: pipeline processors to omit; if nothing should be disabled,
         pass an empty list
        :param stopwords: a set of words to skip
        """
        if disable is None:
            disable = ['parser', 'ner']
        self.stopwords = stopwords or []
        self.model = spacy.load('en', disable=disable)
        self.model.add_pipe(self.model.create_pipe('sentencizer'))
        self.tokenizer = English().Defaults.create_tokenizer(self.model)

    def tokenize(self, data: List[str], ngram_range=(1, 1), batch_size=1000, n_threads=4):
        """
        Tokenize a list of documents.
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
        for i, doc in enumerate(
                self.tokenizer.pipe(data, batch_size=batch_size, n_threads=n_threads)):
            logging.info("Process doc {} from {}".format(i, size))
            tokens = [t.lower_ for t in doc]
            processed_doc = self.ngramize(tokens, ngram_range=ngram_range)
            yield from processed_doc

    def lemmatize(self, data: List[str], ngram_range=(1, 1), batch_size=1000, n_threads=4):
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

        for i, doc in enumerate(self.model.pipe(data, batch_size=batch_size, n_threads=n_threads)):
            logging.info("Process doc {} from {}".format(i, size))
            lemmas = chain.from_iterable([sent.lemma_.split() for sent in doc.sents])
            processed_doc = self.ngramize(lemmas, ngram_range=ngram_range)
            yield from processed_doc

    def ngramize(self, items: List[str], ngram_range=(1, 1)):
        """
        :param items: list of tokens, lemmas or other strings to form ngrams
        :param ngram_range: range for producing ngrams, ex. for unigrams + bigrams should be set to
        (1, 2), for bigrams only should be set to (2, 2)
        :return:
        """
        filtered = list(
            filter(lambda x: x.isalpha() and x not in self.stopwords, items))

        ngrams = []
        ranges = [(0, i) for i in range(ngram_range[0], ngram_range[1] + 1)]
        for r in ranges:
            ngrams += list(zip(*[filtered[j:] for j in range(*r)]))

        formatted_ngrams = [' '.join(item) for item in ngrams]

        yield formatted_ngrams


# Test
# data = ['His paintings brought him both critical and commercial success,'
#         ' which enabled. him to set up his own. professional portrait studio'
#         ' in Chelsea, south-west London.', ' After the Great War finished, he met'
#         ' and fell in love with Katherine Gardiner, she immediately became his muse and features'
#         ' in many key work from the period. The couple married in 1921.']
# tok = SpacyTokenizer()
# items = tok.lemmatize(data)
# print(*list(i for i in items))
# items = tok.tokenize(data)
# print(*list(i for i in items))
