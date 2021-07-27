import leetcode
import notion


def main():
    questions = leetcode.scraping()
    notion.submit_questions(questions)


if __name__ == '__main__':
    main()
