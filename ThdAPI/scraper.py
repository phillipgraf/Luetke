import requests
import json
import os
from bs4 import BeautifulSoup


class ThdScraper:
    """ Class to automate our we  

    """
    def __init__(self):
        self.categories = [
            "studienabschluss",
            "regelstudienzeit",
            "studienbeginn",
            "studienort",
            "unterrichtssprache",
            "schwerpunkte",
            "zulassungsvoraussetzung",
            "studentenwerksbeitrag",
            "kontakt"
        ]
        self.URL = "https://th-deg.de"
        page = requests.get(self.URL + "/studienfelder")
        soup = BeautifulSoup(page.content, "html.parser")
        self.page = None
        self.pageSource = None

        self.felder = []
        for feld in soup.find_all("div", class_="fakultaet-text-info"):
            self.felder.append(feld.find("h2").text)

        studiengaenge = soup.find_all("div", class_="studienprogramm-info")
        self.sg1 = []
        for sg in studiengaenge:
            self.sg1.append(sg.find_all("div", class_="card-body"))

        self.links = {}
        self.sg2 = []
        for idx, s in enumerate(self.sg1):
            self.sg2.append({})
            for s in s:
                title = s.find("p").text.strip()
                if title.replace(".", "").lower() == "bachelor":
                    self.sg2[idx][title.replace(".", "").lower()] = []
                    continue
                if title.replace(".", "").lower() == "master":
                    self.sg2[idx][title.replace(".", "").lower()] = []
                    continue
                link = s.find("a")
                self.sg2[idx][
                "bachelor" if len(self.sg2[idx]) == 1 else "master"
                ].append(title.replace("/", "_"))
                self.links[title.replace("/", "_")] = self.URL + link.get("href")

        self.studien = {}
        self.studToField = {x: "" for x in list(self.links.keys())}
        for idx, i in enumerate(self.felder):
            if i in self.studien:
                self.studien[i].append(self.sg2[idx])
            else:
                self.studien[i] = [self.sg2[idx]]
        for f in self.felder:
            fls = self.studien[f][0]["bachelor"] + self.studien[f][0]["master"]
            for fss in fls:
                self.studToField[fss] = f

    def getStudyFields(self):
        return self.felder

    def getStudyMajorsForField(self, feld):
        return self.studien[feld]

    def setFacultPage(self, major):
        if self.pageSource != self.links[major]:
            self.pageSource = self.links[major]
            page = requests.get(self.links[major])
            self.page = BeautifulSoup(
                page.content, "html.parser"
            )
            with open(f"./Scriptdata/{major}.html", "w+") as majors:
                majors.write(page.text)


    def getFacultPagePart(self, title):
        if title == "summary":
            return self.page.find("div", class_="fakultaet-text-info")
        for s in self.page.find_all("div", class_="section_title"):
            h2 = s.find("h2")
            if title in h2.text.lower():
                return s.parent

    def getAllInfo(self, major):
        self.setFacultPage(major)
        information = []
        information.append(f"# {major}\n")
        information.append(f"# {self.links[major]}\n\n\n")

        information.append("intent: job\n")
        for x in self.getJobInfoForMajor(major):
            information.append(f"\t- {x.lower().strip()}\n")

        information.append("\nintent: summary\n")
        information.append(f"\t- {self.getSummaryForMajor(major).lower().strip()}\n")

        information.append("\nintent: keywords\n")
        for x in self.getKeywordsForMajor(major):
            information.append(f"\t- {x.lower().strip()}\n")

        information.append("\nintent: characteristics\n")
        for x in self.getInfoForMajor(major):
            information.append(f"\t- {x.lower().strip()}\n")
        self.page = None
        return information

    def getInfoForMajor(self, major):
        """get Steckbrief"""
        self.setFacultPage(major)
        steckbriefdict = {}
        try:
            steckbriefpage = self.getFacultPagePart("steckbrief")
            lists = steckbriefpage.find_all("ul")[::-1]
            for x in steckbriefpage.find_all("p"):
                if len(x) == 1 or x.text.split(":")[1].strip() == "":
                    steckbriefdict[x.text.split(":")[0].strip()] = [
                        x.text for x in lists.pop().find_all("li")
                    ]
                else:
                    steckbriefdict[x.text.split(":")[0].strip().lower()] = x.text.split(":")[
                    1
                    ].strip()
        except Exception:
            return steckbriefdict
        return steckbriefdict

    def getJobInfoForMajor(self, major):
        """Get job information for major"""
        self.setFacultPage(major)
        try:
            job = self.getFacultPagePart("berufsbild")
            return [x.text for x in job.find_all("li") if x.text != "u.v.m"]
        except Exception:
            return ["No jobs found"]

    def getSummaryForMajor(self, major):
        """Get Summary from the major job"""
        self.setFacultPage(major)
        try:
            summaryPage = self.getFacultPagePart("summary")
            longest_string = max([x.text for x in summaryPage.find_all("p")], key=len)
            return longest_string
        except Exception:
            return "No summary found"

    def getKeywordsForMajor(self, major):
        self.setFacultPage(major)
        summaryPage = self.getFacultPagePart("summary")
        try:
            return [x.text for x in summaryPage.find_all("li")]
        except Exception:
            return ["No Keywords found"]

    def downloadAll(self):
        try:
            os.makedirs("./Scriptdata")
        except OSError as error:
            pass
        with open("./Scriptdata/fields.yml", "w+") as fields:
            fields.write("intent: fields\n")
            for f in x.felder:
                fields.write(f"\t- {f.lower().strip()}\n")

        with open("./Scriptdata/majors.yml", "w+") as majors:
            majors.write("intent: majors\n")
            for m in x.links.keys():
                majors.write(f"\t- {m.lower().strip()}\n")

        for major in x.links.keys():
            major = major.replace("/", "_")
            with open(f"./Scriptdata/{major}.yml", "w+") as majors:
                infos = x.getAllInfo(major)
                for i in infos:
                    majors.write(i)

    def getCategory(self, major):
        l = self.getInfoForMajor(major)
        return {x:l[x] for x in l}

    def getDegreeForMajor(self, major):
        field = self.studToField[major]
        if major in self.studien[field][0]["bachelor"]:
            if major in self.studien[field][0]["master"]:
                return ["Bachelor", "Master"]
            else:
                return ["Bachelor"]
        elif major in self.studien[field][0]["master"]:
            return ["Master"]

    def makeAllPretty(self, type):
        if type == "majors":
            majors = []
            for idx, major in enumerate(list(self.links.keys())):
                categories = self.getCategory(major)
                entry = {
                    "id": idx,
                    "desc": self.getSummaryForMajor(major),
                    "schwerpunkte": self.getKeywordsForMajor(major),
                    "name": major,
                    "feld": self.studToField[major],
                    "jobs": self.getJobInfoForMajor(major),
                    "link": self.links[major],
                    "degree": self.getDegreeForMajor(major)
                }
                entry.update(categories)
                majors.append(entry)
            with open("./majors.json", "w+") as f:
                # for p in majors:
                #     print(p, file=f)
                f.write(json.dumps(majors))
            self.cleanFile("./majors.json")
            return majors

        if type == "fields":
            fields = []
            for idx, field in enumerate(self.felder):
                entry = {
                    "id": idx,
                    "name": field,
                    "majors": self.getStudyMajorsForField(field)
                }
                fields.append(entry)
            with open("./fields.json", "w+") as f:
                # for p in fields:
                #     print(p, file=f)
                f.write(json.dumps(fields))
            self.cleanFile("./fields.json")
            return fields

    def cleanFile(self, filename):
        with open(filename, 'r') as file :
            filedata = file.read()
            
        filedata = filedata.replace('\'', '"')
            
        with open(filename, 'w+') as file:
            file.write(filedata)
