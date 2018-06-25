import codecs
import sys


def generation(data_in, data_out):
    with codecs.open(data_in, 'r') as f1:
        with codecs.open(data_out, 'w') as f2:
            for line in f1.readlines():
                line = line.strip()
                words_line = line
                words_line = words_line.replace('.', ' .')
                words_line = words_line.replace(',', ' ,')
                words_line = words_line.replace("'", " ' ")
                words_line = words_line.replace('"', ' " ')
                words_line = words_line.replace("  ", " ")
                words = words_line.split()
                for word in words:
                    letters = list(word)
                    letters = ' '.join(letters)
                    f2.write(letters + '\t')
                f2.write('#' + words_line + '\n')


if __name__ == '__main__':
    args = sys.argv
    data_in = args[1]
    data_out = args[2]
    generation(data_in, data_out)



