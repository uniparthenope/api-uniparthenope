from app.apis.access.models import UserAccess
import csv
import re

users = UserAccess.query.all()

with open('access.csv', "w", newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for row in users:
        row.username = re.sub(',', '', row.username)
        row.username = re.sub('|', '', row.username)
        row.username = re.sub(' ', '', row.username)

        writer.writerow([row.username, row.classroom])
