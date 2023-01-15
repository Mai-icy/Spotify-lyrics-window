#!/usr/bin/python
# -*- coding:utf-8 -*-

class NoneResultError(ValueError):
    """api返回的数据是空（搜索的关键词没有对应的数据）"""


class UserError(Exception):
    """与用户相关的api错误"""


class NoDevicesError(UserError):
    """没有活跃设备"""


class NoPermission(UserError):
    """没有Premium会员权限"""


class NoActiveUser(UserError):
    """没有活跃用户"""


class NoAuthError(UserError):
    """未完成授权"""
