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
import random
from rasa_sdk.events import SlotSet


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
    # Gibt alle verfügbaren Studienrichtungen an
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

class ActionStudiengang(Action):
    #Gibt die Beschreibung des Studiengangs aus
    def name(self) -> Text:
        return "action_studiengang"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        major = tracker.get_slot("studiengang")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/desc").text
        )
        if res=="":
            dispatcher.utter_message(text="Oh das ist aber schade. Leider fehlt die Beschreibung des Studiengangs in meinem Lexikon. Ich habe aber trotzdem ein paar Infos zu diesem gefunden. Sie können z.B. nach folgendem fragen:")
            dispatcher.utter_message(Help.list_info_3(tracker))
        else:
            dispatcher.utter_message(text = f"{res}")
            dispatcher.utter_message(text="Ich kann Ihnen noch mehr Informationen über diesen Studiengang bereitstellen. Wie wäre es zum Beispiel mit einer der folgenden Kategorie?")
            dispatcher.utter_message(Help.list_info_3(tracker))
        return []


class ActionStudiengang(Action):
    #Gibt immer 3 Studiengänge einer Studienrichtung aus mit oder ohne abschluss
    def name(self) -> Text:
        return "action_studiengang_list_sr"

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
        amount = 3 * (tracker.get_slot(f"svs_spoken_{field}")+1) if tracker.get_slot(f"svs_spoken_{field}") is not None else 3
        x = ""
        if abschluss:
            for i in res[0][abschluss.lower()][amount-3:amount]:
                x = x + "\n\t> " + str(i)
        else:
            f = res[0]["bachelor"] + res[0]["master"]
            for i in f[:3]:
                x = x + "\n\t> " + str(i)

        dispatcher.utter_message(text = f"{x}")
        return [SlotSet(f"svs_spoken_{field}", (amount / 3))]

class ActionStudiengangListVonStudienrichtung(Action):
    #Gibt alle Studiengänge einer Studienrichtung aus
    def name(self) -> Text:
        return "action_studiengang_list_all_sr"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        field = tracker.get_slot("studiengang")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/fields/{field}/majors").text
        )
        x = ""
        for i in res:
            x = x + "\n\t> " + str(i)
        dispatcher.utter_message(text=f"Okay. Hier bitte sehr alle Studiengänge der Studienrichtung \"{field}\" ")
        dispatcher.utter_message(text = f"{x}")
        return []

class ActionStudiengangList(Action):
    # Gibt 3 Studiengänge eines abschluss aus
    def name(self) -> Text:
        return "action_studiengang_list"

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

class ActionStudiengangListAll(Action):
    # Gibt alle Studiengänge aus
    def name(self) -> Text:
        return "action_studiengang_list_all"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        if tracker.latest_message == "Ja":
            res = json.loads(
                requests.get(f"http://127.0.0.1:5000/majors").text
            )
            resp = [f"\n\t> {x}" for x in res]
            x = ""
            for i in resp:
                x = x + str(i)
            dispatcher.utter_message(text = f"{x}")
        else:
            dispatcher.utter_message(text="Dann fragen Sie mich etwas anderes, bei dem ich Ihnen weiterhelfen kann. Aber verschwenden Sie nicht meine wertvolle Zeit.")
        return []

class ActionInfo(Action):
    def name(self) -> Text:
        return "action_info"

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
            dispatcher.utter_message(text = f"Diese Kategorie wurde für diesen Studiengang nicht angelegt")
            dispatcher.utter_message(text= "Sie können sich alle verfügbaren Kategorien mit dem Zauberwort 'Sonnenvogel' ausgeben lassen oder versuchen Sie es zum Beispiel mit einer dieser: ")
            dispatcher.utter_message(Help.list_info_3(tracker))
        else:
            dispatcher.utter_message(text = f"Zur Information {info} konnte ich diese Informationen finden: {res}")
        return []

class ActionInfoList(Action):
    #Listet 3 Kategorien der Info auf
    def name(self) -> Text:
        return "action_info_list"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        x=Help.list_info_3(tracker)
        dispatcher.utter_message(text=f"{x}")
        return []


class ActionInfoListAll(Action):
    def name(self) -> Text:
        return "action_info_list_all"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        if tracker.latest_message == "Sonnenvogel":
            major = tracker.get_slot("studiengang")
            res = json.loads(
                requests.get(f"http://127.0.0.1:5000/majors/{major}/categories").text
            )
            resp = [f"\n\t> {x}" for x in res]

            x = ""
            for i in resp:
                x = x + str(i)
            dispatcher.utter_message(text=f"{x}")
        return []

class ActionWiederholen(Action):
    #wiederholt alles bis zum letzen user input
    def name(self) -> Text:
        return "action_wiederholen"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_ignore_count = 2
        count = 0
        tracker_list = []

        while user_ignore_count > 0:
            event = tracker.events[count].get('event')
            if event == 'user':
                user_ignore_count = user_ignore_count - 1
            if event == 'bot':
                tracker_list.append(tracker.events[count])
            count = count - 1

        i = len(tracker_list) - 1
        while i >= 0:
            data = tracker_list[i].get('data')
            if data:
                if "buttons" in data:
                    dispatcher.utter_message(text=tracker_list[i].get('text'), buttons=data["buttons"])
                else:
                    dispatcher.utter_message(text=tracker_list[i].get('text'))
            i -= 1

        return []



class Help():
    def list_info_3(self, tracker: Tracker):
        major = tracker.get_slot("studiengang")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/categories").text
        )
        resp = [f"\n\t> {x}" for x in random.sample(res, 3)]

        x = ""
        for i in resp:
            x = x + str(i)
        return x



