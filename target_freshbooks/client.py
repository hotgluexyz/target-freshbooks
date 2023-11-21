"""Freshbooks target sink class, which handles writing streams."""

from __future__ import annotations

import backoff
import requests
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError

from singer_sdk.sinks import RecordSink
from singer_sdk.helpers.jsonpath import extract_jsonpath
import json

from target_hotglue.client import HotglueSink


from target_freshbooks.auth import FreshbooksAuthenticator


class FreshbooksSink(HotglueSink):
    """Freshbooks target sink class."""

    auth_state = {}

    @property
    def base_url(self) -> str:

        return f"https://api.freshbooks.com/accounting/account/{self.account_id}"

    @property
    def account_id(self):
        url = "https://api.freshbooks.com/auth/api/v1/users/me"
        return json.loads(requests.request(method = "GET", url=url, headers=self.authenticator.auth_headers).text).get("response").get("business_memberships")[0].get("business").get("account_id")
        


    @property
    def authenticator(self):
        return FreshbooksAuthenticator(
            self._target, self.auth_state
        )

    # @backoff.on_exception(
    #     backoff.expo,
    #     (RetriableAPIError, requests.exceptions.ReadTimeout),
    #     max_tries=5,
    #     factor=2,
    # )
    # def _request(
    #     self, http_method, endpoint, params=None, request_data=None, headers=None
    # ) -> requests.PreparedRequest:
    #     """Prepare a request object."""
    #     url = f"https://api.freshbooks.com/accounting/account/{self.account_id}"
    #     headers = self.http_headers

    #     response = requests.request(
    #         method=http_method,
    #         url=url,
    #         params=params,
    #         headers=headers,
    #         json=request_data,
    #         auth=self.authenticator.get_auth_session(),
    #     )
    #     self.validate_response(response)
    #     return response