from bidi.algorithm import get_display
from bs4 import BeautifulSoup
import zipfile
import shutil
import os


def setup():
    if not os.path.isdir("temp"):
        os.mkdir("temp")


def fix_document(document: str) -> str:
    content = open(document, "r").read()
    soup = BeautifulSoup(content, "html.parser")
    paragraphs = soup.find_all("p")
    for paragraph in paragraphs:
        paragraph.string = get_display(paragraph.text)
        paragraph["dir"] = "rtl"
    with open(document, "w") as file:
        file.write(soup.prettify())


def unzip_book(book_path: str) -> str:
    data_dir = os.path.join("temp", os.path.basename(book_path).rsplit('.', 1)[0])
    with zipfile.ZipFile(book_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
    return data_dir


def zip_book(save_path: str, data_dir: str) -> None:
    with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as archive_file:
        for root, dirs, filenames in os.walk(data_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                archive_file_path = os.path.relpath(file_path, data_dir)
                archive_file.write(file_path, archive_file_path)


def patch_book(book_path: str, save_path: str):
    data_dir = unzip_book(book_path)

    for root, dirs, files in os.walk(data_dir, topdown=False):
        for name in files:
            path = os.path.join(root, name)
            if path.endswith(".html") or path.endswith(".xhtml"):
                fix_document(path)

    zip_book(save_path, data_dir)
    shutil.rmtree(data_dir)


def main():
    setup()
    patch_book("book.epub", "output.epub")


if __name__ == '__main__':
    main()
