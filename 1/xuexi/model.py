#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: model.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-08-01(星期四) 17:24
@Copyright © 2019. All rights reserved.
'''
from pathlib import Path
import re
import json
from sqlalchemy import Column,Integer, String, Text, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from lxml import etree
from . import logger


# 创建对象的基类:
Base = declarative_base()

# 定义Bank对象:
class Bank(Base):
    # 表的名字:
    __tablename__ = 'banks'

    '''表的结构:
        id | catagory | content | options[item0, item1, item2, item3] | answer | note | bounds
        序号 | 题型 | 题干 | 选项 | 答案 | 注释 | 位置(保存时丢弃)
    '''
    id = Column(Integer,primary_key=True)
    catagory = Column(String(128), default='radio') # radio check blank challenge
    content = Column(Text, default='content')
    # options的处理，每个item用空格分隔开，若item本身包含空格，则replace为顿号(、)
    options = Column(Text, default='')
    answer = Column(String(256), nullable=True, default='')
    note = Column(Text, nullable=True, default='')
    bounds = Column(String(128), nullable=True, default='')

    def __init__(self, catagory, content, options, answer, note, bounds):
        self.catagory = catagory or 'radio' # 挑战答题-挑战题, 每日答题-单选题、多选题、填空题
        self.content = content or 'default content'
        self.options = options or ''
        self.answer = answer.upper() or ''
        self.note = note or ''
        self.bounds = bounds or ''

    def __repr__(self):
        return f'<Bank {self.content}>'

    def __str__(self):
        maxlen = 42
        if len(self.content) > maxlen:
            content = f'{self.content[:maxlen]}...'
        else:
            content = self.content
        content = re.sub(r'\s', '_', content)
        options = ''
        if self.options:
            options = f'O: {self.options}\n'
        return f'I: {self.id} {self.catagory}\nQ: {content:<50}\n{options}A: {self.answer}\n'

    def __eq__(self, other):
        return self.content == other.content
    
    @classmethod
    def from_challenge(cls, content, options='', answer='', note='', bounds=''):
        str_options = '|'.join(options)
        return cls(catagory='挑战题', content=content, options=str_options, answer=answer, note=note, bounds=bounds)

    @classmethod
    def from_daily(cls, catagory, content, options, answer, note):
        return cls(catagory=catagory, content=content, options=options, answer=answer, note=note, bounds='')

    def to_array(self):
        options = self.options.split('|')
        array_bank = [self.id, self.answer, self.content]
        array_bank.extend(options)
        # array_bank.append(self.note)
        return array_bank

    def to_dict(self):
        json_bank = {
            "id": self.id,
            "catagory": self.catagory,
            "content": self.content,
            "options": self.options,
            "answer": self.answer,
            "note": self.note
        }
        return json_bank

    @classmethod
    def from_dict(cls, data):
        return cls(data['catagory'], data['content'], re.sub(r'\s', '|', re.sub(r'|', '', data['options'])), data['answer'], data['note'], '')

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer,primary_key=True)
    title = Column(Text, index=True, default='title')

    def __repr__(self):
        return f'{self.title}'

    def __str__(self):
        return f'[{self.id}] {self.title}'


class Model():
    def __init__(self, database_uri):
        # 初始化数据库连接:
        engine = create_engine(database_uri)
        # 创建DBSession类型:
        Session = sessionmaker(bind=engine)

        Base.metadata.create_all(engine)
        self.session = Session()

    def query(self, id=None, content=None, catagory='挑战题 单选题 多选题 填空题'):
        '''数据库检索记录'''
        catagory = catagory.split(' ')
        if id and isinstance(id, int):
            return self.session.query(Bank).filter_by(id=id).one_or_none()
        if content and isinstance(content, str):
            content = re.sub(r'\s+', '%', content)
            return self.session.query(Bank).filter(Bank.catagory.in_(catagory)).filter(Bank.content.like(content)).one_or_none()
        return self.session.query(Bank).filter(Bank.catagory.in_(catagory)).all()

    def add(self, item):
        '''数据库添加纪录'''
        result = self.query(content=item.content, catagory=item.catagory)
        if result:
            logger.info(f'数据库已存在此纪录，无需添加纪录！')
        else:
            self.session.add(item)
            self.session.commit()
            logger.info(f'数据库添加记录成功！')

    def has_article(self, title):
        return self.session.query(Article).filter_by(title=title).one_or_none() is not None

    def print_arcitles(self):
        items = self.session.query(Article).all()
        for item in items:
            print(item)

    def len_articles(self):
        return len(self.session.query(Article).all())
    
    def add_article(self, title):
        if '' == title:
            raise ValueError('文章标题不能为空')
        if self.has_article(title):
            raise RuntimeError('文章标题已在数据库中')
        else:
            article = Article(title=title)
            self.session.add(article)
            self.session.commit()
            logger.info(f'数据库添加成功！ {title}')

    # def delete(self, item):
    #     '''数据库删除记录'''
    #     to_del = self.qeury(content=item.content)
    #     if to_del:
    #         session.delete(to_del)
    #         session.commit()
    #     else:
    #         logger.info('数据库无此纪录!')

    # def temp_del(self, id):
    #     to_del = self.query(id=id)
    #     self.session.delete(to_del)
    #     self.session.commit()

    # def update(self, id, answer):
    #     '''数据库更新记录'''
    #     to_update = self.query(id=id)
    #     if to_update:
    #         to_update.answer = answer
    #         session.commit()
    #         logger.info(f'更新题目[{id}]的答案为“{answer}”')
    #     else:
    #         logger.info('数据库无此纪录!')

    def _to_json(self, path, catagory='挑战题 单选题 多选题 填空题'):
        datas = self.query(catagory=catagory)
        # logger.debug(len(datas))
        output = [data.to_dict() for data in datas]
        with open(path,'w',encoding='utf-8') as fp:
            json.dump(output,fp,indent=4,ensure_ascii=False)
        logger.info(f'JSON数据{len(datas)}条成功导出{path}')
        return True

    def _from_json(self, path, catagory='挑战题 单选题 多选题 填空题'):
        if path.exists():
            with open(path,'r',encoding='utf-8') as fp:
                res = json.load(fp)
            for r in res:
                bank = Bank.from_dict(r)
                if '填空题' == bank.catagory:
                    if str(len(bank.answer.split(' '))) != bank.options:
                        continue
                self.add(bank)
            logger.info(f'JSON数据成功导入{path}')
            return True
        else:
            logger.debug(f'JSON数据{path}不存在')
            return False
    
    def _to_md(self, path, catagory='挑战题'):
        items = db.query(catagory=catagory)
        with open(path, 'w', encoding='utf-8') as fp:
            fp.write(f'# 学习强国 挑战答题 题库 {len(items):>4} 题\n')
            for item in items:
                content = re.sub(r'\s\s+', '\_\_\_\_',re.sub(r'[\(（]出题单位.*', '', item.content))
                options = "\n\n".join([f'+ **{x}**' if i==ord(item.answer)-65 else f'+ {x}' for i, x in enumerate(item.options.split('|'))])
                fp.write(f'{item.id}. {content}  *{item.answer}*\n\n{options}\n\n')
        with open(path.with_name('data-grid.md'), 'w', encoding='utf-8') as fp2:
            fp2.write(f'# 学习强国 挑战答题 题库 {len(items):>4} 题\n')
            fp2.write(f'|序号|答案|题干|选项A|选项B|选项C|选项D|\n')
            fp2.write(f'|:--:|:--:|--------|----|----|----|----|\n')
            for item in items:
                content = re.sub(r'\s\s+', '\_\_\_\_',re.sub(r'[\(（]出题单位.*', '', item.content))
                options = " | ".join([f'**{x}**' if i==ord(item.answer)-65 else f'{x}' for i, x in enumerate(item.options.split('|'))])
                fp2.write(f'| {item.id} | {item.answer} | {content} | {options} |\n')
            
        return 0

    def _to_xls(self, path, catagory='挑战题 单选题 多选题 填空题'):
        from .common import xlser
        data = self.query(catagory=catagory)
        xs = xlser.Xlser(path)
        xs.save(data)

    def upload(self, path, catagory='挑战题 单选题 多选题 填空题'):
        if '.json' == path.suffix:
            self._from_json(path, catagory)
        elif path.suffix not in ('.xls', '.xlsx'):
            logger.info(f'不被支持的文件类型: {path.suffix}')
    
    def download(self, path, catagory='挑战题 单选题 多选题 填空题'):
        ext = path.suffix
        if '.json' == ext:
            self._to_json(path, catagory)
        elif ext in ('.xls', '.xlsx'):
            self._to_xls(path, catagory)
        elif '.md' == ext:
            self._to_md(path, catagory)
        else:
            logger.info(f'不被支持的文件类型: {ext}')



if __name__ == "__main__":
    from argparse import ArgumentParser
    from . import logger
    logger.debug('running __main__')


    parse = ArgumentParser()
    parse.add_argument(dest='filename', metavar='filename', nargs="?", type=str, help='目标文件路径')
    parse.add_argument('-b', '--behavior', metavar='behavior', type=str, default='download', help='数据库操作，upload、download')
    parse.add_argument('-c', '--catagory', metavar='catagory', type=str, default='挑战题 单选题 多选题 填空题', help='题型：挑战题、单选题、多选题、填空题')
    parse.add_argument('-d', '--display', metavar='display', nargs='?', const=True, type=bool, default=False, help='打印')
    parse.add_argument('-l', '--articles', metavar='articles', nargs='?', const=True, type=bool, default=False, help='打印已阅文章列表')
    args = parse.parse_args()

    db = Model('sqlite:///./xuexi/data-dev.sqlite')
    if args.filename:
        # print(f'选中题型：{args.catagory}')
        path = Path(args.filename)
        if 'download' == args.behavior:
            db.download(path, catagory=args.catagory)
        elif 'upload' == args.behavior:
            db.upload(path, catagory=args.catagory)
        else:
            pass
    else:
        if args.display:
            data = db.query(catagory=args.catagory)
            for d in data:
                print(d)
            print(f'题目数 {len(data)}题')
        elif args.articles:
            db.print_arcitles()
        else:
            print('''使用说明：\n\tpython -m xuexi.model filename -b [upload|download] -c [挑战题|填空题|单选题|多选题]\n\teg.\n\t\tpython -m xuexi.common.model ./xuexi/src/json/daily.json -b upload\n\t\tpython -m xuexi.common.model ./xuexi/output.json\n''')
            data = db.query()
            print(f'文章数 {db.len_articles():>4}篇\n题目数 {len(data):>4}题')
            for catagory in ['挑战题', '填空题', '单选题', '多选题']:
                data = db.query(catagory=catagory)
                print(f'{catagory} {len(data):>4}题')


