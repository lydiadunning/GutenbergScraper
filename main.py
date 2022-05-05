# produces csv files of information scraped from project gutenberg's lists of top 100 downloads.
import csv
import requests as requests
from bs4 import BeautifulSoup


gutenberg_url = 'https://www.gutenberg.org/browse/scores/top'

response = requests.get(gutenberg_url)
gutenberg_site = response.text

soup = BeautifulSoup(gutenberg_site, 'html.parser')


list_of_lists = []
for ol in soup.find_all('ol'):
    new_list = []
    for li in ol.find_all('a'):
        new_list.append(li.get_text())
    list_of_lists.append(new_list)

ebooks_yesterday, authors_yesterday, ebooks_7_days, authors_7_days, ebooks_30_days, authors_30_days = list_of_lists


# ---------------For Writing to a CSV--------------

# the strings with authors and title of books end with a number of downloads. This removes and returns that number.
def separate_count(text_with_count):
    text = text_with_count.rstrip('(1234567890)')
    count = text_with_count[len(text):].strip('()')
    return text[:-1], count


def separate_author(title_with_author):
    if 'by' not in title_with_author:
        return title_with_author, ''
    title, author = title_with_author.rsplit(' by ', maxsplit=1)
    return title, author

# for authors with multiple names
def separate_extra_names(author_name):
    if "(" in author_name:
        name1, name2 = author_name.split("(")
        return name1[:-1], name2[:-1]
    else:
        return author_name, ""

def build_ebook_row(entry):
    text, count = separate_count(entry)
    title, author = separate_author(text)
    return {'title': title, 'author': author, 'downloads': count}


def save_to_csv(filename, all_items, fieldnames):
    # set the encoding to write unwriteable characters, probably a book titled with Chinese characters
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # set the delimeter to '|' because all names are written with commas.
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        for item in all_items:
            writer.writerow(item)


def save_ebook_info_to_csv(ebook_list, filename):
    formatted_list = []
    for ebook in ebook_list:
        formatted_list.append(build_ebook_row(ebook))
    save_to_csv(filename, formatted_list, formatted_list[0].keys())

def save_author_info_to_csv(author_list, filename):
    formatted_list = []
    for author in author_list:
        author, count = separate_count(author)
        author1, author2 = separate_extra_names(author)
        formatted_list.append({'author': author1, 'aka': author2, 'downloads': count})
    save_to_csv(filename, formatted_list, formatted_list[0].keys())


ebooks = {'ebooks_yesterday': ebooks_yesterday, 'ebooks_7_days': ebooks_7_days, 'ebooks_30_days': ebooks_30_days}
authors = {'authors_yesterday': authors_yesterday, 'authors_7_days': authors_7_days, 'authors_30_days': authors_30_days}

for ebook in ebooks:
    save_ebook_info_to_csv(ebooks[ebook], ebook)

for author in authors:
    save_author_info_to_csv(authors[author], author)