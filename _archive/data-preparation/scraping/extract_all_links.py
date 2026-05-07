import json
from bs4 import BeautifulSoup
import requests
import re
import os


pages_per_year = {2023: 14, 2022: 45}

#2021: 51, 2020: 52, 2019: 53, 2018: 47, 2017: 45, 2016: 53, 2015: 48, 2014: 15 remaining years to be run

urls = []
for year, pages in pages_per_year.items():
    url = f"https://www.berlin.de/polizei/polizeimeldungen/archiv/{year}/"
    urls.append(url)
    for i in range(2, pages + 1):
        url = f"https://www.berlin.de/polizei/polizeimeldungen/archiv/{year}/?page_at_1_0={i}"
        urls.append(url)

# Create the "raw-data" folder if it doesn't exist
folder_path = "/Users/mac123/code/finding-conan/raw-data"
os.makedirs(folder_path, exist_ok=True)


for url in urls:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    urls_each_case = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if re.fullmatch(r".*pressemitteilung\.\d+\.php$", a["href"])
    ]
    urls_each_case = ["https://www.berlin.de" + x for x in urls_each_case]
    for police_case in urls_each_case:
        try:
            to_save = {}
            html = requests.get(police_case).text
            soup = BeautifulSoup(html, "html.parser")

            title = soup.find("div", {"id": "layout-grid__area--herounit"}).h1.text
            main_content = soup.find("div", {"id": "layout-grid__area--maincontent"})
            place = main_content.find_all("p", {"class": "polizeimeldung"})[1].text
            date = main_content.find("p", {"class": "polizeimeldung"}).text.split(" ")[-1]
            subtitle = (
                main_content.find("div", {"class": "textile"}).find("p").text.strip()
            )
            if "Nr. " in subtitle:
                subtitle = ""
            paragraphs = main_content.find("div", {"class": "textile"}).find_all("p")
            data = []
            for paragraph in paragraphs:
                if paragraph.strong is not None:

                    number = paragraph.strong.text.split(". ")[-1]
                    description = paragraph.text.replace(
                        paragraph.strong.text, ""
                    ).strip()
                    data.append({"number": number, "description": description})
            to_save["title"] = title
            to_save["place"] = place
            to_save["date"] = date
            to_save["subtitle"] = subtitle
            to_save["data"] = data

            with open(
                police_case[police_case.rfind("/") + 1 :][0:-3] + "json", "w"
            ) as json_file:
                json.dump(to_save, json_file, indent=4, ensure_ascii=False)
        except:
            print(f"error in {police_case}")
