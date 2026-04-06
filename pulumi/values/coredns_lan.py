"""CoreDNS Corefile and deployment values for LAN DNS."""

from __future__ import annotations


def get_corefile(
    cp_ip: str,
    dp_ip: str,
    op_ip: str,
    kube_dns_ip: str = "10.96.0.10",
    bind_ip: str = "",
) -> str:
    """Return a CoreDNS Corefile for *.openchoreo.local resolution.

    Maps specific hostnames to their respective gateway IPs:
    - Control plane (cp_ip): openchoreo.local, api.*, thunder.*, hubble.*,
      longhorn.*, argo.*, openbao.*
    - Observability (op_ip): observer.*, rca-agent.*, prometheus.*,
      opensearch.*, alertmanager.*
    - Data plane (dp_ip): everything else (wildcard catch-all)

    Also forwards .cluster.local queries to kube-dns so that
    containerd on the node can resolve in-cluster service names.

    Args:
        cp_ip: Control plane gateway IP.
        dp_ip: Data plane gateway IP (also used as wildcard default).
        op_ip: Observability plane gateway IP.
        kube_dns_ip: ClusterIP of the kube-dns service.
        bind_ip: If set, bind only to this IP instead of 0.0.0.0.
    """
    bind_directive = f"\n    bind {bind_ip}" if bind_ip else ""
    # Hostnames routed to each gateway — regex alternation
    cp_hosts = "|".join(
        [
            r"openchoreo\.local",
            r"api\.openchoreo\.local",
            r"thunder\.openchoreo\.local",
            r"hubble\.openchoreo\.local",
            r"longhorn\.openchoreo\.local",
            r"argo\.openchoreo\.local",
            r"openbao\.openchoreo\.local",
            r"portal\.openchoreo\.local",
        ]
    )
    op_hosts = "|".join(
        [
            r"observer\.openchoreo\.local",
            r"rca-agent\.openchoreo\.local",
            r"prometheus\.openchoreo\.local",
            r"opensearch\.openchoreo\.local",
            r"alertmanager\.openchoreo\.local",
        ]
    )
    return f"""\
cluster.local:53 {{{bind_directive}
    forward . {kube_dns_ip}
    cache 5
    errors
}}

.:53 {{{bind_directive}
    template IN A openchoreo.local {{
        match ^({cp_hosts})[.]?$
        answer "{{{{ .Name }}}} 60 IN A {cp_ip}"
        fallthrough
    }}
    template IN A openchoreo.local {{
        match ^({op_hosts})[.]?$
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
