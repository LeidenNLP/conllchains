import argparse
import requests
import tempfile
import zipfile
import logging
import os
import glob
import json
import sys

from tqdm import tqdm
from typing import Iterable, TextIO

logging.basicConfig(level=logging.INFO)

_URL = "https://data.mendeley.com/public-files/datasets/zmycy7t9h9/files/b078e1c4-f7a4-4427-be7f-9389967831ef/file_downloaded"


def main():
    argparser = argparse.ArgumentParser(description='Download the CONLL corpus to the current working directory, '
                                        'and (assuming its there) extract its coreference annotations.\n\n'
                                        'Example: $ python -m conllchains extract english train --out chains.jsonl')
    argparser.add_argument('command', choices=["download", "extract"])
    argparser.add_argument('--lang', choices=['english', 'arabic', 'chinese', 'all'], nargs='?', default='all',
                           help="For which language to extract the CONLL corpus. Option for 'extract' command only.")
    argparser.add_argument('--part', choices=['train', 'test', 'development', 'conll-2012-test', 'all'], nargs='?', default='all',
                           help="Which partition of the CONLL corpus to extract. Option for 'extract' command only.")
    argparser.add_argument('--out', type=argparse.FileType('w'), nargs='?', default=sys.stdout,
                           help="Which file to write the results to (.jsonl). Otherwise stdout.")

    args = argparser.parse_args()

    download_dir = os.getcwd()
    conll_dir = os.path.join(download_dir, 'conll-2012')

    if args.command == 'download':
        download(download_dir)
    elif args.command == 'extract':
        extract(conll_dir, args.lang, args.part, args.out)


def download(download_dir):

    response = requests.get(_URL, stream=True)
    download_to = tempfile.mkstemp(prefix='conll_', suffix='.zip', dir=download_dir)[1]
    with open(download_to, 'wb') as file:
        for data in tqdm(response.iter_content(1024), f'Downloading corpus to {download_to}.'):
            file.write(data)

    logging.info(f'Corpus downloaded; now unzipping in {download_dir}.')

    with zipfile.ZipFile(download_to, 'r') as file:
        file.extractall(download_dir)

    logging.info(f'All done! Now you should be able to do: \n $ python -m conllchains extract')



def extract(conll_dir: str, language: str, partition: str, out: TextIO) -> None:

    glob_scheme = os.path.join(conll_dir, '*', 'data',
                               '*' if partition == 'all' else partition,
                               'data',
                               '*' if language == 'all' else language,
                               'annotations', '*', '*', '*', '*.*gold_conll')

    paths = glob.glob(glob_scheme)
    logging.info(f'Found {len(paths)} files to use.')
    if len(paths) == 0:
        logging.error(f"No suitable files found. (Looking for files in {conll_dir}...) Make sure to execute 'download' first.")
        exit(2)

    n_chains = 0

    for path in tqdm(paths, desc='Parsing coreference annotations'):
        with open(path) as file:
            for parsed_coreference in parse_conll_lines(file):
                n_chains += len(parsed_coreference['chains'])
                print(json.dumps(parsed_coreference), file=out)

    logging.info(f'Found {n_chains} coreference chains.')


def parse_conll_lines(lines: Iterable[str]) -> Iterable[dict]:
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
