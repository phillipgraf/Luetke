from flask import Flask, request, jsonify
from markupsafe import escape
from scraper import ThdScraper
import json

app = Flask(__name__)

scraper = ThdScraper()
try:
    with open("./majors.json", "r") as file:
        print('[LOAD] Loading "majors.json" file...')
        majors = json.load(file)
    if len(majors) == 0:
        print("[LOAD] Using Webscraper...")
        majors = scraper.makeAllPretty("majors")
except Exception:
    print("[LOAD] Using Webscraper...")
    majors = scraper.makeAllPretty("majors")
try:
    with open("./fields.json", "r") as file:
        print('[LOAD] Loading "fields.json" file...')
        fields = json.load(file)
    if len(fields) == 0:
        print("[LOAD] Using Webscraper...")
        fields = scraper.makeAllPretty("fields")
except Exception:
    print("[LOAD] Using Webscraper...")
    fields = scraper.makeAllPretty("fields")
if fields:
    for f in fields:
        if f["name"] == "Berufsbegleitende Studiengänge":
            fields.remove(f)


def over_one(element):
    valid = [m for m in majors if m["name"] == element]
    if len(valid) == 1:
        return False
    m = 0
    b = 0
    for v in valid:
        if v["abschluss"].lower() == "master":
            m += 1
        if v["abschluss"].lower() == "bachelor":
            b += 1
    return m >= 1 and b >= 1


# Returns majors for degree
@app.get("/degrees/<degree>")
def get_degree_majors(degree):
    return jsonify(
        [
            x["name"]
            for x in majors
            if escape(degree).lower() in [c.lower() for c in x["abschluss"]]
        ]
    )


# Returns all majors by name
@app.get("/majors")
def get_majors():
    return jsonify([x["name"] for x in majors])


# Returns if major exists
@app.get("/majors/exists/<major>")
def major_exists(major):
    return (
        {"exists": True}
        if escape(major) in [x["name"] for x in majors]
        else {"exists": False}
    )


# Returns if field exists
@app.get("/fields/exists/<field>")
def field_exists(field):
    return (
        {"exists": True}
        if escape(field) in [x["name"] for x in fields]
        else {"exists": False}
    )


# Returns full major information
@app.get("/majors/<major>")
def get_major(major):
    if over_one(escape(major)):
        return jsonify(
            "Error. Fehlender Abschluss.")
    for m in majors:
        if m["name"].lower() == escape(major).lower():
            return jsonify(m)
    return jsonify({"name": "Kein Studiengang mit diesem Namen gefunden!"})


# Returns available categories from major
@app.get("/majors/<major>/categories")
def get_categories(major):
    if over_one(escape(major)):
        return jsonify(
            "Error. Fehlender Abschluss.")
    for m in majors:
        if m["name"].lower() == escape(major).lower():
            return jsonify(list(m.keys()))
    return jsonify({"name": "Kein Studiengang mit diesem Namen gefunden!"})


# Returns a specific piece of information from major
@app.get("/majors/<major>/<category>")
def get_major_category(major, category):
    if over_one(escape(major)):
        return jsonify(
            "Error. Fehlender Abschluss.")
    for m in majors:
        if m["name"].lower() == escape(major).lower():
            try:
                return jsonify(m[escape(category).lower()])
            except KeyError:
                return jsonify({"info": f"{escape(category)} not found"})
    return jsonify({"name": "Kein Studiengang mit diesem Namen gefunden!"})


@app.get("/majors/<major>/<degree>/categories")
def get_degree_categories(major, degree):
    for m in majors:
        if m["name"].lower() == escape(major).lower() and m["abschluss"].lower() == escape(degree).lower():
            return jsonify(list(m.keys()))
    return jsonify({"name": "Kein Studiengang mit diesem Namen gefunden!"})


@app.get("/majors/<major>/<degree>/<category>")
def get_major_degree_category(major, category, degree):
    for m in majors:
        if m["name"].lower() == escape(major).lower() and m["abschluss"].lower() == escape(degree).lower():
            try:
                return jsonify(m[escape(category).lower()])
            except KeyError:
                return jsonify({"info": f"{escape(category)} not found"})
    return jsonify({"name": "Kein Studiengang mit diesem Namen und Abschluss gefunden!"})


# Returns a list of all fields
@app.get("/fields")
def get_fields():
    return jsonify([x["name"] for x in fields])


# Returns all majors concerning a field
@app.get("/fields/<field>/majors")
def get_field_majors(field):
    for f in fields:
        if f["name"].lower() == escape(field).lower():
            return jsonify(f["majors"])
    return jsonify({"name": "Kein Studienfeld mit diesem Namen gefunden!"})


# Returns all majors concerning a field
@app.get("/fields/<field>/majors/<degree>")
def get_field_majors_degrees(field, degree):
    for f in fields:
        if f["name"].lower() == escape(field).lower():
            return jsonify(f["majors"][0][f"{escape(degree).lower()}"])

    return jsonify({"name": "Kein Studienfeld mit diesem Namen gefunden!"})
