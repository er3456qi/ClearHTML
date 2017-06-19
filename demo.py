import os
from urllib import request
from ClearHTML import cleaner


def get_tag(truck, tag_name):
    """
    for example: get_tag('body')
    """
    places = truck['page']['tag_places'].get(tag_name)
    if places is None:
        print("No such tag!")
        return
    place = places[0]
    index = truck['tags'][place]['index']
    return truck['page']['content'][index[0]: index[1]]


def get_tags(truck, tag_name):
    """
    for example: get_tags('div')
    """
    places = truck['page']['tag_places'].get(tag_name)
    if places is None:
        print("No such tag!")
        return

    tags = []
    for i in range(len(places)):
        index = truck['tags'][places[i]]['index']
        s = truck['page']['content'][index[0]: index[1]]
        tags.append(s)
    return tags


def get_tag_by_attr(truck, tag_name, attr):
    """
    for example: get_tag_with_attr('div', 'class="main container"')
    or get_tag_with_attr('div', '.main.container')
    In this case, I write a method to support two css selector:
    .container --> class="container' and #top --> id="top".
    """
    places = truck['page']['tag_places'].get(tag_name)
    if places is None:
        print("No such tag!")
        return
    attr = transfer(attr)
    for i in range(len(places)):
        tag = truck['tags'][places[i]]
        if attr in tag['attr']:
            index = tag['index']
            return truck['page']['content'][index[0]: index[1]]
    return ''


def transfer(truck, attr):
    """
    transfer attr
    """
    class_attr = 'class="{}"'
    id_attr = 'id="{}"'
    if attr.startswith('.'):
        s = attr.replace('.', ' ')
        return class_attr.format(s[1:])
    elif attr.startswith('#'):
        return id_attr.format(attr[1:])
    return attr


def convert_to_json(truck):
    import json
    return json.dumps(truck['tags'], ensure_ascii=False, indent=4)


def get_html_doc(uri, from_local):
    """
    get string content from web page or local file.
    """
    if from_local:
        if not os.path.isfile(uri):
            print('No such file:', uri)
            return None
        with open(uri) as f:
            return f.read()
    else:
        with request.urlopen(uri) as f:
            print('got html')
            return f.read().decode()


def run(uri, from_local=False):
    html = get_html_doc(uri, from_local)
    if html is None:
        print('empty content!')
        return
    truck = cleaner.clean(html)
    return truck


def main():
    url = 'http://www.bing.com'
    truck = run(url)
    tags = truck.get('tags')
    page = truck.get('page')
    content = page.get('content')
    tag_location = page.get('tag_location')
    print(tags)
    print(content)
    print(tag_location)


if __name__ == '__main__':
    main()




