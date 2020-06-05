


words = {}

with open('raw-data/negative-words.txt') as f:
    for line in f:
        if line and not line.startswith(';'):
            words[line] = -2


with open('raw-data/positive-words.txt') as f:
    for line in f:
        if line and not line.startswith(';'):
            words[line] = 2

with open('raw-data/SlangSD') as f:
    for line in f:
        word, score = line.split('\t')
        score = int(score)
        words[word] = score

with open('normal-data/words.csv', 'w') as f:
    f.write('; Sentiment scores for words -> Greater numbers = positive sentiment')
    for (word, score) in words.items():
        f.write('{},{}\n'.format(word, score))
