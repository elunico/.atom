
import tqdm

words = {}

with open('raw-data/negative-words.txt') as f:
    for line in tqdm.tqdm(f):
        try:
            if line and not line.startswith(';'):
                words[line] = -2
        except:
            print(line)


with open('raw-data/positive-words.txt') as f:
    for line in tqdm.tqdm(f):
        if line and not line.startswith(';'):
            words[line] = 2

with open('raw-data/SlangSD') as f:
    for line in tqdm.tqdm(f):
        word, score = line.split('\t')
        score = int(score)
        words[word] = score

print("Processed {} words. {} generally negative, {} generally positive, {} neutral".format(
    len(list(f.values())),
    len(list(i for i in f.values() if i < 0)),
    len(list(i for i in f.values() if i > 0)),
    len(list(i for i in f.values() if i == 0)),
))

with open('normal-data/words.csv', 'w') as f:
    f.write('; Sentiment scores for words -> Greater numbers = positive sentiment')
    for (word, score) in tqdm.tqdm(words.items()):
        f.write('{},{}\n'.format(word, score))
