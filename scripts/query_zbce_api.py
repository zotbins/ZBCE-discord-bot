"""
Description:
A couple of helper functions to query the ZBCE API
"""

import requests
import pendulum


class QueryZBCEAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_available_bins(self):
        try:
            r = requests.get(url=self.base_url + f"/bin-info-all?key={self.api_key}")
            bin_id_lst = [entry["id"] for entry in r.json()["data"]]

            return bin_id_lst
        except Exception as e:
            print(e)
            return None

    def get_fullness_today(self, bin_id, timezone="America/Los_Angeles"):

        # get today's date in PST and convert it to UTC time. The database
        # for the zbce_api converts it to
        starttime = pendulum.today().set(tz=timezone).in_timezone("UTC")
        endtime = pendulum.tomorrow().set(tz=timezone).in_timezone("UTC")

        # create the get request
        params = {
            "start_timestamp": starttime.to_datetime_string(),
            "end_timestamp": endtime.to_datetime_string(),
            "bin_id": bin_id,
        }

        try:
            r = requests.get(
                self.base_url + f"/fullness?key={self.api_key}",
                params=params,
                headers=self.headers,
            ).json()

            return r

        except Exception as e:
            print(e)
            return None
