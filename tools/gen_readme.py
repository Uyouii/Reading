# -*- coding: utf-8 -*
import os
import json
import sys

IGNORE_FILES = [".git", "README.md", "readme.md", "Readme.md"]
LINK_PREFIX = "https://github.com/Uyouii/Reading/blob/master"

PY3 = True if sys.version >= '3' else False

if PY3:
    from urllib.parse import quote
else:
    from urllib import quote

CN_REPLACE_MAP = {
    "一": "01",
    "二": "02",
    "三": "03",
    "四": "04",
    "五": "05",
    "六": "06",
    "七": "07",
    "八": "08",
    "九": "09",
    "十": "10",
}

def isShowFile(filename):
    if filename.startswith("~$"):
        return False
    if filename.endswith(".md") or filename.endswith(".pptx"):
        return True
    return False

def removeFileSuffix(filename):
    index = filename.rfind(".")
    if index == -1:
        return filename
    return filename[:index]


class Docs(object):
    def __init__(self, name, file_path, rel_folder, level):
        self.name = name
        self.file_path = file_path
        self.rel_folder = rel_folder
        self.doc_list = []
        self.level = level
        self._readme_content = ""
        self._parseDoc()

    def addDoc(self, doc_name):
        self.doc_list.append(doc_name)

    def getContents(self):
        return {
            "name": self.name,
            "file_path": self.file_path,
            "rel_folder": self.rel_folder,
            "doc_list": self.doc_list,
        }

    @property
    def readme_content(self):
        if self._readme_content:
            return self._readme_content
        return self.genReadmeContent()

    def genReadmeFile(self):
        readme_file_path = "{}/README.md".format(self.file_path)
        with open(readme_file_path, 'w') as readme_file:
            header = "# {}\n".format(self.name)  if self.name else ""
            readme_file.write("{}\n{}".format(header, self._readme_content))

    def genReadmeContent(self):
        self._readme_content = ""
        if not self.doc_list:
            return ""
        for doc in self.doc_list:
            if isinstance(doc, str):
                self._readme_content += "- [{}]({}{}/{})\n".format(
                    removeFileSuffix(doc), LINK_PREFIX, quote(self.rel_folder), quote(doc))
            elif isinstance(doc, Docs):
                sub_content = doc.readme_content
                if not sub_content:
                    continue
                self._readme_content += "## **[<font color=#008000>{}</font>]({}{}/{})**\n".format(
                    doc.name, LINK_PREFIX, quote(self.rel_folder), quote(doc.name))
                lines = sub_content.split("\n")
                for line in lines:
                    if not line:
                        continue
                    if line.startswith("##"):
                        self._readme_content += "#{}\n".format(line)
                    else:
                        self._readme_content += "{}\n".format(line)
        self.genReadmeFile()
        return self._readme_content


    def __repr__(self):
        return json.dumps(self.getContents(), encoding='utf-8', ensure_ascii=False, default=str)

    def _parseDoc(self):
        if not os.path.isdir(self.file_path):
            print("{} is not dir".format(self.file_path))
            return
        file_name_list = os.listdir(self.file_path)
        for file_name in file_name_list:
            if file_name in IGNORE_FILES:
                continue
            file_full_path = self.file_path + "/" + file_name
            if os.path.isfile(file_full_path) and isShowFile(file_name):
                self.addDoc(file_name)
            if os.path.isdir(file_full_path):
                sub_doc = Docs(file_name, file_full_path, self.rel_folder + "/" + file_name, self.level + 1)
                self.addDoc(sub_doc)
        def sort_func(x):
            if not isinstance(x, Docs):
                return x
            name = x.name
            for k, v in CN_REPLACE_MAP.items():
                name = name.replace(k, v)
            return name
        self.doc_list.sort(key=sort_func)

if __name__ == "__main__":
    pwd = os.getcwd()
    docs = Docs("Reading", pwd, "", 0)
    print(docs.genReadmeContent())