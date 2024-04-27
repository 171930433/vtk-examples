#!/usr/bin/env python3

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlretrieve


def get_program_parameters():
    import argparse
    description = 'Classes in language 1 but not in language 2.'
    epilogue = '''
The JSON file needed by this script is obtained from the gh-pages branch
 of the vtk-examples GitHub site.
It is stored in your tempfile directory.
If you change the URL to the JSON file, remember that there is a ten minute
wait before you can overwrite the last downloaded file. To force the download
specify -o on the command line.

Here is the URL for an alternative site for testing:
"https://raw.githubusercontent.com/ajpmaclean/web-test/gh-pages/src/Coverage/vtk_vtk-examples_xref.json"

'''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('language1', help='The desired language, one of: CSharp, Cxx, Java, Python.')
    parser.add_argument('language2', help='The desired language, one of: CSharp, Cxx, Java, Python.')
    parser.add_argument('-j', '--json_xref_url',
                        default='https://raw.githubusercontent.com/Kitware/vtk-examples/gh-pages/src/Coverage/vtk_vtk-examples_xref.json',
                        help='The URL for the JSON cross-reference file.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Force an initial download of the JSON cross-reference file.')
    parser.add_argument('-f', '--file', default=None,
                        help='The file name to write the markdown file too.')

    args = parser.parse_args()
    return args.language1, args.language2, args.json_xref_url, args.overwrite, args.file


def download_file(dl_path, dl_url, overwrite=False):
    """
    Use the URL to get a file.

    :param dl_path: The path to download the file to.
    :param dl_url: The URL of the file.
    :param overwrite: If true, do a download even if the file exists.
    :return: The path to the file as a pathlib Path.
    """
    file_name = dl_url.split('/')[-1]

    # Create necessary subdirectories in the dl_path
    # (if they don't exist).
    Path(dl_path).mkdir(parents=True, exist_ok=True)
    # Download if it doesn't exist in the directory overriding if overwrite is True.
    path = Path(dl_path, file_name)
    if not path.is_file() or overwrite:
        try:
            urlretrieve(dl_url, path)
        except HTTPError as e:
            raise RuntimeError(f'Failed to download {dl_url}. {e.reason}')
    return path


def get_examples(d, lang1, lang2):
    """
    Classes/examples in lang1 but not in lang2.

    :param d: The dictionary.
    :param lang1: The first language e.g. Python.
    :param lang2: The second language e.g. PythonicAPI.
    :return: Classes/examples in lang1 but not in lang2.
    """
    # Select all classes for each language.
    d1 = dict()
    d2 = dict()
    for k, v in d.items():
        for kk, vv in v.items():
            if lang1 == kk:
                d1[k] = vv
            if lang2 == kk:
                d2[k] = vv
    k1 = d1.keys()
    k2 = d2.keys()
    # Keys in k1 but not in k2.
    wanted_keys = k1 - k2

    # Get the corresponding examples in d1.

    def dict_filter(src_dict, wk):
        """
        Create a dictionary from an existing dictionary
         using a set of wanted keys.

        :param src_dict: The source dictionary.
        :param wk: The wanted keys.
        :return: A dictionary with the wanted keys.
        """
        return dict([(i, src_dict[i]) for i in src_dict if i in set(wk)])

    d12 = dict_filter(d1, wanted_keys)
    keys = sorted(d12.keys())
    res = list()
    res.append(f'### VTK Classes in {lang1} but not in {lang2}')
    number_of_examples = 0
    for k in keys:
        res.append(f'\n#### {k}\n')
        k1 = sorted(d12[k].keys())
        for kk1 in k1:
            res.append(f'  [{kk1}]({d12[k][kk1]})')
            number_of_examples += 1
    res.append(f'\nCount of VTK Classes :{len(wanted_keys):6}')
    res.append(f'             Examples:{number_of_examples:6}')
    res.append('')
    return res


def get_crossref_dict(ref_dir, xref_url, overwrite=False):
    """
    Download and return the json cross-reference file.

    This function ensures that the dictionary is recent.

    :param ref_dir: The directory where the file will be downloaded.
    :param xref_url: The URL for the JSON cross-reference file.
    :param overwrite: If true, do a download even if the file exists.
    :return: The dictionary cross-referencing vtk classes to examples.
    """
    path = download_file(ref_dir, xref_url, overwrite=overwrite)
    if not path.is_file():
        print(f'The path: {str(path)} does not exist.')
        return None
    dt = datetime.today().timestamp() - os.path.getmtime(path)
    # Force a new download if the time difference is > 10 minutes.
    if dt > 600:
        path = download_file(ref_dir, xref_url, overwrite=True)
    with open(path) as json_file:
        return json.load(json_file)


def main():
    language1, language2, xref_url, overwrite, file_name = get_program_parameters()
    language1 = language1.lower()
    available_languages = {k.lower(): k for k in ['CSharp', 'Cxx', 'Java', 'Python', 'PythonicAPI']}
    available_languages.update({'cpp': 'Cxx', 'c++': 'Cxx', 'c#': 'CSharp'})
    if language1 not in available_languages:
        print(f'The language: {language1} is not available.')
        tmp = ', '.join(sorted([lang for lang in set(available_languages.values())]))
        print(f'Choose one of these: {tmp}.')
        return
    else:
        language1 = available_languages[language1]
    language2 = language2.lower()
    if language2 not in available_languages:
        print(f'The language: {language2} is not available.')
        tmp = ', '.join(sorted([lang for lang in set(available_languages.values())]))
        print(f'Choose one of these: {tmp}.')
        return
    else:
        language2 = available_languages[language2]
    xref_dict = get_crossref_dict(tempfile.gettempdir(), xref_url, overwrite)
    if xref_dict is None:
        print('The dictionary cross-referencing vtk classes to examples was not downloaded.')
        return

    res = get_examples(xref_dict, language1, language2)
    if res:
        if file_name:
            fn = Path(file_name).with_suffix('.md')
            if fn.is_file():
                print(f'Cannot overwrite {fn}, please select a new file name.')
                return
            else:
                with fn.open(mode='w'):
                    fn.write_text('\n'.join(res))
        else:
            print(res)


if __name__ == '__main__':
    main()
