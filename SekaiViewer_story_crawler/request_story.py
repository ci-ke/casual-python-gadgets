# 活动 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/events.json
# 活动剧情 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/eventStories.json
# 数据包json：https://storage.sekai.best/sekai-cn-assets/event_story/event_stella_2020/scenario/event_01_01.asset

# 组合 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/unitProfiles.json
# 组合剧情 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/unitStories.json
# 数据包json：https://storage.sekai.best/sekai-cn-assets/scenario/unitstory/light-sound-story-chapter/leo_01_00.asset

# 卡牌 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/cards.json
# 卡牌剧情 摘要：https://sekai-world.github.io/sekai-master-db-cn-diff/cardEpisodes.json
# 数据包json：https://storage.sekai.best/sekai-cn-assets/character/member/res001_no001/001001_ichika01.asset

import bisect
import os, sys
from typing import Any
from concurrent.futures import ThreadPoolExecutor
import requests  # type: ignore


### CONFIG
BASE_SAVE_DIR = r'.'
EVENT_SAVE_DIR = BASE_SAVE_DIR + r'\event_story'
UNIT_SAVE_DIR = BASE_SAVE_DIR + r'\unit_story'
CARD_SAVE_DIR = BASE_SAVE_DIR + r'\card_story'

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

UNIT_CODE_NAME = {
    'light_sound': 'LN',
    'idol': 'MMJ',
    'street': 'VBS',
    'theme_park': 'WS',
    'school_refusal': '25时',
    'piapro': '虚拟歌手',
}

CHARA_ID_UNIT_AND_NAME = {
    1: 'LN_星乃一歌',
    2: 'LN_天马咲希',
    3: 'LN_望月穗波',
    4: 'LN_日野森志步',
    5: 'MMJ_花里实乃理',
    6: 'MMJ_桐谷遥',
    7: 'MMJ_桃井爱莉',
    8: 'MMJ_日野森雫',
    9: 'VBS_小豆泽心羽',
    10: 'VBS_白石杏',
    11: 'VBS_东云彰人',
    12: 'VBS_青柳冬弥',
    13: 'WS_天马司',
    14: 'WS_凤笑梦',
    15: 'WS_草薙宁宁',
    16: 'WS_神代类',
    17: '25时_宵崎奏',
    18: '25时_朝比奈真冬',
    19: '25时_东云绘名',
    20: '25时_晓山瑞希',
    21: '虚拟歌手_初音未来',
    22: '虚拟歌手_镜音铃',
    23: '虚拟歌手_镜音连',
    24: '虚拟歌手_巡音流歌',
    25: '虚拟歌手_MEIKO',
    26: '虚拟歌手_KAITO',
}

EXTRA_CHARA_ID_UNIT_AND_NAME_FOR_BANNER = {
    27: '虚拟歌手_初音未来（LN）',
    28: '虚拟歌手_初音未来（MMJ）',
    29: '虚拟歌手_初音未来（VBS）',
    30: '虚拟歌手_初音未来（WS）',
    31: '虚拟歌手_初音未来（25时）',
}

RARITY_NAME = {
    'rarity_1': '一星',
    'rarity_2': '二星',
    'rarity_3': '三星',
    'rarity_4': '四星',
    'rarity_birthday': '生日',
}


class Story_reader:
    def __init__(self, lang: str = 'cn') -> None:
        self.lang = lang
        if lang == 'cn':
            character2ds_url = 'https://sekai-world.github.io/sekai-master-db-cn-diff/character2ds.json'
        elif lang == 'jp':
            character2ds_url = (
                'https://sekai-world.github.io/sekai-master-db-diff/character2ds.json'
            )
        else:
            raise NotImplementedError

        res = requests.get(character2ds_url, proxies=PROXY)
        res.raise_for_status()
        self.character2ds: list[dict[str, Any]] = res.json()

        self.character2ds_lookup = DictLookup(self.character2ds, 'id')

    def read_story_in_json(self, json_data: dict[str, Any]) -> str:
        ret = ''

        talks = json_data['TalkData']
        scenes = json_data['SpecialEffectData']

        appearCharacters = json_data['AppearCharacters']
        chara_id = set()
        for chara in appearCharacters:
            chara2dId = chara['Character2dId']
            chara2d = self.character2ds[self.character2ds_lookup.find_index(chara2dId)]
            if chara2d['characterId'] in CHARA_ID_UNIT_AND_NAME:
                chara_id.add(chara2d['characterId'])
        chara_id_list = sorted(chara_id)

        if len(chara_id_list) > 0:
            ret += (
                '（登场角色：'
                + '、'.join(
                    [CHARA_ID_UNIT_AND_NAME[id].split('_')[1] for id in chara_id_list]
                )
                + '）\n\n'
            )

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
                    ret += (
                        '（全屏幕文字）：' + scene['StringVal'].replace('\n', '') + '\n'
                    )
                    next_talk_need_newline = False
            elif script['Action'] == 1:
                talk = talks[script['ReferenceIndex']]

                if next_talk_need_newline:
                    ret += '\n'
                ret += (
                    talk['WindowDisplayName']
                    + '：'
                    + talk['Body'].replace('\n', '')
                    + '\n'
                )
                next_talk_need_newline = False

        return ret[:-1]


class Event_story_getter:
    def __init__(self, reader: Story_reader) -> None:
        if reader.lang == 'cn':
            events_url = (
                'https://sekai-world.github.io/sekai-master-db-cn-diff/events.json'
            )
            eventStories_url = 'https://sekai-world.github.io/sekai-master-db-cn-diff/eventStories.json'
            self.asset_url = 'https://storage.sekai.best/sekai-cn-assets/event_story/{assetbundleName}/scenario/{scenarioId}.asset'
        elif reader.lang == 'jp':
            events_url = (
                'https://sekai-world.github.io/sekai-master-db-diff/events.json'
            )
            eventStories_url = (
                'https://sekai-world.github.io/sekai-master-db-diff/eventStories.json'
            )
            self.asset_url = 'https://storage.sekai.best/sekai-jp-assets/event_story/{assetbundleName}/scenario/{scenarioId}.asset'
        else:
            raise NotImplementedError

        res = requests.get(events_url, proxies=PROXY)
        res.raise_for_status()
        self.events_json: list[dict[str, Any]] = res.json()

        res = requests.get(eventStories_url, proxies=PROXY)
        res.raise_for_status()
        self.eventStories_json: list[dict[str, Any]] = res.json()

        self.events_lookup = DictLookup(self.events_json, 'id')
        self.eventStories_lookup = DictLookup(self.eventStories_json, 'eventId')

        self.reader = reader

    def get(self, event_id: int) -> None:

        event_index = self.events_lookup.find_index(event_id)
        eventStory_index = self.eventStories_lookup.find_index(event_id)

        if (event_index == -1) or (eventStory_index == -1):
            print(f'event {event_id} does not exist.')
            return

        event = self.events_json[event_index]
        eventStory = self.eventStories_json[eventStory_index]

        event_name = event['name']
        event_type = event['eventType']
        event_unit = event['unit']
        assetbundleName = event['assetbundleName']
        banner_chara_id = eventStory['bannerGameCharacterUnitId']
        event_outline = eventStory['outline'].replace('\n', '')

        if event_type == 'world_bloom':
            if event_unit == 'none':
                event_unit = 'piapro'
            banner_name = f'{UNIT_CODE_NAME[event_unit]}_WL'
        else:
            banner_name = (
                CHARA_ID_UNIT_AND_NAME | EXTRA_CHARA_ID_UNIT_AND_NAME_FOR_BANNER
            )[banner_chara_id]

        event_filename = valid_filename(event_name)
        save_folder_name = f'{event_id} {event_filename}（{banner_name}）'

        if self.reader.lang != 'cn':
            save_folder_name = self.reader.lang + '-' + save_folder_name

        event_save_dir = os.path.join(EVENT_SAVE_DIR, save_folder_name)

        os.makedirs(event_save_dir, exist_ok=True)

        for episode in eventStory['eventStoryEpisodes']:
            episode_name = (
                f"{episode['eventStoryId']}-{episode['episodeNo']} {episode['title']}"
            )
            if event_type == 'world_bloom':
                gameCharacterId = episode.get('gameCharacterId', -1)
                if gameCharacterId != -1:
                    chara_name = CHARA_ID_UNIT_AND_NAME[gameCharacterId].split('_')[1]
                    episode_name += f"（{chara_name}）"

            scenarioId = episode['scenarioId']

            res = requests.get(
                self.asset_url.format(
                    assetbundleName=assetbundleName, scenarioId=scenarioId
                ),
                proxies=PROXY,
            )
            res.raise_for_status()
            story_json: dict[str, Any] = res.json()

            text = self.reader.read_story_in_json(story_json)

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
    def __init__(self, reader: Story_reader) -> None:
        if reader.lang == 'cn':
            unitProfiles_url = 'https://sekai-world.github.io/sekai-master-db-cn-diff/unitProfiles.json'
            unitStories_url = (
                'https://sekai-world.github.io/sekai-master-db-cn-diff/unitStories.json'
            )
            self.asset_url = 'https://storage.sekai.best/sekai-cn-assets/scenario/unitstory/{assetbundleName}/{scenarioId}.asset'
        elif reader.lang == 'jp':
            unitProfiles_url = (
                'https://sekai-world.github.io/sekai-master-db-diff/unitProfiles.json'
            )
            unitStories_url = (
                'https://sekai-world.github.io/sekai-master-db-diff/unitStories.json'
            )
            self.asset_url = 'https://storage.sekai.best/sekai-jp-assets/scenario/unitstory/{assetbundleName}/{scenarioId}.asset'
        else:
            raise NotImplementedError

        res = requests.get(unitProfiles_url, proxies=PROXY)
        res.raise_for_status()
        self.unitProfiles_json: list[dict[str, Any]] = res.json()

        res = requests.get(unitStories_url, proxies=PROXY)
        res.raise_for_status()
        self.unitStories_json: list[dict[str, Any]] = res.json()

        self.reader = reader

    def get(self, unit_id: int) -> None:
        for unitProfile in self.unitProfiles_json:
            if unitProfile['seq'] == unit_id:
                unitName = unitProfile['unitName']
                unitCode = unitProfile['unit']
                unit_outline = unitProfile['profileSentence']
                break
        else:
            print(f'unit {unit_id} does not exist.')
            return

        for unitStory in self.unitStories_json:
            if unitStory['seq'] == unit_id:
                assetbundleName = unitStory['chapters'][0]['assetbundleName']
                episodes = unitStory['chapters'][0]['episodes']
                break
        else:
            print(f'unit {unit_id} does not exist.')
            return

        unit_filename = valid_filename(unitName)
        save_folder_name = f'{unit_id} {unit_filename}'

        if self.reader.lang != 'cn':
            save_folder_name = self.reader.lang + '-' + save_folder_name

        unit_save_dir = os.path.join(UNIT_SAVE_DIR, save_folder_name)
        os.makedirs(unit_save_dir, exist_ok=True)

        for episode in episodes:
            episode_name = (
                f"{UNIT_CODE_NAME[unitCode]}-{episode['episodeNo']} {episode['title']}"
            )
            scenarioId = episode['scenarioId']
            res = requests.get(
                self.asset_url.format(
                    assetbundleName=assetbundleName, scenarioId=scenarioId
                ),
                proxies=PROXY,
            )
            res.raise_for_status()
            story_json: dict[str, Any] = res.json()

            text = self.reader.read_story_in_json(story_json)

            filename = valid_filename(episode_name)

            with open(
                os.path.join(unit_save_dir, filename) + '.txt', 'w', encoding='utf8'
            ) as f:
                if episode['episodeNo'] == 1:
                    f.write(unit_outline + '\n\n')
                f.write(episode_name + '\n\n')
                f.write(text + '\n')

            print(f'get unit {unit_id} {unitName} {episode_name} done.')


class Card_story_getter:
    def __init__(self, reader: Story_reader) -> None:
        if reader.lang == 'cn':
            cards_url = (
                'https://sekai-world.github.io/sekai-master-db-cn-diff/cards.json'
            )
            cardEpisodes_url = 'https://sekai-world.github.io/sekai-master-db-cn-diff/cardEpisodes.json'
            self.asset_url = 'https://storage.sekai.best/sekai-cn-assets/character/member/{assetbundleName}/{scenarioId}.asset'
        elif reader.lang == 'jp':
            cards_url = 'https://sekai-world.github.io/sekai-master-db-diff/cards.json'
            cardEpisodes_url = (
                'https://sekai-world.github.io/sekai-master-db-diff/cardEpisodes.json'
            )
            self.asset_url = 'https://storage.sekai.best/sekai-jp-assets/character/member/{assetbundleName}/{scenarioId}.asset'
        else:
            raise NotImplementedError

        res = requests.get(cards_url, proxies=PROXY)
        res.raise_for_status()
        self.cards_json: list[dict[str, Any]] = res.json()

        res = requests.get(cardEpisodes_url, proxies=PROXY)
        res.raise_for_status()
        self.cardEpisodes_json: list[dict[str, Any]] = res.json()

        self.cards_lookup = DictLookup(self.cards_json, 'id')
        self.cardEpisodes_lookup = DictLookup(self.cardEpisodes_json, 'cardId')

        self.reader = reader

    def get(self, card_id: int) -> None:
        card_index = self.cards_lookup.find_index(card_id)
        cardEpisode_index = self.cardEpisodes_lookup.find_index(card_id)

        if (card_index == -1) or (cardEpisode_index == -1):
            print(f'card {card_id} does not exist.')
            return

        card = self.cards_json[card_index]
        cardEpisode_1 = self.cardEpisodes_json[cardEpisode_index]
        cardEpisode_2 = self.cardEpisodes_json[cardEpisode_index + 1]

        chara_unit_and_name = CHARA_ID_UNIT_AND_NAME[card['characterId']]
        chara_name = chara_unit_and_name.split('_')[1]
        cardRarityType = RARITY_NAME[card['cardRarityType']]
        card_name = card['prefix']
        sub_unit = card['supportUnit']
        assetbundleName: str = card['assetbundleName']
        card_id_for_chara = int(assetbundleName.split('_')[1][2:])

        story_1_name = cardEpisode_1['title']
        story_2_name = cardEpisode_2['title']
        story_1_scenarioId = cardEpisode_1['scenarioId']
        story_2_scenarioId = cardEpisode_2['scenarioId']

        card_save_dir = os.path.join(CARD_SAVE_DIR, chara_unit_and_name)
        os.makedirs(card_save_dir, exist_ok=True)

        res = requests.get(
            self.asset_url.format(
                assetbundleName=assetbundleName, scenarioId=story_1_scenarioId
            ),
            proxies=PROXY,
        )
        res.raise_for_status()
        story_1_json: dict[str, Any] = res.json()
        text_1 = self.reader.read_story_in_json(story_1_json)

        res = requests.get(
            self.asset_url.format(
                assetbundleName=assetbundleName, scenarioId=story_2_scenarioId
            ),
            proxies=PROXY,
        )
        res.raise_for_status()
        story_2_json: dict[str, Any] = res.json()
        text_2 = self.reader.read_story_in_json(story_2_json)

        if sub_unit != 'none':
            sub_unit_name = f'（{UNIT_CODE_NAME[sub_unit]}）'
        else:
            sub_unit_name = ''

        card_story_filename = valid_filename(
            f'{card_id}_{chara_name}{sub_unit_name}_{card_id_for_chara}_{cardRarityType} {card_name}'
        )

        if self.reader.lang != 'cn':
            card_story_filename = self.reader.lang + '-' + card_story_filename

        with open(
            os.path.join(card_save_dir, card_story_filename) + '.txt',
            'w',
            encoding='utf8',
        ) as f:
            f.write(
                f'{chara_name}{sub_unit_name}-{card_id_for_chara} {card_name}\n\n\n'
            )
            f.write(story_1_name + '\n\n')
            f.write(text_1 + '\n\n\n')
            f.write(story_2_name + '\n\n')
            f.write(text_2 + '\n')

        print(f'get card {card_story_filename} done.')


class DictLookup:
    def __init__(self, data: list[dict[str, Any]], attr_name: str):
        self.data = data
        self.ids = [int(d[attr_name]) for d in data]

    def find_index(self, target_id: int) -> int:
        left_index = bisect.bisect_left(self.ids, target_id)
        if left_index < len(self.ids) and self.ids[left_index] == target_id:
            return left_index
        return -1


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
    reader = Story_reader()
    unit_getter = Unit_story_getter(reader)
    event_getter = Event_story_getter(reader)
    card_getter = Card_story_getter(reader)

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(unit_getter.get, range(1, 7))
        executor.map(event_getter.get, range(1, 140))
        executor.map(card_getter.get, range(1, 108))
        executor.map(card_getter.get, range(724, 760))
