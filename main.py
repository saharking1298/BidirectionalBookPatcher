from bidi.algorithm import get_display
from bs4 import BeautifulSoup
import zipfile
import shutil
import os


def setup() -> None:
    """
    This function prepares the essential files needed for the program to operate.
    """
    if not os.path.isdir("temp"):
        os.mkdir("temp")


def unzip_book(book_path: str) -> str:
    """
    This function extracts an EPUB contents, then returns the path to the extracted directory.
    :param book_path:  The path to the book's EPUB file
    :return: Book's archive folder
    """
    data_dir = os.path.join("temp", os.path.basename(book_path).rsplit('.', 1)[0])
    with zipfile.ZipFile(book_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
    return data_dir


def zip_book(save_path: str, data_dir: str) -> None:
    """
    This function zips a modified book with a given save path and data folder.
    :param save_path: Path for the modified book's output
    :param data_dir: Path for the modified book's data directory.
    """
    with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as archive_file:
        for root, dirs, filenames in os.walk(data_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                archive_file_path = os.path.relpath(file_path, data_dir)
                archive_file.write(file_path, archive_file_path)


def fix_book_document(document_path: str, text_align="") -> None:
    """
    This function fixes a single HTML document by the bidirectional standard.
    :param document_path: An HTML book document path
    :param text_align: Text align of the book's content (LTR or RTL) (optional)
    """
    content = open(document_path, "r").read()
    soup = BeautifulSoup(content, "html.parser")
    paragraphs = soup.find_all("p")
    if text_align != "":
        body = soup.find("body")
        body["dir"] = text_align
    for paragraph in paragraphs:
        paragraph.string = get_display(paragraph.text)
    with open(document_path, "w") as file:
        file.write(soup.prettify())


def fix_book(book_path: str, save_path: str, text_align=""):
    """
    This function modifies an EPUB book to support bidirectional text, then saves it to
    a given location.
    :param book_path: Path to the original EPUB file
    :param save_path: Path for the output EPUB file
    :param text_align: Text align of the book's content (LTR or RTL) (optional)
    """
    # Checking if text align is valid
    text_align = text_align.lower()
    if text_align not in ("", "ltr", "rtl"):
        raise ValueError(f'Text align for document must be "ltr" or "rtl", not "{text_align}"')

    # Unzipping the book and getting the archive directory
    data_dir = unzip_book(book_path)

    # Fixing all documents in the book (HTML or XHTML files)
    for root, dirs, files in os.walk(data_dir, topdown=False):
        for name in files:
            path = os.path.join(root, name)
            if path.endswith(".html") or path.endswith(".xhtml"):
                fix_book_document(path, text_align)

    # Zipping the modified book and destroying the archive folder
    zip_book(save_path, data_dir)
    shutil.rmtree(data_dir)


def main():
    setup()
    fix_book("book.epub", "output.epub", "rtl")


if __name__ == '__main__':
    main()
