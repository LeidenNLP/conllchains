import json
from tqdm import tqdm
import os
import glob
import logging
from collections import namedtuple
import click

logging.basicConfig(level=logging.INFO)


@click.command(help='Let DIR be the directory containing the conll-2012 directory. The default is the current working directory.')
@click.argument('dir', type=click.Path(exists=True, file_okay=False, resolve_path=True), required=False, default='')
@click.option('--lang', type=click.Choice(['english', 'arabic', 'chinese', '*']), default='*')
@click.option('--partition', type=click.Choice(['train', 'test', 'development', 'conll-2012-test', '*']), default='*')
def main(dir, lang, partition):
    glob_scheme = os.path.join(dir, 'conll-2012', '*', 'data', partition, 'data', lang, 'annotations', '*', '*', '*', '*.*gold_conll')

    paths = glob.glob(glob_scheme)
    logging.info(f'Found {len(paths)} files to use.')
    if len(paths) == 0:
        logging.error('No suitable files found. Make sure you passed the right dir.')
        exit(2)

    n_chains = 0

    for path in tqdm(paths, desc='Parsing coreference annotations'):
        with open(path) as file:
            for parsed_coreference in parse_coreference_lines(file):
                n_chains += len(parsed_coreference['chains'])
                print(json.dumps(parsed_coreference))

    logging.info(f'Found {n_chains} coreference chains.')


def parse_coreference_lines(lines):
    """
    Parses coreference annotations in (some) conll format, as downloaded by the accompanying download.py.
    Yields parsed documents, each consisting of a list of tokens and a list of the extracted coreference chains.
    Each coreference chain is a list of mentions; each mention is a tuple of tokens; each token has an id and a form.

    :param lines: an iterable of strings in the conll annotation format.
    :return: dictionaries with keys "document" and "chains".
    """

    token_id = 0

    for line in lines:
        if not line.strip():
            continue
        if line.startswith('#begin document'):
            open_mentions = {}
            open_mention_chains = {}
            token_id = 0
            document = []
            continue
        if line.startswith('#end document'):
            finished_chains = list(open_mention_chains.values())
            if finished_chains:
                yield {"document": document, "chains": finished_chains}
            continue

        values = line.split()   # lines have space-separated values
        form, coref_annotation = values[3], values[-1]
        document.append(form)

        token = {"id": token_id, "form": form}
        token_id += 1

        for mentions in open_mentions.values():
            for mention in mentions:
                mention.append(token)

        if coref_annotation == '-':
            continue

        for label in coref_annotation.split('|'):

            num = label.strip('()')

            if num not in open_mention_chains:
                open_mention_chains[num] = []

            if num not in open_mentions:
                open_mentions[num] = []

            if label.startswith('('):
                open_mentions[num].append([token])

            if label.endswith(')'):
                finished_mention = tuple(open_mentions[num].pop(-1))
                open_mention_chains[num].append(finished_mention)


if __name__ == '__main__':
    main()