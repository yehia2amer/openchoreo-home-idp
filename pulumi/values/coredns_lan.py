"""CoreDNS Corefile and deployment values for LAN DNS."""

from __future__ import annotations


def get_corefile(
    cp_ip: str,
    dp_ip: str,
    op_ip: str,
    bind_ip: str = "",
) -> str:
    """Return a CoreDNS Corefile for *.openchoreo.local resolution.

    Maps specific hostnames to their respective gateway IPs:
    - Control plane (cp_ip): openchoreo.local, api.*, thunder.*
    - Data plane (dp_ip): everything else (wildcard catch-all)
    - Observability (op_ip): observer.*, rca-agent.*

    Args:
        cp_ip: Control plane gateway IP.
        dp_ip: Data plane gateway IP (also used as wildcard default).
        op_ip: Observability plane gateway IP.
        bind_ip: If set, bind only to this IP instead of 0.0.0.0.
    """
    bind_directive = f"\n    bind {bind_ip}" if bind_ip else ""
    return f"""\
.:53 {{{bind_directive}
    template IN A openchoreo.local {{
        match ^(openchoreo\\.local|api\\.openchoreo\\.local|thunder\\.openchoreo\\.local)[.]?$
        answer "{{{{ .Name }}}} 60 IN A {cp_ip}"
        fallthrough
    }}
    template IN A openchoreo.local {{
        match ^(observer\\.openchoreo\\.local|rca-agent\\.openchoreo\\.local)[.]?$
        answer "{{{{ .Name }}}} 60 IN A {op_ip}"
        fallthrough
    }}
    template IN A openchoreo.local {{
        match .*\\.openchoreo\\.local
        answer "{{{{ .Name }}}} 60 IN A {dp_ip}"
        fallthrough
    }}
    template IN AAAA openchoreo.local {{
        match .*\\.openchoreo\\.local
        answer "{{{{ .Name }}}} 60 IN AAAA ::1"
        rcode NOERROR
    }}
    forward . 8.8.8.8 1.1.1.1
    cache 30
    errors
    log
    ready :8080
    health :8081
}}
"""
