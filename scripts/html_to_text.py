from bs4 import BeautifulSoup
import re
import sys
import os

def process_html_file(file_path):
    # Load the HTML file
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Create a list to store the data
    data = []
    tag = os.path.basename(file_path)
    tag = tag[:-5]
    regex_invalid = re.compile("[Ａ-Ｚａ-ｚ０-９]|．{4,}|《")

    # Loop over the pages
    for page in soup.find_all("div", {"class": "page"}):
        for textbox in page.find_all("div", {"class": "textBox"}):
            combinedText = ""
            for text in textbox.find_all("p"):
                combinedText = combinedText + text.text.strip()
            if len(combinedText) > 10 and regex_invalid.search(combinedText) is None:
                data.append(combinedText)

    # Write the data to a TXT file
    txt_name = tag + ".txt"
    txt_path = os.path.join(os.path.dirname(file_path), txt_name)
    with open(txt_path, "w", encoding="utf-8") as f:
        data_string = "\n".join(data)
        f.write(data_string)


def process_html_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".html") and ".mobile.html" not in file_name:
            file_path = os.path.join(folder_path, file_name)
            process_html_file(file_path)


def process_argument(argument):
    if os.path.isfile(argument):
        if argument.endswith(".html") and ".mobile.html" not in argument:
            process_html_file(argument)
        else:
            print("Invalid file format. Only HTML files are supported.")
    elif os.path.isdir(argument):
        process_html_folder(argument)
    else:
        print("Invalid argument. Please provide a valid file or folder path.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the file or folder path as an argument.")
    else:
        argument = sys.argv[1]
        process_argument(argument)
