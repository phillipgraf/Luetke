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
            requests.get(f"http://127.0.0.1:5000/fields").text
        )
        x = ""
        for i in res:
            x = x + "\n\t> " + str(i)
        dispatcher.utter_message(text = f"Dies sind alle uns Verfügbaren Studienrichtungen: {x}")
        return []
