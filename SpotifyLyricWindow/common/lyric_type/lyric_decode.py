#!/usr/bin/python
# -*- coding:utf-8 -*-
import codecs
from enum import Enum
import zlib
import json
import base64
import re


class TransType(Enum):
    NON = 0
    ROMAJI = 1
    CHINESE = 2


class LrcFile:

    def __init__(self, file_path=None, lrc_type: TransType = TransType.NON):
        self.trans_non_dict = {}
        self.trans_romaji_dict = {}
        self.trans_chinese_dict = {}
        if file_path:
            self.load_file_path(file_path, lrc_type)

    def __select_lrc_type(self, lrc_type: TransType) -> dict:
        """
        Get the bound dict.

        :return: Returns a reference to the corresponding dict.
        """
        if lrc_type == TransType.NON:
            target_dict = self.trans_non_dict
        elif lrc_type == TransType.ROMAJI:
            target_dict = self.trans_romaji_dict
        elif lrc_type == TransType.CHINESE:
            target_dict = self.trans_chinese_dict
        else:
            raise ValueError("lrc_type must be TransType.")
        return target_dict

    def load_content(self, content: str, lrc_type: TransType) -> bool:
        """
        Parse lyric data in incoming text.

        :return:
        """
        target_dict = self.__select_lrc_type(lrc_type)
        target_dict.clear()
        file_data = content.splitlines()
        for line in file_data:
            if re.match(r'\[\d\d:\d\d.\d+]', line):
                if line[9] == ']':
                    moment = int(line[1:3]) * 60000 + \
                             int(line[4:6]) * 1000 + int(line[7:9]) * 10
                    context = line[10:]
                elif line[10] == ']':
                    moment = int(line[1:3]) * 60000 + \
                             int(line[4:6]) * 1000 + int(line[7:10])
                    context = line[11:]
                else:
                    end = line.find(']')
                    moment_text_list = re.split('[:.]', line[1:end])
                    moment = int(moment_text_list[0]) * 60000 + \
                             int(moment_text_list[1]) * 1000 + int(moment_text_list[2])
                    context = line[end + 1:]
                target_dict[moment] = context
        # 同步
        if self.trans_non_dict.keys():
            if self.trans_romaji_dict.keys():
                time_list = [x for x in self.trans_non_dict.keys() if x not in self.trans_romaji_dict.keys()]
                for i in time_list:
                    self.trans_romaji_dict[i] = ''

            if self.trans_chinese_dict.keys():
                time_list = [x for x in self.trans_non_dict.keys() if x not in self.trans_chinese_dict.keys()]
                for i in time_list:
                    self.trans_chinese_dict[i] = ''

        return True

    def load_file_path(self, path: str, lrc_type: TransType):
        """
        Parse the lyric data in the path file.

        :return:
        """
        text = open(path, 'r', encoding='utf-8').read()
        self.load_content(text, lrc_type)

    def get_content(self, lrc_type: TransType = TransType.NON) -> str:
        """

        :return: If there is no data for this type, return ''.
        """
        target_dict = self.__select_lrc_type(lrc_type)

        if not target_dict:
            return ''

        time_list = sorted(target_dict.keys())

        res_file_content = ""
        for time_ in time_list:
            time_stamp = "[%s:%s:%s]" % (str(time_ // 60000).zfill(2),
                                         str(time_ % 60000 // 1000).zfill(2),
                                         str(time_ % 1000).zfill(3))
            res_file_content += time_stamp + target_dict[time_] + '\n'
        return res_file_content

    def save_to_lrc(self, save_path: str, lrc_type: TransType) -> bool:
        """
        Save as an LRC file

        :return: If there is no data for this type, return false.
        """
        res_file_content = self.get_content(lrc_type)
        fp = codecs.open(save_path, "w", encoding='utf-8')
        fp.write(res_file_content)
        fp.close()
        return True

    def save_to_mrc(self, save_path: str) -> bool:
        non_text = self.get_content(TransType.NON)
        romaji_text = self.get_content(TransType.ROMAJI)
        chinese_text = self.get_content(TransType.CHINESE)

        res_file_text = ''
        if non_text:
            res_file_text += "-*- type:non -*-\n" + non_text + '\n'
        if romaji_text:
            res_file_text += "-*- type:romaji -*-\n" + romaji_text + '\n'
        if chinese_text:
            res_file_text += "-*- type:chinese -*-\n" + chinese_text + '\n'
        file = open(save_path, 'w', encoding='utf-8')
        file.write(res_file_text)
        file.close()
        return True

    def get_time(self, order: int) -> int:
        """
        Get the time of order in dict.

        :param order:
        :return: the time.
        """
        if self.trans_non_dict:
            time_list = list(self.trans_non_dict.keys())
        elif self.trans_chinese_dict:
            time_list = list(self.trans_chinese_dict.keys())
        elif self.trans_romaji_dict:
            time_list = list(self.trans_romaji_dict.keys())
        else:
            return -1
        if order >= len(time_list):
            return -2
        return time_list[order]

    def get_order_position(self, time_position: int) -> int:
        """
        Gets the last order of time label in time_list closest to the time.

        :param time_position:
        :return: Return -1 if none, Return the length of the time_list if it is greater than all times
        """
        if self.trans_non_dict:
            time_list = list(self.trans_non_dict.keys())
        elif self.trans_chinese_dict:
            time_list = list(self.trans_chinese_dict.keys())
        elif self.trans_romaji_dict:
            time_list = list(self.trans_romaji_dict.keys())
        else:
            return -1
        time_list.sort()

        if time_position < time_list[0]:
            return 0

        for order in range(len(time_list)):
            if time_position < time_list[order]:
                return order - 1
        else:
            return len(time_list)

    def available_trans(self) -> list:
        available_trans_list = [TransType.NON]
        if not self.empty(TransType.ROMAJI):
            available_trans_list.append(TransType.ROMAJI)
        if not self.empty(TransType.CHINESE):
            available_trans_list.append(TransType.CHINESE)
        return available_trans_list

    def empty(self, lrc_type: TransType = TransType.NON) -> bool:
        target_dict = self.__select_lrc_type(lrc_type)
        if not target_dict:
            return True


class KrcFile(LrcFile):
    """
    Read KRC files and decode them
    """

    @staticmethod
    def __decode(file_data: bytes, sec_decimal: int = 3) -> str:
        """
        Decoding KRC

        :param file_data: Specifies the data to read
        :param sec_decimal: The number of seconds inside the file
        :return: Decoded text
        """
        krc_bytes = bytearray(file_data)
        key = bytearray([0x0040,
                         0x0047,
                         0x0061,
                         0x0077,
                         0x005e,
                         0x0032,
                         0x0074,
                         0x0047,
                         0x0051,
                         0x0036,
                         0x0031,
                         0x002d,
                         0x00ce,
                         0x00d2,
                         0x006e,
                         0x0069])
        decompress_bytes = []
        i = 0
        for ch in krc_bytes[4:]:
            decompress_bytes.append(ch ^ key[i % 16])
            i = i + 1
        decode_bytes = zlib.decompress(
            bytearray(decompress_bytes)).decode('utf-8-sig')
        decode_bytes = re.sub(r'<[^>]*>', '', decode_bytes)
        for match in re.finditer(r'\[(\d*),\d*]', decode_bytes):
            ms = int(match.group(1))
            if sec_decimal == 3:
                time = '[%.2d:%.2d.%.3d]' % ((ms % (
                        1000 * 60 * 60)) / (1000 * 60), (ms % (1000 * 60)) / 1000, (ms % (1000 * 60)) % 1000)
            elif sec_decimal == 2:
                time = '[%.2d:%.2d.%.2d]' % ((ms % (1000 * 60 * 60)) / (
                        1000 * 60), (ms % (1000 * 60)) / 1000, (ms % (1000 * 60)) // 10 % 100)
            else:
                raise ValueError("sec_decimal must be 2 or 3.")
            decode_bytes = decode_bytes.replace(match.group(0), time)
        return decode_bytes

    def load_content(self, content: bytes, lrc_type: TransType = TransType.NON):
        """
        Get the text of lyric.
        """
        try:
            decoded_content = self.__decode(content)
        except zlib.error:
            decoded_content = content.decode("utf-8")
        super(KrcFile, self).load_content(decoded_content, lrc_type)

        file_data = decoded_content.splitlines()
        information_dict = {}
        for line in file_data:
            if re.match(r'\[(\D+):(\S*)]', line):
                text = re.match(r'\[(\D+):(\S*)]', line)
                key = text.group(1)
                context = text.group(2)
                information_dict[key] = context

        trans_romaji_list = []
        trans_chinese_list = []
        if 'language' in information_dict.keys():
            translation_dict = json.loads(base64.b64decode(
                (information_dict['language'])).decode())
            for language_type_dict in translation_dict['content']:
                if language_type_dict['type'] == 0:  # 罗马音翻译
                    for sentence in language_type_dict['lyricContent']:
                        res_sentence = ''
                        for romaji in sentence:
                            res_sentence += romaji
                        trans_romaji_list.append(res_sentence)
                if language_type_dict['type'] == 1:  # 中文翻译
                    for sentence in language_type_dict['lyricContent']:
                        trans_chinese_list.append(sentence[0])

        for index, time_ in enumerate(self.trans_non_dict.keys()):
            if trans_romaji_list:
                self.trans_romaji_dict[time_] = trans_romaji_list[index]
            if trans_chinese_list:
                self.trans_chinese_dict[time_] = trans_chinese_list[index]

    def load_file_path(self, path: str, lrc_type: TransType = TransType.NON):
        text_byte = open(path, 'rb').read()
        self.load_content(text_byte, lrc_type)


class MrcFile(LrcFile):

    def load_content(self, content: str, lrc_type: TransType) -> bool:
        file_data = content.splitlines()

        lrc_content = ''
        lrc_type = ''

        for line in file_data:
            res = re.match(r"-\*- type:(.*) -\*-", line)
            if res:
                if lrc_content and lrc_type:
                    super(MrcFile, self).load_content(lrc_content, lrc_type)
                    lrc_content = ''
                lrc_type = getattr(TransType, res.groups()[0].upper())
            else:
                lrc_content += line + '\n'
        if lrc_content and lrc_type:
            super(MrcFile, self).load_content(lrc_content, lrc_type)

        return True


if __name__ == "__main__":
    a = MrcFile("..//..//download//lyrics//6Xl3ty4oPbccRS9ehumXID.mrc")
    print(a.trans_romaji_dict)
    print(a.trans_non_dict)
    print(a.trans_chinese_dict)
