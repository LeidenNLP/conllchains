import requests
from tqdm import tqdm
import zipfile
import click
import logging
import tempfile

logging.basicConfig(level=logging.INFO)

_URL = "https://data.mendeley.com/public-files/datasets/zmycy7t9h9/files/b078e1c4-f7a4-4427-be7f-9389967831ef/file_downloaded"

@click.command(help='DIR should be the directory containing the conll-2012 directory. The default is the current working directory.')
@click.argument('dir', type=click.Path(exists=True, file_okay=False, resolve_path=True), required=False, default='')
def main(dir):
    response = requests.get(_URL, stream=True)
    download_to = tempfile.mkstemp(prefix='conll_', suffix='.zip', dir=dir)[1]
    with open(download_to, 'wb') as file:
        for data in tqdm(response.iter_content(1024), f'Downloading corpus to {download_to}.'):
            file.write(data)

    logging.info(f'Corpus downloaded; now unzipping to {dir}.')

    with zipfile.ZipFile(download_to, 'r') as file:
        file.extractall(dir)

    logging.info(f'All done!')


if __name__ == '__main__':
    main()