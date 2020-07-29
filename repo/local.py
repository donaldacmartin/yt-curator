from csv import DictReader, DictWriter
from os.path import exists


FILENAME = "./subscriptions.csv"


def load_subscriptions():
    if exists(FILENAME):
        with open(FILENAME, "r") as csv_file:
            reader = DictReader(csv_file)
            return [subscription for subscription in reader]
    else:
        return None


def save_subscriptions(subscriptions):
    with open(FILENAME, "w") as csv_file:
        field_names = subscriptions[0].keys()
        csv_writer = DictWriter(csv_file, fieldnames=field_names)
        csv_writer.writeheader()
        [csv_writer.writerow(subscription) for subscription in subscriptions]
