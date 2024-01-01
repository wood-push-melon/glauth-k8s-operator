# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

from functools import wraps
from typing import Any, Callable, Optional

from constants import GLAUTH_CONFIG_FILE
from ops.charm import CharmBase
from tenacity import Retrying, TryAgain, wait_fixed


def after_config_updated(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(charm: CharmBase, *args: Any, **kwargs: Any) -> Optional[Any]:
        for attempt in Retrying(
            wait=wait_fixed(3),
        ):
            with attempt:
                expected_config = charm.config_file.content
                current_config = charm._container.pull(GLAUTH_CONFIG_FILE).read()
                if expected_config != current_config:
                    raise TryAgain

        return func(charm, *args, **kwargs)

    return wrapper
