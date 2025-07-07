import argparse
import string
import urllib.parse

from collections import namedtuple
from typing import Any

import esprima  # type: ignore
import lxml.html
import requests

from lxml.etree import _Element as Element

INFO_BASE_URL = 'https://www.law.go.kr/LSW/lsInfoP.do'
BODY_BASE_URL = 'https://www.law.go.kr/LSW/lsInfoR.do'

# https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsNwInfoGuide
LawInfo = namedtuple('LawInfo', ['MST', 'LD'], defaults=[None, None])

def get_url(base_url: str, query: list[tuple[str, str]]) -> str:
    url_obj = urllib.parse.urlparse(base_url)
    query_str = urllib.parse.urlencode(query)
    url_obj = url_obj._replace(query=query_str)
    url = urllib.parse.urlunparse(url_obj)
    return url

def get_info_url(name: str) -> str:
    url = get_url(INFO_BASE_URL, [('lsNm', name)])
    return url

def get_body_url(info: LawInfo) -> str:
    url = get_url(BODY_BASE_URL, [('lsiSeq', info.MST), ('efYd', info.LD)])
    return url

def get_text(url: str) -> str:
    response = requests.get(url)
    text = response.text
    return text

def get_html(url: str) -> Element:
    response = requests.get(url)
    text = response.text
    html = lxml.html.fromstring(text)
    return html

def remove_element(element: Element) -> None:
    parent = element.getparent()
    if not parent:
        return
    parent.remove(element)

def clean_html(html: Element) -> None:
    for element in html.cssselect('script, style'):
        remove_element(element)

def get_html_text(url: str) -> str:
    response = requests.get(url)
    text = response.text
    html = lxml.html.fromstring(text)
    clean_html(html)
    text = html.text_content()  # type: ignore
    return text  # type: ignore

class CallVisitor(esprima.NodeVisitor):  # type: ignore
    target: str
    arguments: list[Any] | None
    def __init__(self, target: str) -> None:
        self.target = target
        self.arguments = None
    def visit_CallExpression(self, node: Any) -> None:
        callee = node.callee
        callee_type = callee.type
        if callee_type != 'Identifier':
            return
        callee_name = callee.name
        if callee_name != self.target:
            return
        arguments = node.arguments
        if any(argument.type != 'Literal' for argument in arguments):
            return
        arguments = list(argument.value for argument in arguments)
        self.arguments = arguments

def get_arguments(target: str, script: str) -> list[Any] | None:
    visitor = CallVisitor(target)
    tree = esprima.parseScript(script)
    visitor.visit(tree)
    return visitor.arguments

def get_info_old(html: Element) -> LawInfo:
    info = LawInfo()
    for element in html.cssselect('input[type="hidden"]'):
        html_id = element.get('id')
        if not html_id:
            continue
        html_value = element.get('value')
        if not html_value:
            continue
        if html_id == 'lsiSeq':
            info = info._replace(MST=html_value)
        elif html_id == 'ancYd':
            info = info._replace(LD=html_value)
        else:
            continue
    return info

def get_info(html: Element) -> LawInfo:
    info = LawInfo()
    for element in html.cssselect('script'):
        script = element.text
        if not script:
            continue
        arguments = get_arguments('lsPopViewAll2', script)
        if not arguments:
            continue
        seq, ancYd, ancNo, efYd, nwJoYnInfo, efGubun, chrClsCd ,ancYnChk = arguments
        info = info._replace(MST=seq)
        info = info._replace(LD=efYd)
    return info

# <toc>, <level>, <num>, <heading> are USLM (United States Legislative Markup)
# core elements
# https://xml.house.gov/

def get_level(num: str) -> str:
    num = num.strip(string.digits)
    num = num.removesuffix('의')
    return num[-1]

def get_toc(html: Element) -> str:
    toc = []
    stack: list[str] = []
    for element in html.cssselect('p.gtit, div.lawcon label'):
        text = element.text
        if not text:
            continue
        text = text.strip()
        big_level = element.tag == 'p'
        if big_level:
            num, heading = text.split(' ', 1)
        elif '(' in text:
            text = text.removesuffix(')')
            num, heading = text.split('(', 1)
        else:
            num = text
            heading = '(삭제)'
        level = get_level(num)
        if not stack:
            stack.append(level)
        elif level not in stack:
            if big_level and stack[-1] == '조':
                stack.pop()
            stack.append(level)
        else:
            while stack[-1] != level:
                stack.pop()
        indent = len(stack) - 1
        space = '  ' * indent
        toc.append(f'{space}{num} {heading}')
    toc_str = '\n'.join(toc)
    return toc_str

def main(name: str) -> None:
    info_url = get_info_url(name)
    info_html = get_html(info_url)
    info = get_info(info_html)
    body_url = get_body_url(info)
    body_html = get_html(body_url)
    toc = get_toc(body_html)
    print(toc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    main(args.name)
