#!/bin/python3

import requests
import sys
import pytz
from datetime import datetime

HTTP_CODE_OK: int = 200
HTTP_CODE_CREATED: int = 201

class Wakatime:

    API_BASE_URL: str = "https://wakatime.com/api/v1"

    auth_headers  = None

    def __init__(self, api_key: str):
        self.auth_headers = {"Authorization": "Basic {}".format(api_key)}

    def get_day_durations(self, day: str):
        p = {"date": day}  # YYYY-MM-DD
        r = requests.get("{}/users/current/durations".format(self.API_BASE_URL), params=p, headers=self.auth_headers)
        return (r.status_code, r.json())


class Clockify:

    API_BASE_URL: str = "https://api.clockify.me/api/v1"

    auth_headers = None

    def __init__(self, api_key: str):
        self.auth_headers = {"X-Api-Key": api_key}

    def get_all_workspaces(self):
        r = requests.get("{}/workspaces".format(self.API_BASE_URL), headers=self.auth_headers)
        return r.json()

    def add_time_entry(self, workspaceId: int, projectId: str, start: int, description: str, taskId: str = None, billable: bool = True, end: int = None, tagIds = []) -> bool:
        b = {
            "start": datetime.fromtimestamp(start).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "billable": str(billable),
            "description": description,
            "projectId": projectId,
            "end": datetime.fromtimestamp(end).strftime("%Y-%m-%dT%H:%M:%SZ") if end is not None else None, # Optionnal field
            "taskId": taskId if taskId is not None else None, # Optionnal field
            "tagIds": tagIds
        }
        r = requests.post(
            "{}/workspaces/{}/time-entries".format(self.API_BASE_URL, str(workspaceId)), 
            params={"Content-Type": "application/json"}, 
            json=b,
            headers=self.auth_headers)
        return (r.status_code, r.json())


if __name__ == "__main__":
    argc = len(sys.argv)

    if argc <= 4:
        print("./index.py <wakatime_api_token> <clockify_api_token> <clockify_workspace> <clockify_project>")
        exit(1)

    wakatime_api_token = sys.argv[1]
    clockify_api_token = sys.argv[2]
    clockify_workspace = sys.argv[3]
    clockify_project = sys.argv[4]

    date_str = str(input("Please write the date of the day you want to export (YEAR-MONTH-DAY), eg. 2022-08-28 (Sun 28 Aug 2022)\n"))

    # Construct the Wakatime instance
    wtime = Wakatime(wakatime_api_token)
    
    # Construct the Clockify instance
    clockify = Clockify(clockify_api_token)

    # Retrieve durations from Wakatime
    status_code, j = wtime.get_day_durations(date_str)

    if status_code != HTTP_CODE_OK:
        print("Unable to retrieve durations from Wakatime: {}".format(j))
        exit(1)

    exported_project_count: int = 0
    tz = j["timezone"] # Wakatime return timestamps into this zone but Clockify want UTC+0 timezones
    tz_offset = int(datetime.now(pytz.timezone(tz)).utcoffset().total_seconds()) # Offset between Wakatime timezone and UTC+0

    for p in j["data"]:
        # For some reason, Wakatime return floating point numbers for time and duration
        start_ts = int(p["time"]) - tz_offset
        end_ts = start_ts + int(p["duration"])
        
        status_code, j = clockify.add_time_entry(clockify_workspace, clockify_project, start_ts, p["project"], end = end_ts, billable = False)

        if status_code == HTTP_CODE_CREATED:
            exported_project_count = exported_project_count + 1
        else:
            print("Unable to export project {} to Clockify: {}".format(p["project"], j))

    print("Successfully exported {} project(s)".format(exported_project_count))
