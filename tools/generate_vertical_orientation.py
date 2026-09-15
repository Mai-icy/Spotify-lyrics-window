#!/usr/bin/python
# -*- coding:utf-8 -*-
"""从官方 VerticalOrientation.txt 生成压缩后的 Unicode 竖排数据表。

来源：https://www.unicode.org/Public/17.0.0/ucd/VerticalOrientation.txt
用法：python tools/generate_vertical_orientation.py /path/to/VerticalOrientation.txt
输出用于更新 SpotifyLyricWindow/common/ui/vertical_orientation_data.py，应用运行时不下载数据。
"""
import hashlib
from pathlib import Path
import re
import sys


def generate(source):
    """读取官方数据，合并相邻的同方向区间并输出 Python 模块。"""
    data = source.read_bytes()
    text = data.decode('utf-8')
    version = re.search(r'^# VerticalOrientation-([\d.]+)\.txt', text).group(1)
    assert '# @missing: 0000..10FFFF; R' in text
    ranges = []
    for line in text.splitlines():
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        points, orientation = (part.strip() for part in line.split(';'))
        assert orientation in ('U', 'R', 'Tu', 'Tr')
        if orientation == 'R':
            continue  # 未列出的码点统一使用默认方向 R。
        bounds = points.split('..')
        start, end = int(bounds[0], 16), int(bounds[-1], 16)
        if ranges and ranges[-1][1] + 1 == start and ranges[-1][2] == orientation:
            ranges[-1] = (ranges[-1][0], end, orientation)
        else:
            ranges.append((start, end, orientation))
    header = (
        '#!/usr/bin/python\n'
        '# -*- coding:utf-8 -*-\n'
        '# 由 tools/generate_vertical_orientation.py 生成，请勿手动修改。\n'
        '# UAX #50: https://www.unicode.org/reports/tr50/\n'
        f'# Source: https://www.unicode.org/Public/{version}/ucd/VerticalOrientation.txt\n'
        f'# Source SHA-256: {hashlib.sha256(data).hexdigest()}\n'
        '# 数据来自 Unicode，许可证见项目根目录 licenses/UNICODE-LICENSE.txt。\n'
        f'UNICODE_VERSION = {version!r}\n\n'
        '# 非 R 方向的闭区间，其余码点默认方向为 R。\n'
        'ORIENTATION_RANGES = (\n'
    )
    return header + ''.join(f'    (0x{start:X}, 0x{end:X}, {vo!r}),\n'
                            for start, end, vo in ranges) + ')\n'


if __name__ == '__main__':
    print(generate(Path(sys.argv[1])), end='')
