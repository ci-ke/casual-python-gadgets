# 活动 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/events.json
# 活动剧情 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/eventStories.json
# 数据包json：https://storage.sekai.best/sekai-cn-assets/event_story/event_stella_2020/scenario/event_01_01.asset

# 组合 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/unitProfiles.json
# 组合剧情 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/unitStories.json
# 数据包json：https://storage.sekai.best/sekai-cn-assets/scenario/unitstory/light-sound-story-chapter/leo_01_00.asset

import os, sys
from typing import Any
from concurrent.futures import ThreadPoolExecutor
import requests  # type: ignore


### CONFIG
BASE_SAVE_DIR = r'.'
EVENT_SAVE_DIR = BASE_SAVE_DIR + r'\event_story'
UNIT_SAVE_DIR = BASE_SAVE_DIR + r'\unit_story'

PROXY = None
# PROXY = {'http': 'http://127.0.0.1:10808', 'https': 'http://127.0.0.1:10808'}

### CONSTANT
UNIT_ID_NAME = {
    1: '虚拟歌手',
    2: 'Leo/need',
    3: 'MORE MORE JUMP！',
    4: 'Vivid BAD SQUAD',
    5: 'Wonderlands×Showtime',
    6: '25点，Nightcord见。',
}


def read_story_in_json(json_data: dict[str, Any]) -> str:
    ret = ''

    talks = json_data['TalkData']
    scenes = json_data['SpecialEffectData']

    scripts = json_data['Snippets']
    next_talk_need_newline = True

    for script in scripts:
        if script['Action'] == 6:
            scene = scenes[script['ReferenceIndex']]
            if scene['EffectType'] == 7:
                ret += '\n（背景切换）\n'
                next_talk_need_newline = True
            elif scene['EffectType'] == 8:
                ret += '\n【' + scene['StringVal'] + '】\n'
                next_talk_need_newline = True
            elif scene['EffectType'] == 24:
                if next_talk_need_newline:
                    ret += '\n'
                ret += '（全屏幕文字）：' + scene['StringVal'].replace('\n', '') + '\n'
                next_talk_need_newline = False
        elif script['Action'] == 1:
            talk = talks[script['ReferenceIndex']]

            if next_talk_need_newline:
                ret += '\n'
            ret += (
                talk['WindowDisplayName'] + '：' + talk['Body'].replace('\n', '') + '\n'
            )
            next_talk_need_newline = False

    return ret[:-1]


class Event_story_getter:
    def __init__(self) -> None:
        res = requests.get(
            f'https://sekai-world.github.io/sekai-master-db-cn-diff/events.json',
            proxies=PROXY,
        )
        res.raise_for_status()
        self.events_json: list[dict[str, Any]] = res.json()

        res = requests.get(
            f'https://sekai-world.github.io/sekai-master-db-cn-diff/eventStories.json',
            proxies=PROXY,
        )
        res.raise_for_status()
        self.eventStories_json: list[dict[str, Any]] = res.json()

    def get(self, event_id: int) -> None:
        event = self.events_json[event_id - 1]
        eventStory = self.eventStories_json[event_id - 1]

        assert (event['id'] == event_id) and (eventStory['eventId'] == event_id)

        event_name = event['name']
        event_outline = eventStory['outline'].replace('\n', '')
        assetbundleName = event['assetbundleName']

        event_filename = valid_filename(event_name)
        event_save_dir = os.path.join(EVENT_SAVE_DIR, f'{event_id} {event_filename}')
        os.makedirs(event_save_dir, exist_ok=True)

        for episode in eventStory['eventStoryEpisodes']:
            episode_name = (
                f"{episode['eventStoryId']}-{episode['episodeNo']} {episode['title']}"
            )
            scenarioId = episode['scenarioId']

            res = requests.get(
                f'https://storage.sekai.best/sekai-cn-assets/event_story/{assetbundleName}/scenario/{scenarioId}.asset',
                proxies=PROXY,
            )
            res.raise_for_status()
            story_json: dict[str, Any] = res.json()

            text = read_story_in_json(story_json)

            filename = valid_filename(episode_name)

            with open(
                os.path.join(event_save_dir, filename) + '.txt', 'w', encoding='utf8'
            ) as f:
                if episode['episodeNo'] == 1:
                    f.write(event_outline + '\n\n')
                f.write(episode_name + '\n\n')
                f.write(text + '\n')

            print(f'get event {event_id} {event_name} {episode_name} done.')


class Unit_story_getter:
    def __init__(self) -> None:
        res = requests.get(
            f'https://sekai-world.github.io/sekai-master-db-cn-diff/unitProfiles.json',
            proxies=PROXY,
        )
        res.raise_for_status()
        self.unitProfiles_json: list[dict[str, Any]] = res.json()

        res = requests.get(
            f'https://sekai-world.github.io/sekai-master-db-cn-diff/unitStories.json',
            proxies=PROXY,
        )
        res.raise_for_status()
        self.unitStories_json: list[dict[str, Any]] = res.json()

    def get(self, unit_id: int) -> None:
        for unitProfile in self.unitProfiles_json:
            if unitProfile['seq'] == unit_id:
                unitName = unitProfile['unitName']
                unit_outline = unitProfile['profileSentence']
                break
        else:
            raise ValueError(unit_id)

        for unitStory in self.unitStories_json:
            if unitStory['seq'] == unit_id:
                assetbundleName = unitStory['chapters'][0]['assetbundleName']
                episodes = unitStory['chapters'][0]['episodes']
                break
        else:
            raise ValueError(unit_id)

        unit_filename = valid_filename(unitName)
        unit_save_dir = os.path.join(UNIT_SAVE_DIR, f'{unit_id} {unit_filename}')
        os.makedirs(unit_save_dir, exist_ok=True)

        for episode in episodes:
            episode_name = (
                f"{episode['chapterNo']}-{episode['episodeNo']} {episode['title']}"
            )
            scenarioId = episode['scenarioId']
            res = requests.get(
                f'https://storage.sekai.best/sekai-cn-assets/scenario/unitstory/{assetbundleName}/{scenarioId}.asset',
                proxies=PROXY,
            )
            res.raise_for_status()
            story_json: dict[str, Any] = res.json()

            text = read_story_in_json(story_json)

            filename = valid_filename(episode_name)

            with open(
                os.path.join(unit_save_dir, filename) + '.txt', 'w', encoding='utf8'
            ) as f:
                if episode['episodeNo'] == 1:
                    f.write(unit_outline + '\n\n')
                f.write(episode_name + '\n\n')
                f.write(text + '\n')

            print(f'get unit {unit_id} {unitName} {episode_name} done.')


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
    unit_getter = Unit_story_getter()
    event_getter = Event_story_getter()
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(unit_getter.get, range(1, 7))
        executor.map(event_getter.get, range(1, 141))
