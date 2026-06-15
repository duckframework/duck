"""
SystemMetricsPanel component — renders live OS-level system metrics.

Displays CPU, memory, concurrency, open files, network I/O, and storage
as individual metric cards inside a single panel. Each card handles its
own unavailability gracefully — if a metric fails to collect, the card
shows a clear error placeholder instead of breaking the panel.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container

from ..components.theme import Theme


class SystemMetricsPanel(InnerComponent):
    """
    Renders a grid of system-level metric cards.

    Each card corresponds to one OS metric (CPU, memory, etc.) and
    renders either a live value with a visual gauge, or an error
    placeholder if the metric was unavailable at collection time.

    Props:
        data (dict): Output of system_metrics.get_system_metrics().
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the panel header and system metrics grid.
        """
        super().on_create()

        data = self.kwargs.get("data", {})
        self.props["class"] = "db-panel"

        self.add_children([
            self.build_header(),
            self.build_body(data),
        ])

    # ── Header ────────────────────────────────────────────────────────

    def build_header(self) -> Container:
        """
        Returns the panel header with title and OS badge.

        Returns:
            A Container with the header markup.
        """
        import platform
        os_name = platform.system() or "System"
        return Container(
            klass="db-panel-header",
            inner_html=(
                '<span class="db-panel-title">System Metrics</span>'
                f'<span class="db-sys-os-badge">{os_name}</span>'
            ),
        )

    # ── Body ──────────────────────────────────────────────────────────

    def build_body(self, data: dict) -> Container:
        """
        Returns the metrics grid containing all six metric cards.

        Args:
            data: The system metrics snapshot dict.

        Returns:
            A Container wrapping the six metric cards in a grid.
        """
        cpu = data.get("cpu", {})
        memory = data.get("memory", {})
        concurrency = data.get("concurrency", {})
        open_files = data.get("open_files", {})
        network = data.get("network", {})
        storage = data.get("storage", {})

        cards_html = "".join([
            self._build_cpu_card(cpu),
            self._build_memory_card(memory),
            self._build_concurrency_card(concurrency),
            self._build_open_files_card(open_files),
            self._build_network_card(network),
            self._build_storage_card(storage),
        ])

        return Container(
            klass="db-panel-body",
            inner_html=f'<div class="db-sys-grid">{cards_html}</div>',
        )

    # ── Card builders ─────────────────────────────────────────────────

    def _build_cpu_card(self, d: dict) -> str:
        """
        Returns HTML for the CPU utilisation card.

        Args:
            d: CPU metrics dict from system_metrics.get_cpu_metrics().

        Returns:
            HTML string for the CPU metric card.
        """
        if not d.get("available"):
            return self._error_card("CPU Usage", d.get("error", "Unavailable"))

        pct = d.get("percent", 0)
        cores = d.get("cores_logical", "—")
        freq = f"{d.get('freq_mhz', '—')} MHz" if d.get("freq_mhz") else "—"
        color = self._gauge_color(pct)

        details = [
            ("Logical Cores", str(cores)),
            ("Frequency", freq),
        ]
        return self._gauge_card("CPU Usage", pct, "%", color, details)

    def _build_memory_card(self, d: dict) -> str:
        """
        Returns HTML for the memory usage card.

        Args:
            d: Memory metrics dict from system_metrics.get_memory_metrics().

        Returns:
            HTML string for the memory metric card.
        """
        if not d.get("available"):
            return self._error_card("Memory", d.get("error", "Unavailable"))

        pct = d.get("percent", 0)
        used = d.get("used_mb", 0)
        total = d.get("total_mb", 0)
        color = self._gauge_color(pct)

        details = [
            ("Used", f"{used:,} MB"),
            ("Total", f"{total:,} MB"),
        ]
        return self._gauge_card("Memory", pct, "%", color, details)

    def _build_concurrency_card(self, d: dict) -> str:
        """
        Returns HTML for the concurrency (active threads) card.

        Args:
            d: Concurrency metrics dict.

        Returns:
            HTML string for the concurrency metric card.
        """
        if not d.get("available"):
            return self._error_card("Concurrency", d.get("error", "Unavailable"))

        threads = d.get("thread_count", 0)
        pid = d.get("process_id", "—")
        proc_name = d.get("process_name") or "—"

        return self._value_card(
            title="Concurrency",
            value=str(threads),
            unit="threads",
            color=Theme.teal,
            details=[
                ("Process ID", str(pid)),
                ("Process", proc_name),
            ],
        )

    def _build_open_files_card(self, d: dict) -> str:
        """
        Returns HTML for the open file descriptors card.

        Args:
            d: Open files metrics dict.

        Returns:
            HTML string for the open files metric card.
        """
        if not d.get("available"):
            return self._error_card("Open Files", d.get("error", "Unavailable"))

        count = d.get("open_files", 0)
        soft = d.get("soft_limit")
        hard = d.get("hard_limit")

        # Show gauge relative to soft limit if available
        pct = round((count / soft) * 100, 1) if soft and soft > 0 else None

        if pct is not None:
            color = self._gauge_color(pct)
            details = [
                ("Soft Limit", str(soft) if soft else "—"),
                ("Hard Limit", str(hard) if hard else "—"),
            ]
            return self._gauge_card("Open Files", pct, f"% ({count} fds)", color, details)

        return self._value_card(
            title="Open Files",
            value=str(count),
            unit="fds",
            color=Theme.purple,
            details=[
                ("Soft Limit", str(soft) if soft else "—"),
                ("Hard Limit", str(hard) if hard else "—"),
            ],
        )

    def _build_network_card(self, d: dict) -> str:
        """
        Returns HTML for the network I/O card.

        Args:
            d: Network metrics dict.

        Returns:
            HTML string for the network I/O metric card.
        """
        if not d.get("available"):
            return self._error_card("Network I/O", d.get("error", "Unavailable"))

        sent = d.get("bytes_sent_mb", 0)
        recv = d.get("bytes_recv_mb", 0)

        return self._value_card(
            title="Network I/O",
            value=f"{recv:.1f}",
            unit="MB recv",
            color=Theme.blue,
            details=[
                ("Sent", f"{sent:.2f} MB"),
                ("Packets Recv", f"{d.get('packets_recv', 0):,}"),
            ],
        )

    def _build_storage_card(self, d: dict) -> str:
        """
        Returns HTML for the disk storage card.

        Args:
            d: Storage metrics dict.

        Returns:
            HTML string for the storage metric card.
        """
        if not d.get("available"):
            return self._error_card("Storage", d.get("error", "Unavailable"))
    
        pct = d.get("percent", 0)
        used = d.get("used_gb", 0)
        total = d.get("total_gb", 0)
        note = d.get("note")
        color = self._gauge_color(pct)
    
        details = [
            ("Used", f"{used} GB"),
            ("Total", f"{total} GB"),
        ]
    
        # If the fs looks like a docker overlay, show a warning card instead
        if note:
            return (
                f'<div class="db-sys-card db-sys-card--warn">'
                f'<div class="db-sys-card-header">'
                f'<span class="db-sys-card-title">Storage</span>'
                f'<span class="db-sys-warn-badge">Overlay FS</span>'
                f'</div>'
                f'<div class="db-sys-card-big-value" style="color:var(--orange);">'
                f'{used} <span class="db-sys-card-unit">GB used</span>'
                f'</div>'
                f'<div class="db-sys-detail">'
                f'<span class="db-sys-detail-key">Total</span>'
                f'<span class="db-sys-detail-val">{total} GB</span>'
                f'</div>'
                f'<div class="db-sys-error-body">'
                f'<span class="db-sys-error-icon">ℹ</span>'
                f'<span class="db-sys-error-msg">{note}</span>'
                f'</div>'
                f'</div>'
            )
    
        return self._gauge_card("Storage", pct, "%", color, details)
        
    # ── Card primitives ───────────────────────────────────────────────

    def _gauge_card(
        self, title: str, pct: float, unit: str, color: str, details: list
    ) -> str:
        """
        Returns a metric card with a horizontal gauge bar and detail rows.

        Args:
            title: Card heading.
            pct: Percentage fill (0–100) for the gauge.
            unit: Unit label shown next to the value.
            color: CSS color string for the gauge fill and value.
            details: List of (key, value) tuples for the detail rows.

        Returns:
            HTML string for the gauge card.
        """
        clamp = max(0, min(100, pct))
        bar_pct = round(clamp)

        details_html = "".join(
            f'<div class="db-sys-detail">'
            f'<span class="db-sys-detail-key">{k}</span>'
            f'<span class="db-sys-detail-val">{v}</span>'
            f'</div>'
            for k, v in details
        )

        return (
            f'<div class="db-sys-card">'
            f'<div class="db-sys-card-header">'
            f'<span class="db-sys-card-title">{title}</span>'
            f'<span class="db-sys-card-value" style="color:{color};">{pct}{unit}</span>'
            f'</div>'
            f'<div class="db-sys-gauge-wrap">'
            f'<div class="db-sys-gauge-track">'
            f'<div class="db-sys-gauge-fill" '
            f'style="width:{bar_pct}%;background:{color};" '
            f'data-target="{bar_pct}"></div>'
            f'</div>'
            f'</div>'
            f'{details_html}'
            f'</div>'
        )

    def _value_card(
        self, title: str, value: str, unit: str, color: str, details: list
    ) -> str:
        """
        Returns a metric card with a large value and detail rows, no gauge.

        Args:
            title: Card heading.
            value: Primary metric value string.
            unit: Unit label shown below the value.
            color: CSS color for the primary value.
            details: List of (key, value) tuples for the detail rows.

        Returns:
            HTML string for the value card.
        """
        details_html = "".join(
            f'<div class="db-sys-detail">'
            f'<span class="db-sys-detail-key">{k}</span>'
            f'<span class="db-sys-detail-val">{v}</span>'
            f'</div>'
            for k, v in details
        )

        return (
            f'<div class="db-sys-card">'
            f'<div class="db-sys-card-header">'
            f'<span class="db-sys-card-title">{title}</span>'
            f'</div>'
            f'<div class="db-sys-card-big-value" style="color:{color};">'
            f'{value} <span class="db-sys-card-unit">{unit}</span>'
            f'</div>'
            f'{details_html}'
            f'</div>'
        )

    def _error_card(self, title: str, error_msg: str) -> str:
        """
        Returns an error placeholder card for an unavailable metric.

        Args:
            title: The metric name that failed.
            error_msg: The error message or description string.

        Returns:
            HTML string for the error placeholder card.
        """
        return (
            f'<div class="db-sys-card db-sys-card--error">'
            f'<div class="db-sys-card-header">'
            f'<span class="db-sys-card-title">{title}</span>'
            f'<span class="db-sys-error-badge">Unavailable</span>'
            f'</div>'
            f'<div class="db-sys-error-body">'
            f'<span class="db-sys-error-icon">⚠</span>'
            f'<span class="db-sys-error-msg">{error_msg}</span>'
            f'</div>'
            f'</div>'
        )

    # ── Helpers ───────────────────────────────────────────────────────

    def _gauge_color(self, pct: float) -> str:
        """
        Returns a CSS color string based on the utilisation percentage.

        Args:
            pct: Utilisation percentage (0–100).

        Returns:
            A CSS color string from the Theme palette.
        """
        if pct >= 85:
            return Theme.red
        if pct >= 60:
            return Theme.orange
        return Theme.teal
