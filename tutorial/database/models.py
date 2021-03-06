'''
Description: 
email: 359066432@qq.com
Author: lhj
software: vscode
Date: 2021-08-28 18:48:25
platform: windows 10
LastEditors: lhj
LastEditTime: 2021-09-02 21:49:39
'''
# -*- encoding: utf-8 -*-
"""
@File           : models.py
@Time           : 2021/8/28 18:48
@Author         : 林宏基
@Email          : 359066432@qq.com
@Software       : PyCharm
@Description    :
"""

import datetime, json
from typing import Text
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base



class DirectiveJsonEncoder(json.JSONEncoder):
    """
        应对datetime.datetime() 对象的序列化,参考:
        https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class Base(object):
    id = sa.Column(sa.Integer,primary_key=True)
    created = sa.Column(
        sa.DateTime,
        default=datetime.datetime.now,
        nullable=False,
        index=True,
    )
    updated = sa.Column(
        sa.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
        return json.dumps(self.as_dict(), ensure_ascii=False, cls=DirectiveJsonEncoder)


DeclarativeBase = declarative_base(cls=Base)

class China(DeclarativeBase):
    __tablename__ ="ChinaData"
    GuangDong = sa.Column(sa.Integer,nullable=True)
    GuangXi = sa.Column(sa.Integer,nullable=True)
    FuJian = sa.Column(sa.Integer, nullable=True)
    HaiNan = sa.Column(sa.Integer, nullable=True)
    TaiWan = sa.Column(sa.Integer, nullable=True)
    YunNan = sa.Column(sa.Integer, nullable=True)
    HeNan = sa.Column(sa.Integer, nullable=True)
    HeBei = sa.Column(sa.Integer, nullable=True)
    HuNan = sa.Column(sa.Integer, nullable=True)
    HuBei = sa.Column(sa.Integer, nullable=True)
    BeiJing = sa.Column(sa.Integer, nullable=True)
    ShangHai = sa.Column(sa.Integer, nullable=True)



class DouBanMovieComment(DeclarativeBase):
    __tablename__="DouBanPingFen"
    name = sa.Column(sa.String(64),nullable=False,index=True,unique=True)
    score = sa.Column(sa.FLOAT,nullable=True)
    summary =sa.Column(sa.String(64),nullable=True)
    score_update_time = sa.Column(sa.DateTime,default=datetime.datetime.now)


class GentleManResourceModel(DeclarativeBase):
    __tablename__="gentlemanresource"
    # series ID + ID
    flag = sa.Column(sa.String(64),nullable=False,index=True,unique=True)
    title = sa.Column(sa.String(64),nullable=True)
    url = sa.Column(sa.String(64),nullable=True)
    series_type = sa.Column(sa.String(64),nullable=True)
    series_id = sa.Column(sa.String(64),nullable=True)
    src_url = sa.Column(sa.String(64),nullable=True)
    local_uri = sa.Column(sa.String(64),nullable=True)



class GentleManMoveModel(DeclarativeBase):
    __tablename__="gentleman_movie"

    series = sa.Column(sa.String(64),nullable=False,index=True)
    title = sa.Column(sa.String(128),nullable=False)
    local_uri = sa.Column(sa.String(256),nullable=True)
    m3u8_index_url = sa.Column(sa.String(256),nullable=True,index=True)
    m3u8_ts_url_list = sa.Column(sa.JSON(),nullable=True)
    movie_src_url = sa.Column(sa.String(256),nullable=True)