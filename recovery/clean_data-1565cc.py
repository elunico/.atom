import json

words = {}

with open('raw-data/negative-words.txt') as f:
    try:
        for line in f:
            if line and not line.startswith(';'):
                words[line.strip()] = -2
    except UnicodeDecodeError:
        print("unknown char")


with open('raw-data/positive-words.txt') as f:
    for line in f:
        if line and not line.startswith(';'):
            words[line.strip()] = 2

with open('raw-data/SlangSD.txt') as f:
    for line in f:
        word, score = line.strip().split('\t')
        score = int(score)
        words[word] = score

print("Processed {} words. {} generally negative, {} generally positive, {} neutral".format(
    len(list(words.values())),
    len(list(i for i in words.values() if i < 0)),
    len(list(i for i in words.values() if i > 0)),
    len(list(i for i in words.values() if i == 0)),
))

with open('normal-data/words.csv', 'w') as f:
    f.write('; Sentiment scores for words -> Greater numbers = positive sentiment\n')
    del words['']
    for (word, score) in words.items():
        f.write('{},{}\n'.format(word, score))

with open('normal-data/words.json', 'w') as f:
    json.dump(words, f, indent=2)
