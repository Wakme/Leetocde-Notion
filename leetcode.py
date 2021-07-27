# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import time
import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

leetcode_url = 'https://leetcode-cn.com/'
with open("config.json", "r") as f:
    tmp = json.loads(f.read())
    USERNAME = tmp['username']
    PASSWORD = tmp['password']

sign_in_url = 'accounts/login/'
sign_in_url = leetcode_url + sign_in_url

# 登录
def login(email, password):
    client = requests.session()
    client.encoding = "utf-8"

    while True:
        try:
            client.get(sign_in_url, verify=False)

            login_data = {'login': email,
                          'password': password
                          }
            result = client.post(sign_in_url, data=login_data, headers=dict(Referer=sign_in_url))

            if result.ok:
                logger.info("登录成功!")
                break
            else:
                raise Exception
        except Exception as e:
            logger.error("登录失败!")
            raise e
    return client


session = requests.session()

# 通过标题slug获取题目的详细信息, 暂时无用
def get_problem_by_slug(slug):
    url = "https://leetcode-cn.com/graphql"
    params = {'operationName': "questionData",
              'variables': {'titleSlug': slug},
              'query': '''query questionData($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                boundTopicId
                title
                titleSlug
                content
                translatedTitle
                translatedContent
                isPaidOnly
                difficulty
                likes
                dislikes
                isLiked
                similarQuestions
                contributors {
                  username
                  profileUrl
                  avatarUrl
                  __typename
                }
                langToValidPlayground
                topicTags {
                  name
                  slug
                  translatedName
                  __typename
                }
                companyTagStats
                codeSnippets {
                  lang
                  langSlug
                  code
                  __typename
                }
                stats
                hints
                solution {
                  id
                  canSeeDetail
                  __typename
                }
                status
                sampleTestCase
                metaData
                judgerAvailable
                judgeType
                mysqlSchemas
                enableRunCode
                envInfo
                book {
                  id
                  bookName
                  pressName
                  description
                  bookImgUrl
                  pressImgUrl
                  productUrl
                  __typename
                }
                isSubscribed
                __typename
              }
            }'''
              }

    json_data = json.dumps(params).encode('utf8')

    headers = {'User-Agent': USER_AGENT, 'Connection': 'keep-alive', 'Content-Type': 'application/json',
               'Referer': 'https://leetcode-cn.com/problems/' + slug}
    resp = session.post(url, data=json_data, headers=headers, timeout=10)
    content = resp.json()

    # 题目详细信息
    question = content['data']['question']
    link = "https://leetcode-cn.com/problems/two-sum/" + question['titleSlug'];
    title = question['questionId'] + "." + question['translatedTitle'];
    tags = [tag['translatedName'] for tag in question['topicTags']]
    problem = {'link': link, 'title': title, 'cn-content': question['translatedContent'], 'tags': tags}

    return problem


USER_AGENT = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'


# 获取到leetcode的所有题目, 并且保存到questions.json, 以对象数组的形式存储
# {'pid':'1015', 'fid':'86', 'title': '分隔链表', 'titleSlug':'partition-list', 'tags':['链表']}
def save_all_problems(client, update=True):
    # 当update为false的时候, 重新加载所有问题.
    if update:
        with open("questions.json", "r") as f:
            return json.load(f)
    logger.info("重新加载题目集!")
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
    }
    param = {
        "query": "\n    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    hasMore\n    total\n    questions {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId\n      isFavor\n      paidOnly\n      solutionNum\n      status\n      title\n      titleCn\n      titleSlug\n      topicTags {\n        name\n        nameTranslated\n        id\n        slug\n      }\n      extra {\n        hasVideoSolution\n        topCompanyTags {\n          imgUrl\n          slug\n          numSubscribed\n        }\n      }\n    }\n  }\n}\n    ",
        "variables": {
            "categorySlug": "",
            "skip": 0,
            "limit": 100,
            "filters": {}
        },
        "operationName": "problemsetQuestionList"
    }

    skip = 0
    questions = []
    while True:
        param['variables']['skip'] = skip
        param_json = json.dumps(param).encode("utf-8")
        response = client.post("https://leetcode-cn.com/graphql/", data=param_json, headers=headers)
        questionList = response.json()['data']['problemsetQuestionList']['questions']
        if len(questionList) == 0:
            break
        for question in questionList:
            pid = str(question['solutionNum'])

            fid = question['frontendQuestionId']
            title = question['titleCn'].replace(" ", "")
            titleSlug = question['titleSlug']
            tags = [t['nameTranslated'] for t in question['topicTags']]
            questions.append({'pid': pid, 'fid': fid, 'title': title, 'titleSlug': titleSlug, 'tags': tags})
        time.sleep(1)
        skip += 100
    with open("questions.json", "w") as f:
        json.dump(questions, f)
    logger.info("题集更新成功, 题目数量: " + str(len(questions)))
    return questions

# 根据提交的id下载代码
def downloadCode(client, id):
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
    }
    param = {'operationName': "mySubmissionDetail", "variables": {"id": id},
             'query': "query mySubmissionDetail($id: ID\u0021) {  submissionDetail(submissionId: $id) {    id    code    runtime    memory    statusDisplay    timestamp    lang    passedTestCaseCnt    totalTestCaseCnt    sourceUrl    question {      titleSlug      title      translatedTitle      questionId      __typename    }    ... on GeneralSubmissionNode {      outputDetail {        codeOutput        expectedOutput        input        compileError        runtimeError        lastTestcase        __typename      }      __typename    }    __typename  }}"
             }

    param_json = json.dumps(param).encode("utf-8")
    response = client.post("https://leetcode-cn.com/graphql/", data=param_json, headers=headers)
    submission_details = response.json()["data"]["submissionDetail"]
    logger.info(str(id) + "获取代码:" + str(len(submission_details["code"])) + "字")
    return submission_details["code"]


def scraping(timeLimit=24):
    # 登录
    client = login(USERNAME, PASSWORD)
    timeLimit *= 60 * 60
    page_num = 0
    with open("visited.json", "r") as f:
        visited = json.loads(f.read())
    res = []
    questions = save_all_problems(client)
    while True:
        submissions_url = "https://leetcode-cn.com/api/submissions/?offset=" + str(page_num) + "&limit=20&lastkey="

        html = client.get(submissions_url, verify=False)
        html = json.loads(html.text)
        cur_time = time.time()
        if not html.get("submissions_dump"):
            logger.error("获取提交信息失败!")
            break

        for submission in html["submissions_dump"]:
            submission_status = submission['status_display']
            problem_title = submission['title'].replace(" ", "")
            submission_language = submission['lang']
            if submission_status != "Accepted":
                continue
            if cur_time - submission['timestamp'] > timeLimit:
                break

            try:
                sub_id = str(submission['id'])
                code = downloadCode(client, sub_id)
                # 只有含有@Notion的注释才会被提交到Notion中
                if code.find("@Notion") == -1:
                    continue
                # 在题目集中找到中文标题为该提交标题的所有问题
                problems = [t for t in questions if t['title'] == problem_title]
                if len(problems) == 0:
                    # 尝试重新加载
                    logger.info("{" + problem_title + "}" + "未找到该题目, 尝试重新加载")
                    questions = save_all_problems(client, False)
                    problems = [t for t in questions if t['title'] == problem_title]
                if len(problems) == 0:
                    logger.error(problem_title + ":该题目不存在!")
                    raise Exception
                question = problems[0]
                if question['pid'] in visited:
                    continue
                visited.append(question['pid'])
                question['code'] = code
                question['lang'] = submission_language
                res.append(question)
            except Exception as e:
                print(e)
        time.sleep(1)
        page_num += 20
        logger.info("待更新题目数量: "+ str(len(res)))
        return res

