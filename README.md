# SpacyTokenizer

Implementation of a [SpaCy](https://github.com/explosion/spaCy) tokenizer/lemmatizer class for English
language.

## Installation
```bash
pip install -U spacy
python -m spacy download en
```

## Usage example
```python
data = ["I think it's better to fry mushrooms.",
        "Oh, this senseless life of ours!"]
tok = SpacyTokenizer()
items = tok.lemmatize(data)
print(*list(i for i in items))
items = tok.tokenize(data, ngram_range=(1, 2))
print(*list(i for i in items))
```
output:
```bash
02/28/2018 02:22:17 PM: [ Lemmatize doc 0 from 2 ]
02/28/2018 02:22:17 PM: [ Lemmatize doc 1 from 2 ]
02/28/2018 02:22:17 PM: [ Tokenize doc 0 from 2 ]
02/28/2018 02:22:17 PM: [ Tokenize doc 1 from 2 ]
['think', 'be', 'good', 'to', 'fry', 'mushroom', 'think be', 'be good',
'good to', 'to fry', 'fry mushroom'] ['oh', 'this', 'senseless', 'life',
'of', 'oh this', 'this senseless', 'senseless life', 'life of']
['i', 'think', 'it', 'better', 'to', 'fry', 'mushrooms', 'i think',
'think it', 'it better', 'better to', 'to fry', 'fry mushrooms']
['oh', 'this', 'senseless', 'life', 'of', 'ours', 'oh this',
 'this senseless', 'senseless life', 'life of', 'of ours']
```