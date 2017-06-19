def get_attr(attr_list, condition):
    """
    get a tag's attr from a list with a condition
    :return: an attribute string if the condition is satisfied
    """
    for item in attr_list:
        if item.startswith(condition):
            return ' ' + item
    return ''


def special_tag_check(worker, truck):
    """
    check some special tags which must have attribute
    at here, they are 'img', 'a', 'svg', 'path', you can add more
    """
    name, attr = worker['cur_name'], worker['cur_attr']
    addition = '>'
    if name == 'img':
        addition = get_attr(attr, 'src=') + '>'
    elif name == 'a':
        addition = get_attr(attr, 'href=') + '>'
    elif name == 'svg':
        addition = ' ' + ' '.join(attr) + '>'
    elif name == 'path':
        addition = get_attr(attr, 'd=') + '>'
    truck['page']['content'] += addition


def got_tag(worker, truck):
    """
    got a tag.
    """
    worker['state'] = 0
    special_tag_check(worker, truck)
    name, attr = worker['cur_name'], worker['cur_attr']
    worker['cur_name'], worker['cur_attr'] = '', []
    tag_content_left_index = worker['start_at']

    t = {
        'name': name,  # tag name
        'attr': attr,  # tag's attribute
        'children_count': 0,  # tag's children count
        'index': [tag_content_left_index],  # tag's content index in truck['page']
        'content': ['']  # content blocks, '' if the part is tag.
    }
    truck['tags'].append(t)

    # count and record tag's children
    if worker['tag_stack']:
        worker['tag_stack'][-1]['children_count'] += 1
        worker['tag_stack'][-1]['content'].extend(['', ''])

    # record tags distribution
    if truck['page']['tag_location'].get(name) is None:
        truck['page']['tag_location'][name] = []
    place = len(truck['tags']) - 1  # begin with 0
    truck['page']['tag_location'][name].append(place)

    # push no-single tags in stack
    if name in worker['single_tags']:
        worker['state'] = 0
        tag_content_right_index = len(truck['page']['content'])
        t['index'].append(tag_content_right_index)
    else:
        worker['tag_stack'].append(t)


def left_a_tag(worker, truck):
    """
    left tag. reset and record something.
    """
    worker['state'] = 0
    t = worker['tag_stack'].pop()
    tag_content_right_index = len(truck['page']['content'])
    t['index'].append(tag_content_right_index)


def got_else(worker, truck):
    """
    got something unexpected
    """
    worker['state'] = 0
    worker['cur_name'] = ''
    worker['cur_attr'] = []
    truck['page']['content'] += worker['cur_char']


def state10(worker, truck):
    """
    got '<'
    """
    c = worker['cur_char']  # handover
    if c.isalpha():
        worker['state'] = 11
        worker['cur_name'] += c
        truck['page']['content'] += c
    elif c == '/':
        worker['state'] = 40
        truck['page']['content'] += c
    else:
        got_else(worker, truck)
        return True
    return False


def state11(worker, truck):
    """
    got '<ta'
    """
    c = worker['cur_char']  # handover
    if c.isalpha():
        worker['state'] = 11
        worker['cur_name'] += c
        truck['page']['content'] += c
    elif c.isdecimal():
        worker['state'] = 12
        worker['cur_name'] += c
        truck['page']['content'] += c
    elif c.isspace():
        worker['state'] = 13
    elif c == '>':
        # truck['page']['content'] += c  # move into got_tag(), The same bellow
        got_tag(worker, truck)
        return True
    else:
        got_else(worker, truck)
        return True
    return False


def state12(worker, truck):
    """
    got '<tag#', such as <h1
    """
    c = worker['cur_char']
    if c.isspace():
        worker['state'] = 13
    elif c == '>':
        got_tag(worker, truck)
        return True
    else:
        got_else(worker, truck)
        return True
    return False


def state13(worker, truck):
    """
    got '<tag ' or '<tag# '
    """
    c = worker['cur_char']
    if c.isspace():
        worker['state'] = 13
    elif c.isalpha():  # attr maybe
        worker['state'] = 30
        worker['cur_attr'].append('')  # append '' for +=
        worker['cur_attr'][-1] += c
    elif c == '/':
        worker['state'] = 20
        truck['page']['content'] += c
    elif c == '>':
        got_tag(worker, truck)
        return True
    else:
        got_else(worker, truck)
        return True
    return False


def state20(worker, truck):
    """
    got '<tag.../'
    """
    c = worker['cur_char']
    if c == '>':
        got_tag(worker, truck)
        return True
    else:
        got_else(worker, truck)
        return True


def state30(worker, truck):
    """
    got '<tag... att'
    """
    c = worker['cur_char']
    if c.isalpha() or c == '-':
        worker['state'] = 30
        worker['cur_attr'][-1] += c
    elif c == '=':
        worker['state'] = 31
        worker['cur_attr'][-1] += c
    else:
        got_else(worker, truck)
        return True
    return False


def state31(worker, truck):
    """
    got '<tag... attr='
    """
    c = worker['cur_char']
    if c == '"':
        worker['state'] = 32
        worker['cur_attr'][-1] += c
    elif c == "'":
        worker['state'] = 33
        worker['cur_attr'][-1] += c
    else:
        got_else(worker, truck)
        return True
    return False


def state32(worker, truck):
    """
    got '<tag... attr="va'
    """
    c = worker['cur_char']
    if c != '"':
        worker['state'] = 32
        worker['cur_attr'][-1] += c
    else:
        worker['state'] = 34
        worker['cur_attr'][-1] += c
    return False


def state33(worker, truck):
    """
    got "<tag... attr='va"
    """
    c = worker['cur_char']
    if c != "'":
        worker['state'] = 33
        worker['cur_attr'][-1] += c
    else:
        worker['state'] = 34
        worker['cur_attr'][-1] += c
    return False


def state34(worker, truck):
    """
    got '<tag... attr="value"' or "<tag... attr='value'"
    """
    c = worker['cur_char']
    if c.isspace():
        worker['state'] = 13
    elif c == '/':  # new added
        worker['state'] = 13
        truck['page']['content'] += c
    elif c == '>':
        got_tag(worker, truck)
        return True
    else:
        got_else(worker, truck)
        return True
    return False


def state40(worker, truck):
    """
    got '</'
    """
    c = worker['cur_char']
    if c.isalpha():
        worker['state'] = 41
        truck['page']['content'] += c
    else:
        got_else(worker, truck)
        return True


def state41(worker, truck):
    """
    got '</ta'
    """
    c = worker['cur_char']
    if c.isalpha():
        worker['state'] = 41
        truck['page']['content'] += c
    elif c.isdecimal():
        worker['state'] = 42
        truck['page']['content'] += c
    elif c == '>':
        truck['page']['content'] += c
        left_a_tag(worker, truck)
        return True
    else:
        got_else(worker, truck)
        return True
    return False


def state42(worker, truck):
    """
    got '</tag'
    """
    c = worker['cur_char']
    if c == '>':
        truck['page']['content'] += c
        left_a_tag(worker, truck)
        return True
    else:
        got_else(worker, truck)
        return True


def get_char(materials):
    index = materials['index']
    materials['index'] += 1
    return materials['content'][index]


def clean(html_doc):
    """
    parse html to a structured object
    """
    switch = {
        10: state10,
        11: state11,
        12: state12,
        13: state13,
        20: state20,
        30: state30,
        31: state31,
        32: state32,
        33: state33,
        34: state34,
        40: state40,
        41: state41,
        42: state42,
    }
    materials = {'content': html_doc, 'index': 0}
    single_tags = {"br", "img", "meta", "wbr", "embed", "input", "param", "hr", "link", "source"} # and more
    worker = {
        'state': 0,
        'start_at': 0,
        'cur_char': '',
        'cur_name': '',
        'cur_attr': [],
        'tag_stack': [],
        'single_tags': single_tags,
        }
    truck = {
        'page': {
            'content': '',  # whole content of the html page
            'tag_location': {}  # tag's index in truck['tags']
        },
        'tags': []  # all tags in the html
    }

    while materials['index'] < len(html_doc):
        worker['cur_char'] = get_char(materials)
        if worker['cur_char'] == '<':  # tag maybe
            worker['state'] = 10  # start state with 10
            worker['start_at'] = len(truck['page']['content'])
            truck['page']['content'] += worker['cur_char']
            while materials['index'] < len(html_doc):
                worker['cur_char'] = get_char(materials)
                is_break = switch[worker['state']](worker, truck)
                if is_break:
                    break
        else:  # not tag
            truck['page']['content'] += worker['cur_char']
            if worker['tag_stack']:
                worker['tag_stack'][-1]['content'][-1] += worker['cur_char']
    return truck
