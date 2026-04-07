"""CoreDNS Corefile and deployment values for LAN DNS."""

from __future__ import annotations


def get_corefile(
    cp_ip: str,
    dp_ip: str,
    op_ip: str,
    domain: str = "amernas.work",
    kube_dns_ip: str = "10.96.0.10",
    bind_ip: str = "",
) -> str:
    """Return a CoreDNS Corefile for *.<domain> resolution on the LAN.

    With the shared gateway consolidation, all hostnames resolve to the
    same shared gateway IP (cp_ip == dp_ip == op_ip typically).  The
    three-IP signature is kept for backward compatibility.

    Also forwards .cluster.local queries to kube-dns so that
    containerd on the node can resolve in-cluster service names.

    Args:
        cp_ip: Control plane / shared gateway IP.
        dp_ip: Data plane gateway IP (wildcard catch-all).
        op_ip: Observability plane gateway IP.
        domain: Base domain (e.g. ``amernas.work``).
        kube_dns_ip: ClusterIP of the kube-dns service.
        bind_ip: If set, bind only to this IP instead of 0.0.0.0.
    """
    bind_directive = f"\n    bind {bind_ip}" if bind_ip else ""
    # Escape dots for regex
    domain_re = domain.replace(".", r"\.")

    # Hostnames routed to control-plane gateway
    cp_hosts = "|".join(
        [
            rf"backstage\.{domain_re}",
            rf"portal\.{domain_re}",
            rf"api\.{domain_re}",
            rf"thunder\.{domain_re}",
            rf"hubble\.{domain_re}",
            rf"longhorn\.{domain_re}",
            rf"argo\.{domain_re}",
            rf"openbao\.{domain_re}",
            rf"registry\.{domain_re}",
        ]
    )
    # Hostnames routed to observability gateway
    op_hosts = "|".join(
        [
            rf"observer\.{domain_re}",
            rf"rca-agent\.{domain_re}",
            rf"prometheus\.{domain_re}",
            rf"opensearch\.{domain_re}",
            rf"alertmanager\.{domain_re}",
            rf"openobserve\.{domain_re}",
        ]
    )
    return f"""\
cluster.local:53 {{{bind_directive}
    forward . {kube_dns_ip}
    cache 5
    errors
}}

.:53 {{{bind_directive}
    template IN A {domain} {{
        match ^({cp_hosts})[.]?$
        answer "{{{{ .Name }}}} 60 IN A {cp_ip}"
        fallthrough
    }}
    template IN A {domain} {{
        match ^({op_hosts})[.]?$
        answer "{{{{ .Name }}}} 60 IN A {op_ip}"
        fallthrough
    }}
    template IN A {domain} {{
        match .*\\.{domain_re}
        answer "{{{{ .Name }}}} 60 IN A {dp_ip}"
        fallthrough
    }}
    template IN AAAA {domain} {{
        match .*\\.{domain_re}
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
