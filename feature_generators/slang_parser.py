import requests
from bs4 import BeautifulSoup

slangs = []

for i in range(ord('a'), ord('a') + 26):
    page_link = 'http://www.peevish.co.uk/slang/{}.htm'.format(chr(i))

    page_response = requests.get(page_link, timeout=5)

    page_content = BeautifulSoup(page_response.content, 'html.parser')

    objects = page_content.find_all('td', {'valign': 'TOP'})

    slangs.extend([obj.text.strip().lower() for obj in objects])

with open(r'D:\Data\Linkage\FL\FL18\lexicons\slangs_peevish_temp.txt', 'w') as wf:
    for slang in slangs:
        wf.write(slang + '\n')
