# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import json
from rasa_sdk.events import SlotSet


class ActionStudiengangVorhanden(Action):
    def name(self) -> Text:
        return "action_studiengang_vorhanden"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        field = tracker.get_slot("studiengang")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/exists/{field}").text
        )
        return [SlotSet("studiengang_vorhanden", res["exists"])]


class ActionStudienrichtungVorhanden(Action):
    def name(self) -> Text:
        return "action_studienrichtung_vorhanden"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        field = tracker.get_slot("studienrichtung")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/fields/exists/{field}").text
        )
        return [SlotSet("studienrichtung_vorhanden", res["exists"])]

class ActionStudienrichtung(Action):
    def name(self) -> Text:
        return "action_studienrichtung"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/fields").text
        )
        x = ""
        for i in res:
            x = x + "\n\t> " + str(i)
        dispatcher.utter_message(text = f"Dies sind alle uns Verfügbaren Studienrichtungen: {x}")
        return []

class ActionStudiengangVonStudienrichtung(Action):
    def name(self) -> Text:
        return "action_studiengang_von_studienrichtung"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        field = tracker.get_slot("studienrichtung")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/fields/{field}/majors").text
        )
        abschluss = tracker.get_slot("abschluss")
        amount = 3 * (tracker.get_slot("svs_spoken")+1) if tracker.get_slot("svs_spoken") is not None else 3
        x = ""
        if abschluss:
            for i in res[0][abschluss.lower()][amount-3:amount]:
                x = x + "\n\t> " + str(i)
        else:
            f = res[0]["bachelor"] + res[0]["master"]
            for i in f[:3]:
                x = x + "\n\t> " + str(i)

        dispatcher.utter_message(text = f"{x}")
        return [SlotSet("svs_spoken", (amount / 3))]

class ActionStudiengangVonAbschluss(Action):
    def name(self) -> Text:
        return "action_studiengang_von_abschluss"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        abschluss = tracker.get_slot("abschluss")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/degrees/{abschluss}").text
        )
        amount = 3 * (tracker.get_slot("sva_spoken")+1) if tracker.get_slot("sva_spoken") is not None else 3
        x = ""
        for i in res[amount-3:amount]:
            x = x + "\n\t> " + str(i)

        dispatcher.utter_message(text = f"{x}")
        return [SlotSet("sva_spoken", (amount / 3))]

class ActionKategorienVonStudiengang(Action):
    def name(self) -> Text:
        return "action_kategorien_von_studiengang"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        major = tracker.get_slot("studiengang")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/categories").text
        )
        amount = 3 * (tracker.get_slot("kvs_spoken")+1) if tracker.get_slot("kvs_spoken") is not None else 3
        x = ""
        for i in res[amount-3:amount]:
            x = x + "\n\t> " + str(i)

        dispatcher.utter_message(text = f"{x}")
        return [SlotSet("kvs_spoken", (amount / 3))]

class ActionKategorieVonStudiengang(Action):
    def name(self) -> Text:
        return "action_kategorie_von_studiengang"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        major = tracker.get_slot("studiengang")
        info = tracker.get_slot("info")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/{info}").text
        )
        if "info" in res:
            dispatcher.utter_message(text = f"Zu dieser Kategorie wurde noch keine Information bereitgestellt.")
        else:
            dispatcher.utter_message(text = f"Zur Information {info} konnte ich diese Informationen finden: {res}")
        return []
