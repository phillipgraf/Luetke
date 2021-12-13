import requests
import json
from bs4 import BeautifulSoup


class Major:
    def __init__(self, major, link, field, degree):
        self.major = major
        self.link = link
        self.field = field
        self.categories = []
        self.degree = degree

    def __str__(self):
        str = "\n> ".join(self.categories)
        return f"{self.major}:\n> {self.link}\n> {self.degree}\n> {self.field}\n> {str}"

class ThdScraper:
    """Class to automate our web scraping"""

    def __init__(self):
        self.majors = []
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

        deg = ""
        for idx, s in enumerate(self.sg1):
            for s in s:
                title = s.find("p").text.strip()
                if title.replace(".", "").lower() == "bachelor":
                    deg = "Bachelor"
                    continue
                if title.replace(".", "").lower() == "master":
                    deg = "Master"
                    continue
                link = s.find("a")
                self.majors.append(
                    Major(
                        degree=deg,
                        major=title.replace("/", "_"),
                        link=self.URL + link.get("href"),
                        field=self.felder[idx],
                    )
                )

    def getStudyFields(self):
        """ Returns all possible fields"""
        return self.felder

    def getStudyMajorsForField(self, feld):
        """ Return all majors for a certain field, divided by degree
        """
        return {"bachelor": [x.major for x in self.majors if x.field == feld and x.degree == "Bachelor"], "master": [[x.major for x in self.majors if x.field == feld and x.degree == "Master"]]}

    def setFacultPage(self, link):
        """ Set new URL to be parsed and set requested html page
        """
        if self.pageSource != link:
            self.pageSource = link
            page = requests.get(link)
            self.page = BeautifulSoup(page.content, "html.parser")

    def getFacultPagePart(self, title):
        """ Returns certain part of the html page from major based on title
        """
        if title == "summary":
            return self.page.find("div", class_="fakultaet-text-info")
        for s in self.page.find_all("div", class_="section_title"):
            h2 = s.find("h2")
            if title in h2.text.lower():
                return s.parent

    def getInfoForMajor(self, major):
        """get wanted page"""
        self.setFacultPage(major.link)
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
                    steckbriefdict[x.text.split(":")[0].strip().lower()] = x.text.split(
                        ":"
                    )[1].strip()
        except Exception:
            return steckbriefdict
        return steckbriefdict

    def getJobInfoForMajor(self, major):
        """Get job information for major"""
        self.setFacultPage(major.link)
        try:
            job = self.getFacultPagePart("berufsbild")
            return [x.text for x in job.find_all("li") if x.text != "u.v.m"]
        except Exception:
            return ["No jobs found"]

    def getSummaryForMajor(self, major):
        """Get Summary from the major"""
        self.setFacultPage(major.link)
        try:
            summaryPage = self.getFacultPagePart("summary")
            longest_string = max([x.text for x in summaryPage.find_all("p")], key=len)
            return '. '.join(longest_string.split('.')[:4])+'.'
        except Exception as e:
            return "No summary found"

    def getKeywordsForMajor(self, major):
        """ Method that returns all keywords for a certain major
        """
        self.setFacultPage(major.link)
        summaryPage = self.getFacultPagePart("summary")
        try:
            return [x.text for x in summaryPage.find_all("li")]
        except Exception:
            return ["No Keywords found"]

    def getCategory(self, major):
        """ Returns Dictionary of Categories with their value
        """
        l = self.getInfoForMajor(major)
        return {x: l[x] for x in l}

    def makeAllPretty(self, type):
        """ Method to create valid JSON objects and writes them into appropriate files
        """
        if type == "majors":
            majors = []
            for idx, major in enumerate(self.majors):
                categories = self.getCategory(major)
                entry = {
                    "beschreibung": self.getSummaryForMajor(major),
                    "schwerpunkte": self.getKeywordsForMajor(major),
                    "name": major.major,
                    "studienrichtung": major.field,
                    "berufsbild": self.getJobInfoForMajor(major),
                    "abschluss": major.degree
                }
                entry.update(categories)
                majors.append(entry)
            with open("./majors.json", "w+") as f:
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
                f.write(json.dumps(fields))
            self.cleanFile("./fields.json")
            return fields

    def cleanFile(self, filename):
        """ Makes File syntax valid for json format, changes " to '
        filename - path to the to be written file
        """
        with open(filename, "r") as file:
            filedata = file.read()

        filedata = filedata.replace("'", '"')

        with open(filename, "w+") as file:
            file.write(filedata)
