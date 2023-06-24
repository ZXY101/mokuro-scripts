from pathlib import Path
from bs4 import BeautifulSoup
from mokuro.run import run
from urllib.parse import unquote

import json
import os
import re
import argparse

""" 
Script to generate the _ocr data from already processed mokuro manga.
This will allow you to regenerate mokuro html files without needing to reprocess the entire manga.
"""


def generate_ocr_json(path, ocr_path):
    if (path.is_file() and path.suffix == '.html' and ".mobile.html" not in path.name):
        if not ocr_path.exists():
            os.mkdir(ocr_path)
            print('_ocr folder created')
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
            soup = BeautifulSoup(html, 'html.parser')

            folder_name = None
            pages = soup.find_all(class_="page")
            for page in pages:
                page_container = page.find(class_="pageContainer")
                styles = page_container["style"].split(";")[:-1]
                for style in styles:
                    key, value = style.strip().split(":")
                    if (key == "width"):
                        img_width = int(value)
                    if (key == "height"):
                        img_height = int(value)
                    if (key == "background-image"):
                        background_image = value

                image_name = unquote(re.findall(
                    '"([^"]*)"', background_image)[0])
                image_path = Path(image_name)
                if folder_name is None:
                    folder_name = os.path.dirname(image_path)
                blocks = []
                text_boxes = page.find_all(class_="textBox")
                for text_box in text_boxes:
                    if text_box is not None:
                        text_box_styles = text_box["style"].split(";")[:-1]
                        for text_box_style in text_box_styles:
                            text_box_style_key, text_box_style_value = text_box_style.strip().split(":")
                            writing_mode = None
                            if (text_box_style_key == "width"):
                                text_box_width = int(text_box_style_value)
                            if (text_box_style_key == "height"):
                                text_box_height = int(text_box_style_value)
                            if (text_box_style_key == "left"):
                                xmin = int(text_box_style_value)
                            if (text_box_style_key == "top"):
                                ymin = int(text_box_style_value)
                            if (text_box_style_key == 'writing-mode'):
                                writing_mode = text_box_style_value
                            if (text_box_style_key == 'font-size'):
                                font_size = text_box_style_value
                        xmax = xmin + text_box_width
                        ymax = ymin + text_box_height
                        box = [xmin, ymin, xmax, ymax]
                        if writing_mode is not None:
                            vertical = True
                        else:
                            vertical = False

                        lines = []
                        p_tags = text_box.find_all('p')
                        for p in p_tags:
                            lines.append(p.text.strip())
                    block = {
                        "box": box,
                        "vertical": vertical,
                        "font_size": float(font_size.replace("px", "")),
                        "lines": lines
                    }
                    blocks.append(block)

                page = {
                    "version": "0.1.6",
                    "img_width": img_width,
                    "img_height": img_height,
                    "blocks": blocks,
                }

                folder_path = Path(os.path.join(ocr_path, folder_name))
                if not folder_path.exists():
                    os.mkdir(folder_path)

                json_file_name = os.path.join(
                    folder_path, f'{image_path.stem}.json')

                json_dump = json.dumps(
                    page, ensure_ascii=False).encode('utf8').decode()

                with open(json_file_name, 'w', encoding='utf-8') as json_file:
                    json_file.write(json_dump)
                    json_file.close()
            return folder_name


def main():
    if not path.exists():
        print('Path does not exist')
        exit()
    if path.is_file():
        if path.suffix != '.html':
            print('Invalid file .html file specified')
            exit()
        if ".mobile.html" in path.name:
            print('Skipping mobile file')
            exit()

    if path.is_dir():
        print(f'Generating ocr json for all html files in {path.name}')
        ocr_path = Path(os.path.join(path, ocr_dir))
        for p in Path(path).expanduser().absolute().iterdir():
            generate_ocr_json(p, ocr_path)
            if remove_originals and run_mokuro and p.is_file() and p.suffix == '.html':
                os.remove(p)
        if run_mokuro:
            print(f'Reprocessing directory {path.name}')
            run(parent_dir=path)
    else:
        print(f'Generating _ocr files')
        folder_name = generate_ocr_json(path, ocr_dir)
        if folder_name is not None and run_mokuro:
            if (remove_originals):
                os.remove(path)
            print(f'Reprocessing {folder_name}')
            run(folder_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path", help="Path to html file or directory to generate ocr files for")
    parser.add_argument(
        "-m", "--run_mokuro", help="Reprocess the manga with mokuro once the ocr files have been generated", action='store_true')
    parser.add_argument(
        "-r", "--remove_originals", help="Delete the original html files when repcrocessing with mokuro", action='store_true')
    parser.add_argument(
        "-pd", "--parent_dir", help="Specify if the given path is parent directory containing multiple sub dirs", action='store_true')

    args = parser.parse_args()
    ocr_dir = Path('./_ocr')
    path = Path(args.path)

    run_mokuro = args.run_mokuro
    remove_originals = args.remove_originals
    parent_dir = args.parent_dir

    if parent_dir:
        print(f'Processing every directory within {path.name}')
        for p in path.expanduser().absolute().iterdir():
            if p.is_dir():
                path = p
                main()
    else:
        main()
