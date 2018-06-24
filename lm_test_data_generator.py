import codecs
import sys


def generation(data_in, data_out):
    with codecs.open(data_in, 'r') as f1:
        with codecs.open(data_out, 'w') as f2:
            for line in f1.readlines():
                line = line.strip()
                words = line
                words = words.replace('.', ' .')
                words = words.replace(',', ' ,')
                words = words.replace("'", " ' ")
                words = words.replace('"', ' " ')
                words = words.replace("  ", " ")
                words = words.split()
                for word in words:
                    letters = list(word)
                    letters = ' '.join(letters)
                    f2.write(letters + '\t')
                f2.write('#' + line + '\n')


if __name__ == '__main__':
    args = sys.argv
    data_in = args[1]
    data_out = args[2]
    generation(data_in, data_out)



