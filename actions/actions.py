# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import json
import random
from rasa_sdk.events import SlotSet
from rasa_sdk.events import ConversationPaused


# Überprüft ob die gewünschte Studienrichtung vorhanden ist
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


# Gibt alle verfügbaren Studienrichtungen an
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

        res = " \n \t> " + " \n\t> ".join(res) + "\n "

        dispatcher.utter_message(
            text=f"{res}\n Wählen Sie davon bitte Ihre bevorzugte Studienrichtung aus,"
                 f" damit ich meine Suche nach einem Studiengang der THD noch weiter einschränken kann.")
        return []


### STUDIENGANG ACTIONS
# Überprüft ob der Studiengang an der THD vorhanden ist
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


# Gibt den gewählten Studiengang mit der Beschreibung für diesen aus. Bzw. reagiert anderst, falls es keine Beschreibung gibt.
class ActionStudiengang(Action):
    def name(self) -> Text:
        return "action_studiengang"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        major = tracker.get_slot("studiengang")
        abschluss = tracker.get_slot("abschluss")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/{abschluss}/beschreibung").text
        ) if abschluss != None else json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/beschreibung").text
        )

        if res == "No summary found" or res == "":
            dispatcher.utter_message(
                text=f"Oh das tut mir jetzt sehr Leid. Aber ich finde in unserem Verzeichnis keine Beschreibung zu dem "
                     f"Studiengang {major}. Zu dem Studiengang stehen hier nur Informationen zu folgenden Kategorien: "
                     f"\n{list_info_3(tracker, 'beschreibung')} \n\nNennen Sie mir doch bitte die Kategorie zu der ich Ihnen "
                     f"die Informationen vorlesen soll.")
        elif res == "Error.  Fehlender Abschluss":
            dispatcher.utter_message(
                text="Oh. Ich brauch nochmal bitte Ihre Hilfe. Ich sehe gerade die Hochschule bietet diesen Studiengang als Bachelor, sowie als Master Abschluss an. "
                     "Sagen Sie mir doch bitte ob Sie was zu dem Bachelor oder dem Master Studiengang hören wollen.")
            return [SlotSet("abschluss_notwendig", True)]
        else:
            dispatcher.utter_message(
                text=f" Sehr gute Wahl! Einen Moment bitte. Ich schau kurz in meinem schlauen Büchlein nach."
                     f"Da steht zu dem Studiengang {major} folgendes "
                     f"geschrieben:\n {res}\n \nMöchten Sie noch mehr über "
                     f"diesen Studiengang erfahren? Im Inhaltsverzeichnis habe "
                     f"ich dazu noch folgende Kategorien gefunden: {list_info_3(tracker, 'beschreibung')}")
        return []


# Gibt immer 3 Studiengänge einer Studienrichtung aus mit oder ohne abschluss
# Gibt beim nächsten Aufruf die nächsten 3 Studiengänge aus
class ActionStudiengang(Action):
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
            f = res["bachelor"] + res["master"]
            for i in f[amount - 3:amount]:
                x = x + "\n\t> " + str(i)

        dispatcher.utter_message(
            text=f"{x}\n Was klingt für Sie davon am interessantesten? Oder möchten Sie weitere Studiengänge der Studienrichtung {field} hören?")
        return [SlotSet(f"svs_spoken_{field}", (amount / 3))]


# Gibt alle Studiengänge einer Studienrichtung aus
class ActionStudiengangListVonStudienrichtung(Action):
    def name(self) -> Text:
        return "action_studiengang_list_all_sr"

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
        x = "Bachelor Studiengänge: \n \n\t> " + " \n\t> ".join(
            res["bachelor"]) + " \n \n Master Studiengänge: \n \n\t> " + " \n\t> ".join(res["master"][0])
        dispatcher.utter_message(
            text=f"Hier bitte sehr alle Studiengänge der Studienrichtung \"{field}\"\n\n{x} \n Wählen Sie davon bitte den Studiengang aus der Sie interessiert.")
        return []


# Gibt 3 Studiengänge eines Abschluss aus, wenn man z.B. einfach ein bisschen stöbern möchte welche Bachelorstudiengänge es überhaupt gibt
class ActionStudiengangList(Action):

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


# Gibt alle Studiengänge aus
class ActionStudiengangListAll(Action):
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


### INFO Actions

# Gibt die ausgewählte Info zu dem jeweiligen Studiengang und reagiert im Zweifel auf Errors.
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
        abschluss = tracker.get_slot("abschluss")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/{abschluss}/{info}").text
        )

        if res == "Error: Kein Studiengang mit diesem Namen und Abschluss gefunden!":
            res = json.loads(
                requests.get(f"http://127.0.0.1:5000/majors/{major}/{info}").text
            )

        if "info" in res:
            dispatcher.utter_message(
                text=f"Tut mir Leid. Aber zu dieser Kategorie kann ich für diesen Studiengang nirgends was finden.")
        if "Informationen zum Bewerbungsprozess" in res:
            dispatcher.utter_message(
                text=f"Informationen zur Bewerbung findest du auf der Webseite der Technischen Hochschule Deggendorf.")

        elif res == "'name': 'Kein Studiengang mit diesem Namen gefunden!'":
            dispatcher.utter_message(template="utter_studiengang_nicht_vorhanden")

        elif info == "'name': 'Kein Studiengang mit diesem Namen gefunden!'":
            dispatcher.utter_message(template="utter_studiengang_nicht_vorhanden")

        else:
            if isinstance(res, list):
                res = " \n\t> " + " \n\t> ".join(res) + "\n "
                dispatcher.utter_message(text=f"Zur Information {info} konnte ich folgendes finden: {res}")
            else:
                dispatcher.utter_message(text=f"Zur Information {info} konnte ich folgendes finden: {res}")

        return []


# Gibt 3 Beispiel Kategorien aus zu dem noch mehr Information in dem Studiengang vorhanden sind
# Wird aufgerufen, nachdem der User gefragt wird ob er noch mehr Informationen haben will.
class ActionInfoNachfrage(Action):
    def name(self) -> Text:
        return "action_info_nachfrage"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        info = tracker.get_slot("info")
        dispatcher.utter_message(text=f" \n\t{list_info_3(tracker, info)}")
        return []


# Gibt alle Kategorien aus die für den jeweiligen Studiengang möglich sind abzufragen
class ActionInfoListAll(Action):
    def name(self) -> Text:
        return "action_info_list_all"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        major = tracker.get_slot("studiengang")
        abschluss = tracker.get_slot("abschluss")
        res = json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/{abschluss}/categories").text
        ) if abschluss != None else json.loads(
            requests.get(f"http://127.0.0.1:5000/majors/{major}/categories").text
        )
        resp = [f"\n\t> {x.capitalize()}" for x in res]

        x = ""
        for i in resp:
            x = x + str(i)
            dispatcher.utter_message(text=f"{x}")
        return []


# Stopt den Bot, so dass dieser auf keine Anfrage mehr reagieren kann.
class ActionStopTheConversation(Action):
    def name(self):
        return "action_stop_the_bot"

    def run(self, dispatcher, tracker, domain):
        return [ConversationPaused()]


# Wiederholt die zuletzt ausgegeben Actionen des Bots, falls der User etwas nicht verstanden hat
class ActionWiederholen(Action):
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
                dispatcher.utter_message(text=tracker_list[i].get('text'))
            i -= 1

        return []


### Hilfs Funktion ###
def list_info_3(tracker: Tracker, info=""):
    major = tracker.get_slot("studiengang")
    abschluss = tracker.get_slot("abschluss")
    res = json.loads(
        requests.get(f"http://127.0.0.1:5000/majors/{major}/{abschluss}/categories").text
    ) if abschluss != None else json.loads(
        requests.get(f"http://127.0.0.1:5000/majors/{major}/categories").text
    )

    try:
        res = [f" \n \t> {x.capitalize()}" for x in random.sample([r for r in res if r != info], 3)]
    except Exception:
        return "Leider ist ein Fehler aufgetreten. Bitte Starten Sie den Bot von vorne."
    return "".join(res)



## EVENTUELL NUETZLICHE METHODEN

# Methode um zu überprüfen ob es den Studiengang sowohl als Bachelor, als auch als Master gibt
# Damit nur nach dem Abschluss gefragt wird, wenn nötig, wenn der Studiengang nicht eindeutig ist
# class ActionAbschlussVorhanden(Action):
#     def name(self) -> Text:
#         return "action_abschluss_ueberpruefen"
#
#     def run(
#             self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         major = tracker.get_slot("studiengang")
#         res = json.loads(
#             requests.get(f"http://127.0.0.1:5000/majors/{major}/beschreibung").text
#         )
#
#         if res == "Error. Fehlender Abschluss.":
#             return [SlotSet("abschluss_notwendig", True)]
#         return [SlotSet("abschluss_notwendig", False)]
