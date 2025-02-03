#! /usr/bin/env python3

from lyricsgenius import Genius
from time import sleep
from random import random, shuffle
import os
import re
import requests


token_file = '/home/nwoods/.genius/access_token'
artist_file = '/home/nwoods/wikipedia_list_of_hip-hop_musicians.txt'
base_path = '/data/nwoods/featurized_verses/lyrics'
fail_file = '/home/nwoods/genius_failures.txt'

bad_char_pattern = re.compile(r"^[ .]|[/<>:\"'\\|?*]+|[ .]$")

if __name__ == '__main__':
    with open(artist_file, 'r') as f:
        artists = [a for a in f if a.strip()]
        shuffle(artists)

    with open(token_file, 'r') as f:
        genius = Genius(f.read().strip())

    for a in artists:
        artist = bad_char_pattern.sub('_', a.strip())
        path = os.path.join(base_path, artist)
        try:
            os.mkdir(path)
        except (FileExistsError, FileNotFoundError):
            continue
        try:
            with open(os.path.join(path, 'status.txt'), 'x') as f:
                f.write('1')
        except FileExistsError:
            continue

        retry = 0
        while retry < 5:
            try:
                catalog = genius.search_artist(artist)
                break
            except (requests.exceptions.Timeout, requests.exceptions.HTTPError):
                retry += 1

        if retry >= 5 or catalog is None or len(catalog.songs) == 0:
            with open(fail_file, 'a') as f:
                f.write(artist + '\n')
            continue

        for song in catalog.songs:
            title = bad_char_pattern.sub('_', song.title.strip())
            with open(os.path.join(path, title + '.json'), 'w') as f:
                f.write(song.to_json())

        with open(os.path.join(path, 'status.txt'), 'w') as f:
            f.write('0')

        sleep(random() * 3. + 2.)
