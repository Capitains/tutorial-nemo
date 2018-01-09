import requests
from lxml import html as html_parser
from lxml.html import clean
from collections import defaultdict
import re

DEBUG = False
BREAK_ON = 1

poems = []
translations = []
second_translations = []

download = range(0, 96)
URI = "http://www.sacred-texts.com/cla/priap/prp{}.htm"

NOTES_INSERT = re.compile("\[(\d+)\]")
NOTES_TEXT = re.compile("\[?\d+\.")

with open("./template.xml") as f:
    template = f.read()


def check_p(*args):
    names = ["poem", "translation", "notes"]
    for arg in range(0, len(args)):
        print(names[arg], [html_parser.tostring(p, encoding=str) for p in args[arg]])


def normalize(unit):
    return html_parser.tostring(unit, encoding=str).replace("<p>", "").replace("</p>", "").replace("\xa0", "")


def reformat(paragraphs):
    for paragraph in paragraphs:
        p = normalize(paragraph)
        lines = p.split("<br>")
        lines = ["<l>"+l.replace("\n", "")+"</l>" for l in lines]
        lines = [x.split("Next:")[0] for x in lines]
        yield "<div type=\"textpart\" subtype=\"poem\">{}</div>".format("\n".join(lines))


def replace_notes(translations, input_notes):
    notes = defaultdict(lambda: None)
    for note in NOTES_TEXT.split("\n".join([normalize(unit) for unit in input_notes])):
        if len(note) > 0:
            notes[len(notes)+1] = note.replace("<br>", "").replace("\n", "")
    output = []

    def sub(match):
        index = int(match.groups()[0])
        if index in notes:
            return "<note type=\"footnote\">"+notes[index].split("]")[0]+"</note>"
        else:
            return ""
    for translation in translations:
        output.append(NOTES_INSERT.sub(sub, translation))
    return output

cleaner = clean.Cleaner(allow_tags=["br", "p"], remove_unknown_tags=False)

for poem_index in download:
    print("Doing {}".format(str(poem_index)))
    data = requests.get(URI.format(str(poem_index).zfill(2))).content
    html = html_parser.fromstring(data)
    html = cleaner.clean_html(html)
    poem, translation, notes = [], [], []

    paragraph_index = 0
    for p in html.xpath(".//p"):
        if paragraph_index == 0:
            poem = [p]
        elif paragraph_index >= 100: # (We found the notes)
            notes.append(p)
        elif html_parser.tostring(p, encoding=str).startswith("<p>[1"):
            notes.append(p)
            paragraph_index = 100
        else:
            translation.append(p)
        paragraph_index += 1

    if DEBUG is True:
        check_p(poem, translation, notes)

    poem, translation = list(reformat(poem)), list(reformat([translation[0]] + translation[1:]))

    translation = replace_notes(translation, notes)

    poems.append(poem[0])
    translations.append(translation[0])
    second_translations.append(translation[1])

with open("data/phi1103/phi001/phi1103.phi001.lascivaroma-lat1.xml", "w") as f:
    f.write(template.format(
        title="Priapeia",
        urn="urn:cts:latinLit:phi1103.phi001.lascivaroma-lat1",
        xml="\n\n".join(poems),
        lang="lat"
    ))

with open("data/phi1103/phi001/phi1103.phi001.lascivaroma-eng1.xml", "w") as f:
    f.write(template.format(
        title="Priapeia",
        urn="urn:cts:latinLit:phi1103.phi001.lascivaroma-eng1",
        xml="\n\n".join(translations),
        lang="eng"
    ))

with open("data/phi1103/phi001/phi1103.phi001.lascivaroma-eng2.xml", "w") as f:
    f.write(template.format(
        title="Priapeia",
        urn="urn:cts:latinLit:phi1103.phi001.lascivaroma-eng2",
        xml="\n\n".join(second_translations),
        lang="eng"
    ))