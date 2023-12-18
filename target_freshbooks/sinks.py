"""Freshbooks target sink class, which handles writing streams."""

from __future__ import annotations
from typing import Optional
from singer_sdk import typing as th
import json
from datetime import datetime
import dateutil.parser
import hotglue_models_accounting.accounting as accounting

from target_freshbooks.client import FreshbooksSink

def parse_line_items(record_line_items):
    line_items = []

    for item in record_line_items:
        payload_item = {}
        payload_item["description"] = item.get("description")
        payload_item["name"] = item.get("productName")
        payload_item["amount"] = {
            "amount" : str(item.get("totalPrice"))
            }
        payload_item["unit_cost"] = {
            "amount" : str(item.get("unitPrice"))
            }
        payload_item["qty"] = item.get("quantity")
        line_items.append(payload_item)

    return line_items


class InvoicesSink(FreshbooksSink):
    """Freshbooks target sink class."""

    
    endpoint = "/invoices/invoices"
    unified_schema = accounting.Invoice # Place a unified schema class here
    name = "Invoices"


    def preprocess_record(self, record: dict, context: dict) -> dict:
        payload = {}
        entity = {}

        # if record.get("id"):
        #     entity["entity_id"] = record.pop("id")
        # commented this out for now just in case we dont need it

        #Gotta get customerid before posting a record
        cust_res = json.loads((self.request_api(http_method = "GET", endpoint = f"/users/clients?search[email]={record.get('billEmail')}", headers=self.authenticator.auth_headers)).text)
        cust_res = cust_res.get("response").get("result").get("clients")[0].get("id") if len(cust_res.get("response").get("result").get("clients")) > 0 else None
        
        if cust_res is None:
            raise ValueError(f"Cannot find customer with the email: {record.get('billEmail')}. Please check the provided email and try again.")

        first_name, *last_name = record.pop("customerName", "").split(" ")
        last_name = " ".join(last_name)
        address = record.pop("address")[0]


        entity["fname"] = first_name
        entity["lname"] = last_name
        entity["city"] = address.get("city")
        entity["country"] = address.get("country")
        entity["street"] = address.get("line1")
        entity["street2"] = address.get("line2") if address.get("line2") is not None else ""
        entity["province"] = address.get("state")
        entity["invoice_number"] = record.get("invoiceNumber")
        entity["discount_value"] = record.get("totalDiscount")
        entity["create_date"] = dateutil.parser.parse(record.get("createdAt")).strftime('%Y-%m-%d')
        entity["currency_code"] = record.get("currency")
        entity["payment_details"] = record.get("paymentMethod")
        entity["terms"] = record.get("salesTerm")
        entity["customerid"] = cust_res
        entity["lines"] = parse_line_items(record.get("lineItems"))
        


        payload["invoice"] = entity

        return payload



    

    def upsert_record(self, record: dict, context: dict) -> None:
        """Process the record.

        Args:
            record: Individual record in the stream.
            context: Stream partition or context dictionary.
        """
        method = "POST"
        header = self.authenticator.auth_headers

        #check if invoice exists to avoid failure:
        invoice = self.request_api(http_method="GET", endpoint= f"{self.endpoint}/{record['invoice']['invoice_number']}", headers=header)
        if json.loads(invoice.text):
            method = "PUT"
        
        res = self.request_api(http_method = method, endpoint = self.endpoint, request_data = record, headers=header)

class CustomersSink(FreshbooksSink):


    endpoint = "/users/clients"
    unified_schema = accounting.Customer # Place a unified schema class here
    name = "Customers"

    def preprocess_record(self, record: dict, context: dict) -> dict:
        payload = {}
        entity = {}

        first_name, *last_name = record.pop("customerName", "").split(" ")
        last_name = " ".join(last_name)
        address = record.get("address")[0]


        entity["fname"] = first_name
        entity["lname"] = last_name
        entity["p_city"] = address.get("city")
        entity["country"] = address.get("country")
        entity["p_country"] = address.get("line1")
        entity["p_street2"] = address.get("line2")
        entity["p_province"] = address.get("state")
        entity["currency_code"] = record.get("currency")
        entity["email"] = record.get("emailAddress")
        
        payload["client"] = entity

        return payload

    def upsert_record(self, record: dict, context: dict) -> None:
        """Process the record.
    
        Args:
            record: Individual record in the stream.
            context: Stream partition or context dictionary.
        """
        method = "POST"

        #check if client exists already
        client = json.loads((self.request_api(http_method = "GET", endpoint = f"/users/clients?search[email]={record['client']['email']}", headers=self.authenticator.auth_headers)).text)
        cust_res = client.get("response").get("result").get("clients")[0].get("id") if len(cust_res.get("response").get("result").get("clients")) > 0 else None

        if cust_res: # update client with the new info if there is a duplicate or should we skip?
            method = "PUT"

        self.logger.info(record)
        
        res = self.request_api(http_method = method, endpoint = self.endpoint, request_data = record, headers=self.authenticator.auth_headers)
