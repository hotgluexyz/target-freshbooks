"""Freshbooks target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import Target
from target_hotglue.target import TargetHotglue
from typing import Callable, Dict, List, Optional, Tuple, Type, Union
from pathlib import Path, PurePath

from target_freshbooks.sinks import (
    FreshbooksSink,
    InvoicesSink,
    CustomersSink
)


class TargetFreshbooks(TargetHotglue):
    """Sample target for Freshbooks."""

    def __init__(
        self,
        config: Optional[Union[dict, PurePath, str, List[Union[PurePath, str]]]] = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
        state: str = None
    ) -> None:
        self.config_file = config[0]
        super().__init__(config, parse_env_config, validate_config)


    name = "target-freshbooks"

    SINK_TYPES = [ CustomersSink, InvoicesSink]
    MAX_PARALLELISM = 1

    config_jsonschema = th.PropertiesList(
            th.Property("client_id", th.StringType, required=True),
            th.Property("client_secret", th.StringType, required=True),
            th.Property("refresh_token", th.StringType, required = True),
            th.Property("access_token", th.StringType,  required = True),
            th.Property("expires_in", th.NumberType),
            th.Property('account_id', th.StringType),
        ).to_dict()

    def get_sink_class(self, stream_name: str):
        return next(
            (
                sink_class
                for sink_class in self.SINK_TYPES
                if sink_class.unified_schema.schema_name.lower() == stream_name.lower()
            ),
            None,
        )



if __name__ == "__main__":
    TargetFreshbooks.cli()
