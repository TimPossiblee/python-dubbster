import json
import os
import re


def scan_dir(path: str, recursive=False, file_types=(None)):
    list = []
    for entry in os.listdir(path):
        result = os.path.join(path, entry)
        if recursive is True and os.path.isdir(result) is True:
            list.extend(
                scan_dir(result, recursive=recursive, file_types=file_types))
        else:
            if os.path.splitext(entry)[-1] in file_types:
                list.append(result)
    return list


def load_archive(archive_file):
    # TODO replace relative paths with absolute paths eg. AUDIO TRACK PATH
    with open(archive_file) as json_file:
        data = json.load(json_file)
        return data


def load_frames(uid: str, folder: str):
    os.chdir(folder)
    path = os.getcwd()
    list = []
    for entry in os.listdir(path):
        if uid in entry:
            list.append(os.path.join(path, entry))
    list.sort(key=lambda i: int(
        (os.path.splitext(os.path.basename(i))[0]).split('_')[-1]))

    return list


def output_filename(file_name: str, file_directory: str):
    if ']' in file_name:
        if 'MULTi' not in file_name:
            file_name = file_name[:file_name.find(
                ']')] + '-MULTi' + file_name[file_name.find(']'):]
    else:
        file_name = file_name + ' [MULTi]'

    tries = 0
    tmp = ""
    while tries <= 100:
        if not os.path.exists(os.path.join(file_directory, file_name + tmp + '.mkv')):
            return file_name + tmp
        else:
            tries += 1
            tmp = f" ({str(tries)})"

    return None


def create_dir(dirs: str, prefix: str):
    path = os.path.join(dirs, prefix)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def create_file(path):
    f = open(path, 'w')
    f.close()
    return path


def read_sources_file(file: str):
    array = []
    with open(file, 'r') as filehandle:
        array = json.load(filehandle)

    return array


def write_batch_file(file, array):
    with open(file, 'w') as filehandle:
        json.dump(array, filehandle)


def match_tv_episode(filename):
    match = re.search(
        '''S\d{1,2}([-+]?E\d{1,2})+''', filename, re.IGNORECASE)
    if match:
        return match.group(0).lower()
    return None


def load_tv(path1, path2):
    dict1 = {}
    dict2 = {}
    results = []

    for i in scan_dir(path1, recursive=True, file_types=('.mp4', '.mkv', '.avi', 'm4a')):
        match = match_tv_episode(os.path.basename(i))
        if match is not None:
            dict1[match] = os.path.join(
                os.path.dirname(i), os.path.basename(i))

    for i in scan_dir(path2, recursive=True, file_types=('.mp4', '.mkv', '.avi', 'm4a')):
        match = match_tv_episode(os.path.basename(i))
        if match is not None:
            dict2[match] = os.path.join(
                os.path.dirname(i), os.path.basename(i))

    for i in dict1:
        if i in dict2:
            results.append([dict1.get(i), dict2.get(i)])

    return results
