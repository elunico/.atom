import json

def process_negative_words(words):
    with open('raw-data/negative-words.txt') as f:
        while True:
            try:
                for line in f:
                    if line and not line.startswith(';'):
                        words[line.strip()] = -2
                break
            except UnicodeDecodeError:
                print("unknown char")
                continue
    return words


def process_positive_words(words):
    with open('raw-data/positive-words.txt') as f:
        for line in f:
            if line and not line.startswith(';'):
                words[line.strip()] = 2
    return words


def process_slang_words(words):
    with open('raw-data/SlangSD.txt') as f:
        for line in f:
            word, score = line.strip().split('\t')
            score = int(score)
            words[word.strip()] = score
    return words


def process_afinn_words(words):
    # afinn has priority over other sources, so we do that last
    with open('raw-data/afinn/AFINN-111.txt') as f:
        for line in f:
            word, score = line.strip().split('\t')
            words[word.strip()] = int(score)
    return words



def clean_all_words(words):
    return {k.lower(): v for (k, v) in words.items()}


def write_csv_words(words, place):
    with open(place, 'w') as f:
        f.write('; Sentiment scores for words -> Greater numbers = positive sentiment\n')
        del words['']
        for (word, score) in words.items():
            f.write('{},{}\n'.format(word, score))

def write_json_words(words, place):
    with open(place, 'w') as f:
        json.dump(words, f, indent=2)

def main():
    words = {}

    words = process_negative_words(words)
    words = process_positive_words(words)
    words = process_slang_words(words)

    # afinn has priority so do it last
    words = process_afinn_words(words)

    words = clean_all_words(words)

    print("Processed {} words. {} generally negative, {} generally positive, {} neutral".format(
        len(list(words.values())),
        len(list(i for i in words.values() if i < 0)),
        len(list(i for i in words.values() if i > 0)),
        len(list(i for i in words.values() if i == 0)),
    ))

    write_csv_words(words, 'normal-data/words.csv')
    write_json_words(words, 'normal-data/words.json')


if __name__ == '__main__':
    main()
