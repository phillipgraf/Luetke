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

        res = " \n\t> " + " \n\t> ".join(res) + "\n "

        dispatcher.utter_message(
            text=f"{res}\n \n Wählen Sie davon bitte Ihre bevorzugte Studienrichtung aus,"
                 f" damit ich meine Suche nach einem Studiengang noch weiter einschränken kann.")
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
    # Gibt die Beschreibung des Studiengangs aus
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
            requests.get(f"http://127.0.0.1:5000/majors/{major}/beschreibung").text
        )
        if res == "No summary found" or res == "":
            dispatcher.utter_message(
                text=f"Oh das tut mir jetzt sehr Leid. Aber ich finde in unserem Verzeichnis keine Beschreibung zu dem "
                     f"Studiengang {major}. Zu dem Studiengang stehen hier nur Informationen zu folgenden Kategorien: "
                     f"\n{list_info_3(tracker, 'beschreibung')} \n\nNennen Sie mir doch bitte die Kategorie zu der ich Ihnen "
                     f"die Informationen vorlesen soll.")
        else:
            dispatcher.utter_message(
                text=f" \n{res}\n \nMöchten Sie noch mehr über diesen Studiengang erfahren? Im Inhaltsverzeichnis habe "
                     f"ich dazu noch folgende Kategorien gefunden: \n \n{list_info_3(tracker, 'beschreibung')}")
        return []


class ActionStudiengang(Action):
    # Gibt immer 3 Studiengänge einer Studienrichtung aus mit oder ohne abschluss
    # Gibt beim nächsten Aufruf die nächsten 3 Studiengänge aus
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
        amount = 3 * (tracker.get_slot(f"svs_spoken_{field}") + 1) if tracker.get_slot(
            f"svs_spoken_{field}") is not None else 3
        x = ""
        if abschluss:
            for i in res[0][abschluss.lower()][amount - 3:amount]:
                x = x + "\n\t> " + str(i)
        else:
            f = res[0]["bachelor"] + res[0]["master"]
            for i in f[:3]:
                x = x + "\n\t> " + str(i)

        dispatcher.utter_message(
            text=f"{x}\n\nWas klingt für Sie davon am interessantesten? Oder möchten Sie weitere Studiengänge der {field} hören?")
        return [SlotSet(f"svs_spoken_{field}", (amount / 3))]


class ActionStudiengangListVonStudienrichtung(Action):
    # Gibt alle Studiengänge einer Studienrichtung aus
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
        x = "Bachelor Studiengänge: \n" + " \n\t> ".join(
            res[0]["bachelor"]) + "Master Studiengänge: \n" + " \n\t> ".join(res[0]["master"])
        dispatcher.utter_message(text=f"Okay. Hier bitte sehr alle Studiengänge der Studienrichtung \"{field}\"\n\n{x}")
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
        amount = 3 * (tracker.get_slot("sva_spoken") + 1) if tracker.get_slot("sva_spoken") is not None else 3
        x = ""
        for i in res[amount - 3:amount]:
            x = x + "\n\t> " + str(i)

        dispatcher.utter_message(text=f"{x}")
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
            dispatcher.utter_message(text=f"{x}")
        else:
            dispatcher.utter_message(
                text="Dann fragen Sie mich etwas anderes, bei dem ich Ihnen weiterhelfen kann. Aber verschwenden Sie "
                     "nicht meine wertvolle Zeit.")
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
            dispatcher.utter_message(
                text=f"Diese Kategorie wurde für diesen Studiengang nicht angelegt\n\n Sie können sich alle "
                     f"verfügbaren Kategorien mit dem Zauberwort 'Sonnenvogel' ausgeben lassen oder versuchen Sie es "
                     f"zum Beispiel mit einer dieser:\n\n{list_info_3(tracker, info)}")
        else:
            if isinstance(res, list):
                res = " \n\t> " + " \n\t> ".join(res) + "\n "
            if res == "'name': 'Kein Studiengang mit diesem Namen gefunden!'":
                dispatcher.utter_message(response="utter_studiengang_nicht_vorhanden")

            dispatcher.utter_message(text=f"Zur Information {info} konnte ich folgendes finden: {res}")

        return []


class ActionInfoNachfrage(Action):
    # Fragt nach ob der User noch mehr wissen möchte.
    def name(self) -> Text:
        return "action_info_nachfrage"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        info = tracker.get_slot("info")
        dispatcher.utter_message(response="utter_info_nachfrage", text=f" \n\t{list_info_3(tracker, info)}")
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
        if "Sonnenvogel" in tracker.latest_message:
            major = tracker.get_slot("studiengang")
            res = json.loads(
                requests.get(f"http://127.0.0.1:5000/majors/{major}/categories").text
            )
            resp = [f"\n\t> {x.capitalize()}" for x in res]

            x = ""
            for i in resp:
                x = x + str(i)
            dispatcher.utter_message(text=f"{x}")
        return []


class ActionWiederholen(Action):
    # wiederholt alles bis zum letzen user input
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


class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Entschuldigung, aber ich konnte Sie leider nicht verstehen. Sprechen Sie bitte etwas deutlicher.")

        # Revert user message which led to fallback.
        return []


def list_info_3(tracker: Tracker, info=""):
    major = tracker.get_slot("studiengang")
    res = json.loads(
        requests.get(f"http://127.0.0.1:5000/majors/{major}/categories").text
    )

    resp = [f"\n\t> {x.capitalize()}" for x in random.sample([r for r in res if r != info], 3)]

    return "".join(resp)
