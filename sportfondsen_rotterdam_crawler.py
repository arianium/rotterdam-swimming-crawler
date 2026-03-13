import requests
from datetime import datetime, timedelta

POOLS = {
    "Oostelijk Zwembad": "https://oostelijkzwembad.sportfondsen.nl/_next/data/pU8mujAfLdu9v2DAfnWDD/tijden-tarieven.json?slug=tijden-tarieven",
    "Oostervant": "https://oostervant.sportfondsen.nl/_next/data/pU8mujAfLdu9v2DAfnWDD/tijden-tarieven-van-oostervant.json?slug=tijden-tarieven-van-oostervant",
    "Zevenkampsering": "https://zevenkampsering.sportfondsen.nl/_next/data/pU8mujAfLdu9v2DAfnWDD/tijden-en-tarieven.json?slug=tijden-en-tarieven",
    "Van Maanenbad": "https://vanmaanenbad.sportfondsen.nl/_next/data/pU8mujAfLdu9v2DAfnWDD/tijden-tarieven.json?slug=tijden-tarieven",
}

KEYWORDS = ["banenzwemmen", "vrij zwemmen"]


def fetch_timeslots(url):
    headers = {"Accept": "application/json"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data["pageProps"]["extraPageProps"]["scheduleData"]["timeSlots"]


def filter_relevant_slots(timeslots):
    relevant = []
    for slot in timeslots:
        activity = slot.get("activitySchedule", {}).get("activity", {})
        title = activity.get("title", "")

        if any(k in title.lower() for k in KEYWORDS):
            relevant.append(
                {
                    "day": slot["day"],
                    "dayValue": slot["dayValue"],
                    "start": slot["startTime"],
                    "end": slot["endTime"],
                    "activity": title,
                }
            )

    return relevant


def classify_week(slots):
    today = datetime.today()
    weekday_today = today.weekday()  # Monday=0
    monday = today - timedelta(days=weekday_today)

    results = {"today": [], "week": []}

    day_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    for slot in slots:
        idx = day_map.get(slot["dayValue"])
        if idx is None:
            continue

        slot_date = monday + timedelta(days=idx)

        if slot_date.date() == today.date():
            results["today"].append(slot)

        if monday.date() <= slot_date.date() <= (monday + timedelta(days=6)).date():
            results["week"].append(slot)

    return results


def main():
    print("\n=== Swim Availability Report ===\n")

    for pool, url in POOLS.items():
        try:
            timeslots = fetch_timeslots(url)
            relevant = filter_relevant_slots(timeslots)
            classified = classify_week(relevant)

            print(f"--- {pool} ---")

            print("\nToday:")
            if not classified["today"]:
                print("  No lane or free swim today.")
            else:
                for s in classified["today"]:
                    print(f"  {s['start']}-{s['end']} {s['activity']}")

            print("\nThis Week:")
            if not classified["week"]:
                print("  No lane or free swim this week.")
            else:
                for s in classified["week"]:
                    print(f"  {s['day']} {s['start']}-{s['end']} {s['activity']}")

            print("\n")

        except Exception as e:
            print(f"Failed for {pool}: {e}\n")


if __name__ == "__main__":
    main()
