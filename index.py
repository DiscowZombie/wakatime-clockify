#!/bin/python3

import requests
import sys
from datetime import datetime

class Wakatime:

    API_BASE_URL: str = "https://wakatime.com/api/v1"

    auth_headers  = None

    def __init__(self, api_key: str):
        self.auth_headers = {"Authorization": "Basic {}".format(api_key)}

    def get_day_durations(self, day: str):
        p = {"date": day} # 2022-09-08
        r = requests.get("{}/users/current/durations".format(self.API_BASE_URL), params=p, headers=self.auth_headers)
        return r.json()


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
        return r.status_code == 201


if __name__ == "__main__":
    argc = len(sys.argv)

    if argc <= 3:
        print("./index.py <wakatime_api_token> <clockify_api_token> <clockify_workspace>")
        exit(1)

    wakatime_api_token = sys.argv[1]
    clockify_api_token = sys.argv[2]
    clockify_workspace = sys.argv[3]

    # Construct the Wakatime instance
    wtime = Wakatime(wakatime_api_token)
    print(wtime.get_day_durations("2022-09-08"))

    # Construct the Clockify instance
    clockify = Clockify(clockify_api_token)
    print(clockify.add_time_entry(clockify_workspace, "631a01e0dda163175686e26c", 1662660000, "Test API", billable = False))
