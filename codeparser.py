# 解析代码, 在代码中提取出注释中的标签以及删除掉多余的注释
def parse_code(rawCode):
    lines = rawCode.split('\n')
    res = {}
    code = ""
    for line in lines:
        if line.find("@Notion") != -1:
            continue
        elif line.find("@Tags") != -1:
            res['tags'] = parse_tags(line)
        elif line.find("@Note") != -1:
            res['note'] = parse_note(line)
        else:
            code += line + "\n"
    res['code'] = code
    return res


def parse_note(line):
    return line[line.find(":") + 1:].strip()


def parse_tags(line):
    res = [t.strip() for t in line[line.find(':') + 1:].split(",")]
    return res
