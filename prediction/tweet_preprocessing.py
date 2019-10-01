from urllib.parse import urlparse

url_obj = urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')

print(url_obj.hostname)
print(url_obj.netloc)
