import os

import leetcode
import notion

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 切换目录到当前脚本下

def main():
    questions = leetcode.scraping()
    notion.submit_questions(questions)


if __name__ == '__main__':
    main()
