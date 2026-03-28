"""Helper: sleep/wait utilities for Pulumi."""

import pulumi
import pulumi_command as command


def sleep(
    name: str,
    seconds: int,
    opts: pulumi.ResourceOptions | None = None,
) -> command.local.Command:
    """Create a sleep command (replacement for time_sleep)."""
    return command.local.Command(
        f"wait-{name}",
        create=f"sleep {seconds}",
        opts=opts,
    )
