## What's this?

Short to say, it's a tool to filter html tag's attributes
and get a structured object about this html document.

####example

If you have a html document string like this:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document</title>
</head>
<body>
    <div class="bs-docs-header" id="content" tabindex="-1">
      <div class="container">
        <p class="someclass" id="someid">something example</p>
        <a href="/">HOME</a>
      </div>
    </div>
</body>
</html>
```

put it into `cleaner.clean`, you will get a dict object named `truck` which
 contain an clean html document(`truck['page']['content']`):

```html
<!DOCTYPE html>
<html>
<head>
    <meta>
    <title>Document</title>
</head>
<body>
    <div>
      <div>
        <p>something example</p>
        <a href="/">HOME</a>
      </div>
    </div>
</body>
</html>
```

and  `truck['tags']`:

```json
[
    {
        "children_count": 2,
        "attr": ["lang='en'"],
        "content": ["\n","","\n","","\n"],
        "name": "html",
        "index": [16,186]
    },
    {
        "children_count": 2,
        "attr": [],
        "content": ["\n\t","","\n\t","","\n"],
        "name": "head",
        "index": [23,70]
    },
    {
        "children_count": 0,
        "attr": ["charset='UTF-8'"],
        "content": [""],
        "name": "meta",
        "index": [31,37]
    },
    {
        "children_count": 0,
        "attr": [],
        "content": ["Document"],
        "name": "title",
        "index": [39,62]
    },
    {
        "children_count": 1,
        "attr": [],
        "content": ["\n\t","","\n"],
        "name": "body",
        "index": [71,178]
    },
    {
        "children_count": 1,
        "attr": ["class='bs-docs-header'","id='content'","tabindex='-1'"],
        "content": ["\n      ","","\n    "],
        "name": "div",
        "index": [79,170]
    },
    {
        "children_count": 2,
        "attr": ["class='container'"],
        "content": ["\n\t\t","","\n\t\t","","\n      "],
        "name": "div",
        "index": [91,159]
    },
    {
        "children_count": 0,
        "attr": ["class='someclass'","id='someid'"],
        "content": ["something example"],
        "name": "p",
        "index": [99,123]
    },
    {
        "children_count": 0,
        "attr": ["href='/'"],
        "content": ["HOME"],
        "name": "a",
        "index": [126,146]
    }
]
```

####specifically

```python
truck = {
    'page': {
        'content': '',  # content of the html page
        'tag_places': {}  # tag's index in truck['tags']
    },
    'tags': []  # all tags in the html
}

truck['page']['tag_places'] = {
    'tag': [10, 20, 22, ...],  # tag's index in truck['tags']
    #...
}

truck['tags'] = [
    {
        'name': 'name',  # tag name
        'attr': [],  # tag's attribute
        'children_count': 0,  # tag's children count
        'index': [left_index, right_index],  # integer, tag's content index in truck['page']
        'content': ['']  # content blocks, '' if the part is tag.
    },
    #...
]

truck['tags']['attr'] = ['attr1="value1"', 'attr2="value2"', ...]

truck['tags']['content'] = ['text content', '', 'empty string is a', '', 'slot', '', 'for tag']
```

`truck['tags']['content']` 's detail:

A `truck['tags']` like this:

```python
truck['tags'] = [
    {
        "children_count": 2,
        "attr": ["class='container'"],
        "content": ["\n\t","","\n\t","","\n      "],
        "name": "div",
        "index": [91,159]
    },
    {
        "children_count": 0,
        "attr": ["class='someclass'","id='someid'"],
        "content": ["something example"],
        "name": "p",
        "index": [99,123]
    },
    {
        "children_count": 0,
        "attr": ["href='/'"],
        "content": ["HOME"],
        "name": "a",
        "index": [126,146]
    }
]
```
It's mean that a tag named `div` has two children(tag `p` and tag `a`) which followed the tag in the list.
And the `div` tag's content is `["\n\t","","\n\t","","\n      "]`
which equals `["\n\t",<p>,"\n\t",<a>,"\n      "]`


The origin html doc will be this:

```html
<div>
    <p>something example</p>
    <a href="/">HOME</a>
</div>
```


## How to use?

`cleaner.py` is core module, just `from ClearHTML import cleaner`, and put a string html to `cleaner.clean` function,
 you will get the object `truck`.

`demo.py` is a example to show how to use this.