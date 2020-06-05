
import tqdm

words = {}

with open('raw-data/negative-words.txt') as f:
    try:
        for line in f:
            if line and not line.startswith(';'):
                words[line] = -2
    except:
        pass


with open('raw-data/positive-words.txt') as f:
    for line in f:
        if line and not line.startswith(';'):
            words[line] = 2

with open('raw-data/SlangSD.txt') as f:
    for line in f:
        word, score = line.split('\t')
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
    for (word, score) in words.items():
        f.write('{},{}\n'.format(word, score))
