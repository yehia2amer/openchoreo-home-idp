"""OpenBao Helm values builder."""

from __future__ import annotations

from pathlib import Path
from string import Template
from typing import Any


def get_values(
    openbao_root_token: str,
) -> dict[str, Any]:
    """Return Helm values for the OpenBao chart (dev mode with postStart seed)."""
    return {
        "injector": {"enabled": False},
        "server": {
            "dev": {
                "enabled": True,
                "devRootToken": openbao_root_token,
            },
            "postStart": [
                "/bin/sh",
                "-c",
                _post_start_script(openbao_root_token),
            ],
        },
    }


def _post_start_script(token: str) -> str:
    template_path = Path(__file__).resolve().parent.parent / "templates" / "openbao_post_start.sh.tpl"
    tpl = Template(template_path.read_text())
    return tpl.substitute(token=token)
