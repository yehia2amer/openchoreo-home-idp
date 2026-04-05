#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer>=0.9",
#     "rich>=13",
#     "pyyaml>=6",
# ]
# ///
"""Talos cluster resource dumper.

Connects to a Talos node via talosctl, enumerates every resource definition,
fetches each resource, runs extra diagnostic commands, and writes everything
to timestamped output files.

Usage:
    uv run talos_get_all_details.py [OPTIONS]
"""

from __future__ import annotations

import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

# ── constants ───────────────────────────────────────────────────────────────
DEFAULT_TALOSCONFIG = str(
    Path(__file__).resolve().parent
    / "pulumi"
    / "talos-cluster-baremetal"
    / "outputs"
    / "talosconfig"
)

EXTRA_COMMANDS: list[str] = [
    "version",
    "health",
    "time",
    "services",
    "containers",
    "memory",
    "usage /var/lib",
    "mounts",
    "image list",
    "stats",
    "list /",
    "read /etc/os-release",
    "read /etc/resolv.conf",
    "read /proc/cmdline",
    "read /proc/modules",
    "read /etc/modprobe.d/cx23885.conf",
    "ls /var/mnt/AmerData",
]

console = Console()
app = typer.Typer(
    help="Dump all Talos cluster resource details to timestamped files.",
    rich_markup_mode="rich",
)

# ── file-write lock (for parallel appends) ──────────────────────────────────
_file_lock = threading.Lock()


# ── result tracking ─────────────────────────────────────────────────────────
@dataclass
class CmdResult:
    label: str
    status: str  # "ok", "skipped", "error"
    reason: str = ""
    duration: float = 0.0


@dataclass
class Stats:
    ok: int = 0
    skipped: int = 0
    errors: int = 0
    results: list[CmdResult] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record(self, r: CmdResult) -> None:
        with self._lock:
            self.results.append(r)
            if r.status == "ok":
                self.ok += 1
            elif r.status == "skipped":
                self.skipped += 1
            else:
                self.errors += 1


# ── helpers ─────────────────────────────────────────────────────────────────
def read_node_from_talosconfig(path: Path) -> str | None:
    """Extract the first node IP from a talosconfig YAML file."""
    try:
        cfg = yaml.safe_load(path.read_text())
        context_name = cfg.get("context", "")
        contexts = cfg.get("contexts", {})
        ctx = contexts.get(context_name, {})
        nodes = ctx.get("nodes", [])
        if nodes:
            return str(nodes[0])
        endpoints = ctx.get("endpoints", [])
        if endpoints:
            return str(endpoints[0])
    except Exception:
        pass
    return None


def run_talosctl(
    node_ip: str,
    talosconfig: str,
    subcommand: list[str],
) -> subprocess.CompletedProcess[str]:
    cmd = [
        "talosctl",
        "-n", node_ip,
        "-e", node_ip,
        "--talosconfig", talosconfig,
        *subcommand,
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


def _human_size(path: Path) -> str:
    """Return a human-readable file size string."""
    size = path.stat().st_size if path.exists() else 0
    for unit, threshold in [("MB", 1024 ** 2), ("KB", 1024)]:
        if size >= threshold:
            return f"{size / threshold:.1f} {unit}"
    return f"{size} B"


def parse_resource_ids(output: str) -> list[str]:
    """Parse the columnar talosctl output and return the ID column values."""
    lines = [l for l in output.splitlines() if l.strip()]
    if not lines:
        return []
    header = lines[0].split()
    id_col = header.index("ID") if "ID" in header else 3
    resources: list[str] = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) > id_col:
            resources.append(parts[id_col])
    return resources


def process_command(
    node_ip: str,
    talosconfig: str,
    subcmd: list[str],
    output_file: Path,
    label: str,
    stats: Stats,
) -> CmdResult:
    """Run a single talosctl command, append output to file, return result."""
    cmd_str = " ".join(
        ["talosctl", "-n", node_ip, "-e", node_ip, "--talosconfig", talosconfig, *subcmd]
    )

    start = time.monotonic()
    result = run_talosctl(node_ip, talosconfig, subcmd)
    duration = time.monotonic() - start

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        r = CmdResult(label, "error", stderr[:120], duration)
        stats.record(r)
        return r

    output = result.stdout or ""

    if "rpc error: code = PermissionDenied desc = not authorized" in output:
        r = CmdResult(label, "skipped", "not authorized", duration)
        stats.record(r)
        return r

    non_empty_lines = [line for line in output.splitlines() if line.strip()]
    if len(non_empty_lines) <= 1:
        r = CmdResult(label, "skipped", "empty or trivial output", duration)
        stats.record(r)
        return r

    section = (
        "\n"
        "------------------------------\n"
        f"Command:   {cmd_str}\n"
        f"Label:     {label}\n"
        f"Duration:  {duration:.3f} seconds\n"
        "------------------------------\n"
        f"{output}\n"
    )
    with _file_lock:
        with open(output_file, "a") as fh:
            fh.write(section)

    r = CmdResult(label, "ok", "", duration)
    stats.record(r)
    return r


def make_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )


def print_summary(stats: Stats, phase: str) -> None:
    table = Table(title=f"{phase} Summary", show_lines=False)
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")
    table.add_row("[green]Collected[/green]", str(stats.ok))
    table.add_row("[yellow]Skipped[/yellow]", str(stats.skipped))
    table.add_row("[red]Errors[/red]", str(stats.errors))
    console.print(table)

    # Show error details if any
    error_results = [r for r in stats.results if r.status == "error"]
    if error_results:
        console.print(f"\n[red bold]Errors ({len(error_results)}):[/red bold]")
        for r in error_results[:10]:
            console.print(f"  [red]✗[/red] {r.label}: {r.reason}")
        if len(error_results) > 10:
            console.print(f"  … and {len(error_results) - 10} more")


# ── main CLI ────────────────────────────────────────────────────────────────
@app.command()
def main(
    node: Annotated[
        Optional[str],
        typer.Option(help="Talos node IP. Auto-detected from talosconfig if omitted."),
    ] = None,
    talosconfig: Annotated[
        str,
        typer.Option(help="Path to talosconfig file."),
    ] = DEFAULT_TALOSCONFIG,
    workers: Annotated[
        int,
        typer.Option(help="Parallel workers for resource fetching."),
    ] = 10,
    output_dir: Annotated[
        str,
        typer.Option(help="Directory to write output files."),
    ] = ".",
) -> None:
    """Dump all Talos cluster resources, dmesg, and diagnostics to files."""

    talosconfig_path = Path(talosconfig)
    if not talosconfig_path.exists():
        console.print(f"[red bold]Error:[/red bold] talosconfig not found at {talosconfig}")
        raise typer.Exit(code=1)

    # ── resolve node IP ─────────────────────────────────────────────────────
    if node is None:
        node = read_node_from_talosconfig(talosconfig_path)
        if node is None:
            console.print("[red bold]Error:[/red bold] could not detect node IP from talosconfig. Pass --node explicitly.")
            raise typer.Exit(code=1)
        console.print(f"[dim]Auto-detected node:[/dim] [bold]{node}[/bold]")

    node_ip: str = node

    # ── output paths ────────────────────────────────────────────────────────
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_file = out / f"k8s_talos_resources_{ts}.txt"
    dmesg_file = out / f"k8s_talos_dmesg_{ts}.txt"
    misc_file = out / f"k8s_talos_misc_{ts}.txt"

    output_file.write_text("")
    misc_file.write_text("")

    console.print(
        Panel(
            f"[bold]Node:[/bold]        {node_ip}\n"
            f"[bold]Talosconfig:[/bold] {talosconfig}\n"
            f"[bold]Workers:[/bold]     {workers}",
            title="[bold blue]Talos Cluster Dump[/bold blue]",
            border_style="blue",
        )
    )

    # ── 1. dmesg ────────────────────────────────────────────────────────────
    with make_progress() as progress:
        task = progress.add_task("dmesg", total=1)
        start = time.monotonic()
        result = run_talosctl(node_ip, talosconfig, ["dmesg"])
        duration = time.monotonic() - start
        if result.returncode == 0:
            dmesg_file.write_text(result.stdout or "")
            progress.update(task, advance=1)
            console.print(f"  [green]✓[/green] dmesg [dim]({duration:.3f}s)[/dim]")
        else:
            progress.update(task, advance=1)
            console.print(f"  [red]✗[/red] dmesg failed: {(result.stderr or '').strip()[:120]}")
            dmesg_file.write_text("")

    # ── 2. resource definitions ─────────────────────────────────────────────
    console.print("\n[bold blue]Fetching resource definitions …[/bold blue]")
    rd_result = run_talosctl(node_ip, talosconfig, ["get", "resourcedefinitions.meta.cosi.dev"])
    if rd_result.returncode != 0:
        console.print(f"[red bold]Error:[/red bold] could not list resource definitions.\n{(rd_result.stderr or '').strip()}")
        raise typer.Exit(code=1)

    resources = parse_resource_ids(rd_result.stdout or "")
    console.print(f"  Found [bold]{len(resources)}[/bold] resource definitions\n")

    # ── 3. fetch resources in parallel ──────────────────────────────────────
    res_stats = Stats()
    with make_progress() as progress:
        task = progress.add_task("Resources", total=len(resources))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(
                    process_command,
                    node_ip, talosconfig, ["get", res], output_file, res, res_stats,
                ): res
                for res in resources
            }
            for future in as_completed(futures):
                future.result()  # propagate exceptions
                progress.update(task, advance=1)

    print_summary(res_stats, "Resources")

    # ── 4. extra commands (sequential — some are slow / order-dependent) ────
    console.print(f"\n[bold blue]Running {len(EXTRA_COMMANDS)} extra commands …[/bold blue]")
    misc_stats = Stats()
    with make_progress() as progress:
        task = progress.add_task("Extra commands", total=len(EXTRA_COMMANDS))
        for subcmd_str in EXTRA_COMMANDS:
            subcmd_parts = subcmd_str.split()
            process_command(node_ip, talosconfig, subcmd_parts, misc_file, subcmd_str, misc_stats)
            progress.update(task, advance=1)

    print_summary(misc_stats, "Extra Commands")

    # ── final report ────────────────────────────────────────────────────────
    files_table = Table(title="\nOutput Files", show_lines=False)
    files_table.add_column("File", style="bold green")
    files_table.add_column("Size", justify="right")
    for f in [output_file, dmesg_file, misc_file]:
        files_table.add_row(str(f), _human_size(f))
    console.print(files_table)
    console.print("[bold green]Done![/bold green]")


if __name__ == "__main__":
    app()
