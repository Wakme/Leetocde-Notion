import requests
import json
import logging
import os
import codeparser

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 切换目录到当前脚本下

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# handler2 = logging.StreamHandler()
# handler2.setLevel(logging.INFO)
# handler2.setFormatter(formatter)
#
# logger.addHandler(handler2)

with open("config.json", "r") as f:
    tmp = json.loads(f.read())
    token = tmp['token']
    database_id = tmp['database_id']

leetcode_url = 'https://leetcode-cn.com/problems/'


def submit_questions(questions):
    logger.info("待提交问题数量:" + str(len(questions)))
    cnt = 0
    with open("visited.json", "r") as f:
        visited = json.load(f)
    while True:
        if len(questions) == 0:
            break
        question = questions[0]
        if question['pid'] in visited:
            questions.remove(question)
            logger.error(question['fid'] + ". " + question['title'] + ": 已存在!")
            continue
        if submit_question(question):
            cnt += 1
            logger.info(question['fid'] + ". " + question['title'] + ": 提交成功")
            questions.remove(question)
            visited.append(question['pid'])
    logger.info("提交成功:" + str(cnt))
    with open("visited.json", "w") as f:
        json.dump(visited, f)


def submit_question(question):
    title = question['fid'] + ". " + question['title']
    parsed_code = codeparser.parse_code(question['code'])
    code = parsed_code['code']
    link = leetcode_url + question['titleSlug']
    tags = parsed_code['tags']
    print( [{"name": t} for t in tags])
    # 官方给出的数组
    # for t in question['tags']:
    #     if len(tags) != 0:
    #         tags += ", "
    #     tags += t
    try:
        r = requests.request("POST",
                             "https://api.notion.com/v1/pages",
                             json={
                                 "parent": {"type": "database_id", "database_id": database_id},
                                 "properties": {
                                     "Title": {"title": [{"type": "text", "text": {"content": title}}]},
                                     # "描述": {"rich_text": [{"type": "text", "text": {"content": content}}]},
                                     "Link": {"url": link},
                                     "Tag": {"type": "multi_select", "multi_select": [{"name": t} for t in tags]},
                                     "Source": {"type": "select", "select": {"name": "Leetcode"}},
                                     "Status": {"type": "select", "select": {"name": "🌓AC"}},
                                 },
                                 "children": [
                                     {
                                         "object": "block",
                                         "type": "paragraph",
                                         "paragraph": {
                                             "text": [{"type": "text",
                                                       "annotations": {"bold": True, "italic": True, "color": "green"},
                                                       "text": {"content": "题目\n"}},
                                                      {"type": "text",
                                                       "text": {"content": "Lc{}\n".format(title),
                                                                "link": {"url": link}}}
                                                      ]
                                         }
                                     },
                                     {
                                         "object": "block",
                                         "type": "paragraph",
                                         "paragraph": {
                                             "text": [{"type": "text",
                                                       "annotations": {"bold": True, "italic": True, "color": "red"},
                                                       "text": {"content": "算法\n"}}
                                                      ]
                                         }
                                     },
                                     {
                                         "object": "block",
                                         "type": "paragraph",
                                         "paragraph": {
                                             "text": [{"type": "text",
                                                       "annotations": {"bold": True, "italic": True, "color": "blue"},
                                                       "text": {"content": "时空复杂\n"}},
                                                      {"type": "text", "text": {"content": "时间复杂度:O()\n"}},
                                                      {"type": "text", "text": {"content": "空间复杂度:O()\n"}}
                                                      ]
                                         }
                                     },
                                     {
                                         "object": "block",
                                         "type": "paragraph",
                                         "paragraph": {
                                             "text": [{"type": "text",
                                                       "annotations": {"bold": True, "italic": True,
                                                                       "color": "yellow"},
                                                       "text": {"content": "代码 ( {} )\n".format(question['lang'])}},
                                                      {"type": "text",
                                                       "text": {"content": code}}
                                                      ]
                                         }
                                     }
                                 ]
                             },
                             headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-05-13"}
                             )
    except Exception as e:
        logger.error(question['fid'] + "." + question['title'] + ": 请求异常, 提交失败!")
        return False

    return r.ok


if __name__ == '__main__':
    str = {'pid': '1015', 'fid': '86', 'title': '分隔链表', 'titleSlug': 'partition-list', 'tags': ['链表'], 'code': ''}
    try:
        submit_questions([str])
    except Exception as e:
        print(e)
