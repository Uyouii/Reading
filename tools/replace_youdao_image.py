import hashlib
import os

import requests

DIR = ""

def download_img(img_url):
    response = requests.get(img_url)
    img_content = response.content
    md5hash = hashlib.md5(img_content)
    img_name = md5hash.hexdigest() + ".png"
    with open("{}/images/auto/{}".format(DIR, img_name), 'w') as file:
        file.write(img_content)
    print("download file:", img_name)
    return img_name


def replaceImagePath(file_path, image_rel_path):
    image_rel_path = "{}images/auto/".format(image_rel_path)
    content = ""
    with open(file_path, 'r') as file:
        content = file.read()

    old_len = len(content)
    idx = 0
    while idx != -1:
        idx = content.find("![](https://note.youdao.com/yws/", idx)
        if idx == -1:
            break
        md_img_url = content[idx:content.find(")", idx) + 1]
        img_url = md_img_url[md_img_url.find("https"):-1]
        image_name = download_img(img_url)
        image_path = image_rel_path + image_name
        replace_md_path = "![{}]({})".format(image_name, image_path)
        content = content.replace(md_img_url, replace_md_path)
        idx = idx + len(replace_md_path)
    
    if old_len != len(content):
        with open(file_path, 'w') as file:
            file.write(content)
        print("rewrite file:" + file_path)

def goThrouthFile(path, image_rel_path):
    if os.path.isdir(path):
        file_name_list = os.listdir(path)
        for file_name in file_name_list:
            file_full_path = path + "/" + file_name
            if os.path.isdir(file_full_path):
                goThrouthFile(file_full_path, image_rel_path + "../")
            else:
                goThrouthFile(file_full_path, image_rel_path)
    elif path.endswith(".md"):
        replaceImagePath(path, image_rel_path)

if __name__ == "__main__":
    pwd = os.getcwd()
    DIR = pwd
    goThrouthFile(pwd, "")