from lxml import etree
import os
from glob import glob
from pickle import load
import re
from collections import defaultdict
import json
import argparse


class CreatePage:

    def __init__(self, orig, dest, out="html", source="", project="", url_base="", hook_results="", gitpage=""):
        """
        :param orig: The /data folder for the local CapiTainS repository
        :type orig: str
        :param dest: the destination to save the .txt file with the markdown
        :type dest: str
        :param hook_results: the pickled dictionary where the HookTest results for this repository are located
        :type hook_results: str
        :param out: the output format for the gh-page ('hmtl' or 'markdown')
        :type out: str
        :param source: the directory that contains the template.html, footer.txt, header.txt, and leader.txt files
        :type source: str
        :param project: the name of the project that produced the results
        :type project: str
        :param url_base: the base URL, including the data folder, that points to the files in the GH repo
        :type url_base: str
        :param gitpage: the URL of the page on Github where the repository lives, e.g., https://github.com/OpenGreekAndLatin/First1KGreek
        :type gitpage: str
        """
        self.orig = orig
        self.dest = dest
        if out == "html":
            self.bold_start = "<strong>"
            self.bold_end = "</strong>"
            self.it_start = "<em>"
            self.it_end = "</em>"
        elif out == "markdown":
            self.bold_start = self.bold_end = "**"
            self.it_start = self.it_end = "*"
        with open('{}/template.html'.format(source)) as f:
            self.template = f.read()
        self.project = project
        with open('{}/footer.txt'.format(source)) as f:
            self.foot = f.read()
        with open('{}/header.txt'.format(source)) as f:
            self.presentation = f.read()
        self.url_base = url_base
        self.gitpage = gitpage
        self.gitorg = gitpage.replace('/{}'.format(gitpage.split('/')[-1]), '')
        self.organization = self.gitorg.split('/')[-1]
        with open('{}/leader.txt'.format(source)) as f:
            self.leader = f.read()
        self.hook_results = {}
        total_words = 0
        try:
            if hook_results.endswith('pickle'):
                with open(hook_results, mode="rb") as f:
                    results = load(f)
            elif hook_results.endswith('json'):
                with open(hook_results) as f:
                    results = json.load(f)
            for r in results['units']:
                try:
                    self.hook_results[r['name'].split('/')[-1]] = r['words']
                    total_words += r['words']
                except:
                    continue
        except:
            print("No results found")
            self.hook_results = {}
        self.presentation = re.sub(r'<strong id="word_count">[\d,]+</strong>', r'<strong id="word_count">{:,}</strong>'.format(total_words), self.presentation)
        self.author_words = defaultdict(int)
        self.source_words = defaultdict(int)
        self.funder_words = defaultdict(int)
        if self.hook_results:
            self.table = """<table>
            <tr>
            <td>{words} Words</td>
            <td><a href="{git_link}">XML Source</a></td>
            </tr>
            </table>
            """
        else:
            self.table = """<table>
                        <tr>
                        <td><a href="{nemo_link}">Read Online</a></td>
                        <td><a href="{git_link}">XML Source</a></td>
                        <td><a href="{pos_link}">Morphological Annotation</a></td>
                        </tr>
                        </table>
                        """

    def write_dict(self):
        """

        :return: the dictionary containing all the authors, works, and editions
        :rtype: {urn: {"name": str, "works": {urn (str): {"editions": [edition1 (str), edition2 (str)]}}}}
        """
        # Rewrite this using a MyCapytain resolver
        ns = {"ti": "http://chs.harvard.edu/xmlns/cts", "tei": "http://www.tei-c.org/ns/1.0"}
        authors = [x for x in glob("{}/*".format(self.orig)) if os.path.isdir(x)]
        work_dict = {}
        for author in authors:
            try:
                a_root = etree.parse("{}/__cts__.xml".format(author)).getroot()
                a_urn = a_root.xpath("/ti:textgroup", namespaces=ns)[0].get("urn").split(":")[-1]
                a_name = a_root.xpath("/ti:textgroup/ti:groupname", namespaces=ns)[0].text
                work_dict[a_urn] = {"name": "{0}{1} ({2}{3}{4}){5}".format(self.bold_start,
                                                                           a_name,
                                                                           self.it_start,
                                                                           a_urn,
                                                                           self.it_end,
                                                                           self.bold_end), "works": {}}
            except OSError:
                print("No metadata for author {}".format(os.path.basename(author)))
                continue
            works = [w for w in glob("{}/*".format(author)) if os.path.isdir(w)]
            for work in sorted(works):
                try:
                    w_root = etree.parse("{}/__cts__.xml".format(work)).getroot()
                    w_urn = w_root.xpath("/ti:work", namespaces=ns)[0].get("urn").split(":")[-1]
                    w_name = w_root.xpath("/ti:work/ti:title", namespaces=ns)[0].text
                    work_dict[a_urn]["works"][w_urn] = {"name": "{0}{1} {2}({3})".format(self.it_start, w_name, self.it_end, w_urn), "editions": []}
                except OSError:
                    print("No metadata for the work {}/{}".format(os.path.basename(author), os.path.basename(work)))
                    continue
                for edition in w_root.xpath("/ti:work/*", namespaces=ns):
                    try:
                        e_full_urn = edition.get("urn")
                        e_urn = e_full_urn.split(":")[-1]
                    except:
                        continue
                    try:
                        e_root = etree.parse("{}/{}.xml".format(work, e_urn)).getroot()
                        source_root = e_root.xpath("/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:authority",
                                              namespaces=ns)
                        funder_root = e_root.xpath('/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:funder',
                                            namespaces=ns)
                    except OSError:
                        source_root = None
                        funder_root = None
                    except Exception:
                        print("There was a problem with {}".format(e_urn))
                        source_root = None
                        funder_root = None
                    if source_root:
                        source = source_root[0].text.split(',')[0]
                    else:
                        source = "Unknown"
                    if funder_root:
                        funder = funder_root[0].text
                    else:
                        funder = 'Unknown'
                    if funder is None:
                        funder = 'Unknown'
                    if source is None:
                        source = 'Unknown'
                    source = re.sub(r"\s+", " ", source)
                    e_name = edition.xpath("./ti:description", namespaces=ns)[0].text
                    e_url = "{}/{}/{}/{}.xml".format(self.url_base, e_urn.split(".")[0], e_urn.split(".")[1], e_urn)
                    e_nemo = "http://cts.dh.uni-leipzig.de/text/{}/passage".format(e_full_urn)
                    e_pos = "https://raw.githubusercontent.com/gcelano/LemmatizedAncientGreekXML/master/texts/{}.xml".format(e_urn)
                    if self.hook_results:
                        try:
                            e_words = self.hook_results['{}.xml'.format(e_urn)]
                        except KeyError as E:
                            print("Nothing found for {}".format(e_urn))
                            e_words = 0
                        self.author_words[a_urn] += e_words
                        self.source_words[source] += e_words
                        self.funder_words[funder] += e_words
                        e_words = "{:,}".format(e_words)
                        e_table = self.table.format(words=e_words, git_link=e_url, nemo_link=e_nemo, pos_link=e_pos)
                        if self.it_start == "*":
                            work_dict[a_urn]["works"][w_urn]["editions"].append(
                                "[{0} ({1}{2}{3})]({4}) - {5} words\nSource: {6}".format(e_name,
                                                                            self.it_start,
                                                                            e_urn,
                                                                            self.it_end,
                                                                            e_url,
                                                                            e_words,
                                                                            source))
                        else:
                            work_dict[a_urn]["works"][w_urn]["editions"].append(
                                '{0} ({1}{2}{3})<br>Source: {5}<br>{6}'.format(e_name,
                                                                                           self.it_start,
                                                                                           e_urn,
                                                                                           self.it_end,
                                                                                           e_url,
                                                                                           source,
                                                                                           e_table))
                    else:
                        e_table = self.table.format(git_link=e_url, nemo_link=e_nemo, pos_link=e_pos)
                        if self.it_start == "*":
                            work_dict[a_urn]["works"][w_urn]["editions"].append("[{0} ({1}{2}{3})]({4})\nSource: {5}".format(e_name,
                                                                                                                self.it_start,
                                                                                                                e_urn,
                                                                                                                self.it_end,
                                                                                                                e_url,
                                                                                                                source))
                        else:
                            work_dict[a_urn]["works"][w_urn]["editions"].append(
                                '{0} ({1}{2}{3})<br>Source: {5}<br>{6}'.format(e_name,
                                                                                           self.it_start,
                                                                                           e_urn,
                                                                                           self.it_end,
                                                                                           e_url,
                                                                                           source,
                                                                                           e_table))
        return work_dict

    def write_results(self, work_dict):
        """

        :param work_dict: the dictionary containing all the authors, works, and editions
        :type work_dict: {urn: {"name": str, "works": {urn: {"editions": [edition1, edition2]}}}}
        :return: the formatted markdown string
        :rtype: str
        """
        raise NotImplementedError("write_results is not implemented on the base class")

    def save_txt(self, results):
        """

        :param results: the formatted string created by self.write_results
        :type results: str
        """
        with open(self.dest, mode="w") as f:
            f.write(results)

    def run_all(self):
        """ A convenience function to automatically run all functions.

        """
        work_dict = self.write_dict()
        results = self.write_results(work_dict)
        self.save_txt(results)


class CreateMarkdown(CreatePage):

    def write_results(self, work_dict):
        """

        :param work_dict: the dictionary containing all the authors, works, and editions
        :type work_dict: {urn: {"name": str, "works": {urn: {"editions": [edition1, edition2]}}}}
        :return: the formatted markdown string
        :rtype: str
        """
        markdown = ''
        for a in sorted(work_dict.keys(), key=lambda x: work_dict[x]["name"].lower()):
            markdown = markdown + "+ {}** - {:,} words**\n".format(work_dict[a]["name"], self.author_words[a])
            for work in sorted(work_dict[a]["works"].keys(), key=lambda x: work_dict[a]["works"][x]["name"].lower()):
                markdown = markdown + "    + {}\n".format(work_dict[a]["works"][work]["name"])
                for edition in work_dict[a]["works"][work]["editions"]:
                    markdown = markdown + "        + {}\n".format(edition)
        return markdown


class CreateHTML(CreatePage):

    def write_results(self, work_dict):
        """

        :param work_dict: the dictionary containing all the authors, works, and editions
        :type work_dict: {urn: {"name": str, "works": {urn: {"editions": [edition1, edition2]}}}}
        :return: the formatted markdown string
        :rtype: str
        """
        html = self.template
        texts = '<ul>'
        for a in sorted(work_dict.keys(), key=lambda x: work_dict[x]["name"].lower()):
            texts += "<li>\n{}<strong> - {:,} words</strong>\n\n<ul>".format(work_dict[a]["name"], self.author_words[a])
            for work in sorted(work_dict[a]["works"].keys(), key=lambda x: work_dict[a]["works"][x]["name"].lower()):
                texts = texts + "<li>\n{}\n".format(work_dict[a]["works"][work]["name"])
                if len(work_dict[a]["works"][work]["editions"]) > 0:
                  texts += "<ul>"
                  for edition in work_dict[a]["works"][work]["editions"]:
                      texts += "<li>{}</li>".format(edition)
                  texts += "</ul>"
                texts += "</li>\n"
            texts += "</ul>\n</li>\n"
        texts += '</ul>'
        texts += "<p><strong>Word Counts by Source:</strong><br>"
        for k, v in sorted(self.source_words.items(), key=lambda x: x[1], reverse=True):
            texts += "<strong>{}:</strong> {:,}<br>".format(k, v)
        texts += "</p>"
        html = html.replace('{{UL-LI}}', texts)
        html = html.replace('{{footer}}', self.foot)
        html = html.replace('{{presentation}}', self.presentation)
        html = html.replace('{{ProjectName}}', self.project)
        html = html.replace('{{GitPage}}', self.gitpage)
        html = html.replace('{{GitOrg}}', self.gitorg)
        html = html.replace('{{organization}}', self.organization)
        html = html.replace('{{leader}}', self.leader)
        return html


def cmd():
    parser = argparse.ArgumentParser(description='Creates a Github page for a local CTS-compliant Github repository.')
    parser.add_argument('--orig', default='../data', help='The location of the local Github repository.')
    parser.add_argument('--dest', default="./index.html", help='The file in which you want to save your page.')
    parser.add_argument('--out', default="html", help='The format in which you want to save your results.')
    parser.add_argument('--source', default="./", help='The directory containing template.html, header.txt, footer.txt, and leader.txt.')
    parser.add_argument('--project', default="", help='The name of the project the page represents.')
    parser.add_argument('--url_base', help='The string that will serve as the base URL for the links to the text files in the repository.')
    parser.add_argument('--gitpage', default="https://github.com/lascivaroma/additional-texts",
                        help='The URL for the Github repository.')
    parser.add_argument('--hook_results', default="../results.json", help='The location of the HookTest results JSON file.')
    args = parser.parse_args()
    CreateHTML(**vars(args)).run_all()

if __name__ == '__main__':
    cmd()
