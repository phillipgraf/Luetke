from flask import Flask, request, jsonify
from markupsafe import escape
from scraper import ThdScraper 
import json

app = Flask(__name__)

scraper = ThdScraper()
try:
    with open("./majors.json", "r") as file:
        print("[LOAD] Loading \"majors.json\" file...")
        majors = json.load(file)
    if len(majors) == 0:
        print("[LOAD] Using Webscraper...")
        majors = scraper.makeAllPretty("majors")
except Exception:
    print("[LOAD] Using Webscraper...")
    majors = scraper.makeAllPretty("majors")


try:
    with open("./fields.json", "r") as file:
        print("[LOAD] Loading \"fields.json\" file...")
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


@app.get("/degrees/<degree>") # Returns majors for degree 
def get_degree_majors(degree):
    return jsonify([x["name"] for x in majors if escape(degree).lower() in [c.lower() for c in x["degree"]]])
@app.get("/majors")
def get_majors():
    return jsonify([x["name"] for x in majors])
@app.get("/majors/exists/<major>")
def major_exists(major):
    return {"exists": True} if escape(major) in [x["name"] for x in majors] else {"exists": False}
@app.get("/fields/exists/<field>")
def field_exists(field):
    return {"exists": True} if escape(field) in [x["name"] for x in fields] else {"exists": False}
@app.get("/majors/<major>") # Returns full major information
def get_major(major):
    for m in majors:
        if m["name"].lower() == escape(major).lower():
            return jsonify(m)
    return jsonify({"name": "Kein Studiengang mit diesem Namen gefunden!"})
@app.get("/majors/<major>/categories") # Returns available categories from major
def get_categories(major):
    for m in majors:
        if m["name"].lower() == escape(major).lower():
            return jsonify(list(m.keys()))
    return jsonify({"name": "Kein Studiengang mit diesem Namen gefunden!"})
@app.get("/majors/<major>/<category>") # Returns a specific piece of information from major
def get_major_category(major, category):
    for m in majors:
        if m["name"].lower() == escape(major).lower():
            try:
                return jsonify(m[escape(category).lower()])
            except KeyError:
                return jsonify({"info": f"{escape(category)} not found"})
    return jsonify({"name": "Kein Studiengang mit diesem Namen gefunden!"})
@app.get("/fields") # Returns a list of Fields
def get_fields():
    return jsonify([x["name"] for x in fields])
@app.get("/fields/<field>/majors") # Returns all majors concerning a field
def get_field_majors(field):
    for f in fields:
        if f["name"].lower() == escape(field).lower():
            return jsonify(f["majors"])
    return jsonify({"name": "Kein Studienfeld mit diesem Namen gefunden!"})
@app.get("/fields/<field>/majors/<degree>") # Returns all majors concerning a field
def get_field_majors_degrees(field, degree):
    for f in fields:
        if f["name"].lower() == escape(field).lower():
            return jsonify(f["majors"][0][f"{escape(degree).lower()}"])
    return jsonify({"name": "Kein Studienfeld mit diesem Namen gefunden!"})
