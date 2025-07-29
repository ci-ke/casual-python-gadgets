# 所有活动 摘要：https://bestdori.com/api/events/all.stories.json
# 特定活动 摘要：https://bestdori.com/api/events/1.json
# 数据包列表：https://bestdori.com/api/explorer/cn/assets/scenario/eventstory/event1.json
# 数据包json：https://bestdori.com/assets/cn/scenario/eventstory/event1_rip/Scenarioevent01-01.asset

# 乐队 摘要：https://bestdori.com/api/misc/bandstories.5.json
# 数据包列表：https://bestdori.com/api/explorer/cn/assets/scenario/band/001.json
# 数据包json：https://bestdori.com/assets/cn/scenario/band/001_rip/Scenarioband1-001.asset

# 主线 摘要：https://bestdori.com/api/misc/mainstories.5.json
# 数据包列表：https://bestdori.com/api/explorer/cn/assets/scenario/main.json
# 数据包json：https://bestdori.com/assets/cn/scenario/main_rip/Scenariomain001.asset

from concurrent.futures import ThreadPoolExecutor
import os, sys
from typing import Any, Dict, Optional, Sequence
import requests  # type: ignore

### CONFIG
BASE_SAVE_DIR = r'.'
EVENT_SAVE_DIR = BASE_SAVE_DIR + r'\event_story'
BAND_SAVE_DIR = BASE_SAVE_DIR + r'\band_story'
MAIN_SAVE_DIR = BASE_SAVE_DIR + r'\main_story'

PROXY = None
# PROXY = {'http': 'http://127.0.0.1:10808', 'https': 'http://127.0.0.1:10808'}


### CONSTANT
LANG_INDEX = {'jp': 0, 'en': 1, 'tw': 2, 'cn': 3, 'kr': 4}
BAND_ID_NAME = {
    1: 'Poppin\'Party',
    2: 'Afterglow',
    3: 'Hello, Happy World!',
    4: 'Pastel＊Palettes',
    5: 'Roselia',
    18: 'RAISE A SUILEN',
    21: 'Morfonica',
    45: 'MyGO!!!!!',
}
EVENT_IS_MAIN = [217]


def read_story_in_json(json_data: Dict[str, Dict[str, Any]]) -> str:
    ret = ''

    talks = json_data['Base']['talkData']
    scenes = json_data['Base']['specialEffectData']

    scripts = json_data['Base']['snippets']
    next_talk_need_newline = True

    for script in scripts:
        if script['actionType'] == 6:
            scene = scenes[script['referenceIndex']]
            if scene['effectType'] == 7:
                ret += '\n（背景切换）\n'
                next_talk_need_newline = True
            elif scene['effectType'] == 8:
                ret += '\n【' + scene['stringVal'] + '】\n'
                next_talk_need_newline = True
            elif scene['effectType'] == 24:
                if next_talk_need_newline:
                    ret += '\n'
                ret += '（全屏幕文字）：' + scene['stringVal'].replace('\n', '') + '\n'
                next_talk_need_newline = False
        elif script['actionType'] == 1:
            talk = talks[script['referenceIndex']]
            if next_talk_need_newline:
                ret += '\n'
            ret += (
                talk['windowDisplayName'] + '：' + talk['body'].replace('\n', '') + '\n'
            )
            next_talk_need_newline = False

    return ret[:-1]


def get_event_story(event_id: int, lang: str = 'cn') -> None:
    res = requests.get(
        f'https://bestdori.com/api/events/{event_id}.json', proxies=PROXY
    )
    res.raise_for_status()
    res_json: Dict[str, Any] = res.json()

    event_name = res_json['eventName'][LANG_INDEX[lang]]
    if event_name is None:
        print(f'event {event_id} has no {lang.upper()}.')
        return

    event_filename = valid_filename(event_name)

    save_folder_name = f'{event_id} {event_filename}'

    if lang != 'cn':
        save_folder_name = lang + '-' + save_folder_name

    event_save_dir = os.path.join(EVENT_SAVE_DIR, save_folder_name)

    os.makedirs(event_save_dir, exist_ok=True)

    if event_id == 248:
        with open(
            os.path.join(event_save_dir, '无剧情.txt'), 'w', encoding='utf8'
        ) as f:
            f.write('本活动没有活动剧情\n')
        return

    for story in res_json['stories']:
        name = f"{story['scenarioId']} {story['caption'][LANG_INDEX[lang]]} {story['title'][LANG_INDEX[lang]]}"
        synopsis = story['synopsis'][LANG_INDEX[lang]].replace('\n', '')
        id = story['scenarioId']

        if ('bandStoryId' not in story) and (event_id not in EVENT_IS_MAIN):
            res2 = requests.get(
                f'https://bestdori.com/assets/{lang}/scenario/eventstory/event{event_id}_rip/Scenario{id}.asset',
                proxies=PROXY,
            )
            res2.raise_for_status()
            res_json2: Dict[str, Dict[str, Any]] = res2.json()

            text = read_story_in_json(res_json2)
        elif event_id in EVENT_IS_MAIN:
            text = '见主线故事'
        else:
            text = '见乐队故事'

        filename = valid_filename(name)

        with open(
            os.path.join(event_save_dir, filename) + '.txt', 'w', encoding='utf8'
        ) as f:
            f.write(name + '\n\n')
            f.write(synopsis + '\n\n')
            f.write(text + '\n')

        print(f'get event {event_id} {event_name} {name} done.')


def get_band_story(
    want_band_id: Optional[int] = None,
    want_chapter_number: Optional[int] = None,
    lang: str = 'cn',
) -> None:
    if want_band_id is not None:
        assert want_band_id in BAND_ID_NAME

    res = requests.get(
        'https://bestdori.com/api/misc/bandstories.5.json', proxies=PROXY
    )
    res.raise_for_status()
    res_json: Dict[str, Dict[str, Any]] = res.json()

    for band_story in res_json.values():
        band_id = band_story['bandId']
        try:
            chapterNumber = band_story['chapterNumber']
        except KeyError:
            continue

        if want_band_id is not None:
            if want_band_id != band_id:
                continue
        if want_chapter_number is not None:
            if want_chapter_number != chapterNumber:
                continue

        band_name = BAND_ID_NAME[band_id]

        if band_story['mainTitle'][LANG_INDEX[lang]] == None:
            print(
                f'band story {band_name} {band_story["mainTitle"][0]} {band_story["subTitle"][0]} has no {lang.upper()}.'
            )
            continue

        save_folder_name = f'{band_story["mainTitle"][LANG_INDEX[lang]]} {band_story["subTitle"][LANG_INDEX[lang]]}'
        if lang != 'cn':
            save_folder_name = lang + '-' + save_folder_name

        band_save_dir = os.path.join(BAND_SAVE_DIR, band_name, save_folder_name)
        os.makedirs(band_save_dir, exist_ok=True)

        for story in band_story['stories'].values():
            name = f"{story['scenarioId']} {story['caption'][LANG_INDEX[lang]]} {story['title'][LANG_INDEX[lang]]}"
            synopsis = story['synopsis'][LANG_INDEX[lang]].replace('\n', '')
            id = story['scenarioId']

            res2 = requests.get(
                f'https://bestdori.com/assets/{lang}/scenario/band/{band_id:03}_rip/Scenario{id}.asset',
                proxies=PROXY,
            )
            res2.raise_for_status()
            res_json2: Dict[str, Dict[str, Any]] = res2.json()

            text = read_story_in_json(res_json2)

            with open(
                os.path.join(band_save_dir, name) + '.txt', 'w', encoding='utf8'
            ) as f:
                f.write(name + '\n\n')
                f.write(synopsis + '\n\n')
                f.write(text + '\n')

            print(
                f'get band story {band_name} {band_story["mainTitle"][LANG_INDEX[lang]]} {name} done.'
            )


def get_main_story(id_range: Optional[Sequence[int]] = None, lang: str = 'cn') -> None:
    res = requests.get(
        'https://bestdori.com/api/misc/mainstories.5.json', proxies=PROXY
    )
    res.raise_for_status()
    res_json: Dict[str, Dict[str, Any]] = res.json()

    os.makedirs(MAIN_SAVE_DIR, exist_ok=True)

    for strId, main_story in res_json.items():
        if id_range is not None and int(strId) not in id_range:
            continue

        if main_story['title'][LANG_INDEX[lang]] == None:
            print(
                f'main story {main_story["caption"][0]} {main_story["title"][0]} has no {lang.upper()}.'
            )
            continue

        name = f"{main_story['scenarioId']} {main_story['caption'][LANG_INDEX[lang]]} {main_story['title'][LANG_INDEX[lang]]}"

        if lang != 'cn':
            name = lang + '-' + name

        synopsis = main_story['synopsis'][LANG_INDEX[lang]].replace('\n', '')
        id = main_story['scenarioId']

        res2 = requests.get(
            f'https://bestdori.com/assets/{lang}/scenario/main_rip/Scenario{id}.asset',
            proxies=PROXY,
        )
        res2.raise_for_status()
        res_json2: Dict[str, Dict[str, Any]] = res2.json()

        text = read_story_in_json(res_json2)

        with open(
            os.path.join(MAIN_SAVE_DIR, name) + '.txt', 'w', encoding='utf8'
        ) as f:
            f.write(name + '\n\n')
            f.write(synopsis + '\n\n')
            f.write(text + '\n')

        print(f'get main story {name} done.')


def valid_filename(filename: str) -> str:
    return (
        filename.strip()
        .replace('*', '＊')
        .replace(':', '：')
        .replace('/', '／')
        .replace('?', '？')
        .replace('"', "''")
    )


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(lambda _: get_main_story(), range(1))
        executor.map(lambda _: get_band_story(), range(1))
        executor.map(get_event_story, range(1, 282))
