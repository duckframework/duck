"""
CounterApp views.
"""
from duck.views import View
from duck.shortcuts import static, to_response, resolve
from duck.html.components import to_component, ForceUpdate
from duck.html.components.container import FlexContainer
from duck.html.components.heading import Heading
from duck.html.components.button import Button
from duck.html.components.label import Label
from duck.html.components.page import Page
from duck.html.components.style import Style
from duck.html.components.script import Script



# Page-scoped CSS — dark editorial theme matching duckframework.xyz
PAGE_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --accent:        #F5C842;
    --accent-dim:    rgba(245,200,66,0.12);
    --accent-border: rgba(245,200,66,0.28);
    --bg:            #080808;
    --bg-card:       #0e0e0e;
    --border:        rgba(255,255,255,0.07);
    --border-strong: rgba(255,255,255,0.13);
    --text:          #ebebeb;
    --text-muted:    rgba(235,235,235,0.45);
    --text-faint:    rgba(235,235,235,0.22);
    --radius:        12px;
    --mono:          'DM Mono', monospace;
    --display:       'Syne', system-ui, sans-serif;
}

html, body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--display);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
}

/* Dot grid texture */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.022) 1px, transparent 1px);
    background-size: 54px 54px;
    pointer-events: none;
    z-index: 0;
}

/* Gold glow orb */
body::after {
    content: '';
    position: fixed;
    top: -180px;
    left: 50%;
    transform: translateX(-50%);
    width: 700px;
    height: 600px;
    background: radial-gradient(ellipse, rgba(245,200,66,0.055) 0%, transparent 65%);
    pointer-events: none;
    z-index: 0;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }

/* ── Layout ─────────────────────────────────────────────────────── */
#counterapp-root {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 40px 20px 60px;
    gap: 32px;
}

/* ── Back link ───────────────────────────────────────────────────── */
.counterapp-back {
    align-self: flex-start;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-faint) !important;
    text-decoration: none !important;
    transition: color 0.15s;
    letter-spacing: 0.02em;
    padding: 4px 0;
}
.counterapp-back:hover { color: var(--text-muted) !important; }
.counterapp-back .bi { font-size: 0.9rem; }

/* ── Main card ───────────────────────────────────────────────────── */
.counterapp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 48px 44px 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 32px;
    width: 100%;
    max-width: 420px;
    position: relative;
    overflow: hidden;
}
.counterapp-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-border), transparent);
}

/* ── Header ──────────────────────────────────────────────────────── */
.counterapp-header {
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.counterapp-kicker {
    font-family: var(--mono);
    font-size: 0.68rem;
    font-weight: 500;
    color: var(--accent);
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.counterapp-title {
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: #fff !important;
    letter-spacing: -0.02em !important;
}

/* ── Counter ring ────────────────────────────────────────────────── */
.counterapp-ring-wrap {
    position: relative;
    width: 164px;
    height: 164px;
    flex-shrink: 0;
}
.counterapp-ring-svg {
    width: 164px;
    height: 164px;
    transform: rotate(-90deg);
}
.counterapp-ring-track {
    fill: none;
    stroke: rgba(255,255,255,0.06);
    stroke-width: 5;
}
.counterapp-ring-fill {
    fill: none;
    stroke: var(--accent);
    stroke-width: 5;
    stroke-linecap: round;
    stroke-dasharray: 440;
    stroke-dashoffset: 440;
    transition: stroke-dashoffset 0.45s cubic-bezier(0.4,0,0.2,1);
}
.counterapp-ring-center {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
}
.counterapp-count {
    font-family: var(--mono) !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    color: #fff !important;
    line-height: 1 !important;
    letter-spacing: -0.04em !important;
    transition: transform 0.12s ease !important;
}
.counterapp-count.bump {
    transform: scale(1.12) !important;
}
.counterapp-count-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-faint);
    font-family: var(--mono);
}

/* ── Buttons ─────────────────────────────────────────────────────── */
.counterapp-btn-row {
    display: flex;
    gap: 12px;
    align-items: center;
}
/* Hover/active effects — inline styles handle base appearance */
#ca-inc-btn:hover  { filter: brightness(1.1); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(245,200,66,0.3); }
#ca-inc-btn:active { transform: scale(0.97); }
#ca-dec-btn:hover  { background: rgba(255,255,255,0.1) !important; color: #ebebeb !important; transform: translateY(-1px); }
#ca-reset-btn:hover { color: rgba(235,235,235,0.7) !important; border-color: rgba(255,255,255,0.2) !important; }

/* ── View source link (GitHub) ─────────────────────────────────── */
.counterapp-src-toggle {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-faint) !important;
    text-decoration: none !important;
    font-family: var(--display);
    transition: color 0.15s;
    letter-spacing: 0.02em;
}
.counterapp-src-toggle:hover { color: var(--accent) !important; text-decoration: none !important; }
.counterapp-src-toggle .bi { font-size: 0.88rem; }

/* ── Powered badge ───────────────────────────────────────────────── */
.counterapp-badge {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.75rem;
    color: var(--text-faint);
    font-family: var(--mono);
    letter-spacing: 0.04em;
}
.counterapp-badge a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
}
.counterapp-badge a:hover { text-decoration: underline; }
.counterapp-badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 6px rgba(245,200,66,0.6);
    flex-shrink: 0;
}

/* ── Mobile ──────────────────────────────────────────────────────── */
@media (max-width: 600px) {
    #counterapp-root {
        padding: 28px 16px 48px;
        gap: 24px;
        justify-content: flex-start;
        padding-top: 32px;
    }
    .counterapp-card {
        padding: 32px 22px 28px;
        gap: 24px;
        max-width: 100%;
        border-radius: 18px;
    }
    .counterapp-ring-wrap { width: 140px; height: 140px; }
    .counterapp-ring-svg  { width: 140px; height: 140px; }
    .counterapp-count { font-size: 2.2rem !important; }
    .counterapp-btn-row { gap: 10px; width: 100%; }
    #ca-inc-btn { flex: 1; padding: 13px 16px !important; }
    #ca-dec-btn { padding: 13px 16px !important; }
    #ca-reset-btn { width: 100%; justify-content: center; }
}
"""

# Ring progress JS + copy button
PAGE_SCRIPT = """
(function() {
    var MAX = 100;
    var CIRCUMFERENCE = 440;

    function updateRing(count) {
        var fill = document.getElementById('ca-ring-fill');
        if (!fill) return;
        var clamped = Math.min(Math.abs(count), MAX);
        var offset  = CIRCUMFERENCE - (clamped / MAX) * CIRCUMFERENCE;
        fill.style.strokeDashoffset = offset;
        // Negative count — turn ring red
        fill.style.stroke = count < 0 ? '#ff6b6b' : '#F5C842';
    }

    function bumpCount() {
        var el = document.getElementById('ca-count');
        if (!el) return;
        el.classList.remove('bump');
        void el.offsetWidth; // reflow
        el.classList.add('bump');
        setTimeout(function() { el.classList.remove('bump'); }, 180);
    }

    // Expose for Duck to call after Lively updates
    window.caUpdateRing  = updateRing;
    window.caBumpCount   = bumpCount;

})();
"""


class HomePage(Page):
    """
    CounterApp home page — redesigned with dark editorial aesthetic.
    """
    def on_create(self):
        super().on_create()
        self.style["font-family"] = "var(--display, system-ui)"
        self.set_title("Counter App — Duck Framework")

        # Stylesheets
        self.add_stylesheet(href=static("counterapp/css/bootstrap-icons.min.css"))
        self.add_stylesheet(href=static("counterapp/css/prism.css"))

        # Scripts
        self.add_script(src=static("counterapp/js/prism.js"), defer=True)
        self.add_script(src=static("counterapp/js/jquery-3.7.1.min.js"))

        # Inject page styles
        self.add_to_head(Style(inner_html=PAGE_STYLES))

        # Counter state
        self.counter = 0
        def on_increment(btn, *_):
            self.counter += 1
            self.count_label.text = self.counter
            # Sync ring via JS
            self.count_label.props["data-count"] = str(self.counter)

        def on_decrement(btn, *_):
            self.counter -= 1
            self.count_label.text = self.counter
            self.count_label.props["data-count"] = str(self.counter)

        def on_reset(btn, *_):
            self.counter = 0
            self.count_label.text = self.counter
            self.count_label.props["data-count"] = "0"


        # ── Root wrapper ──────────────────────────────────────────
        root = FlexContainer(id="counterapp-root")
        root.style["flex-direction"] = "column"
        root.style["align-items"] = "center"

        # Back link
        back = to_component("", "a")
        back.klass = "counterapp-back"
        back.props["href"] = resolve("home", fallback_url="/")
        back_icon = to_component("", "span")
        back_icon.klass = "bi bi-arrow-left"
        back_text = to_component("Home", "span")
        back.add_children([back_icon, back_text])
        root.add_child(back)

        # ── Main card ─────────────────────────────────────────────
        card = FlexContainer(flex_direction="column")
        card.klass = "counterapp-card"

        # Header
        header = FlexContainer()
        header.klass = "counterapp-header"
        kicker = to_component("Lively Component System", "span")
        kicker.klass = "counterapp-kicker"
        title = Heading("h1", text="Counter App", klass="counterapp-title")
        header.add_children([kicker, title])
        card.add_child(header)

        # Ring progress
        ring_wrap = to_component("", "div")
        ring_wrap.klass = "counterapp-ring-wrap"

        svg = to_component(
            '<circle class="counterapp-ring-track" cx="82" cy="82" r="70"/>'
            '<circle id="ca-ring-fill" class="counterapp-ring-fill" cx="82" cy="82" r="70"/>',
            "svg",
        )
        svg.klass = "counterapp-ring-svg"
        svg.props["viewBox"] = "0 0 164 164"
        svg.props["xmlns"]   = "http://www.w3.org/2000/svg"

        ring_center = to_component("", "div")
        ring_center.klass = "counterapp-ring-center"

        self.count_label = Label(text=self.counter, id="ca-count")
        self.count_label.klass = "counterapp-count"
        self.count_label.props["data-count"] = "0"

        count_sub = to_component("count", "span")
        count_sub.klass = "counterapp-count-label"

        ring_center.add_children([self.count_label, count_sub])
        ring_wrap.add_children([svg, ring_center])
        card.add_child(ring_wrap)

        # Button row
        btn_row = FlexContainer()
        btn_row.klass = "counterapp-btn-row"

        # Base inline styles shared by all buttons
        BASE_BTN = {
            "display": "inline-flex",
            "align-items": "center",
            "justify-content": "center",
            "gap": "8px",
            "border-radius": "12px",
            "font-family": "Syne, system-ui, sans-serif",
            "font-weight": "700",
            "font-size": "0.92rem",
            "cursor": "pointer",
            "transition": "all 0.18s ease",
            "letter-spacing": "0.01em",
            "border": "none",
        }

        # Decrement button
        self.dec_btn = to_component("", "button")
        self.dec_btn.id = "ca-dec-btn"
        self.dec_btn.inner_html = "<span class='bi bi-dash-lg'></span>"
        self.dec_btn.props["type"] = "button"
        self.dec_btn.style.update({
            **BASE_BTN,
            "background": "rgba(255,255,255,0.06)",
            "color": "rgba(235,235,235,0.55)",
            "border": "1px solid rgba(255,255,255,0.13)",
            "padding": "13px 20px",
        })
        self.dec_btn.bind(
            "click",
            on_decrement,
            update_targets=[self.count_label],
            update_self=False,
        )

        # Increment button
        self.inc_btn = to_component("", "button")
        self.inc_btn.id = "ca-inc-btn"
        self.inc_btn.inner_html = "<span class='bi bi-plus-lg'></span> Increment"
        self.inc_btn.props["type"] = "button"
        self.inc_btn.style.update({
            **BASE_BTN,
            "background": "#F5C842",
            "color": "#111111",
            "padding": "13px 28px",
        })
        self.inc_btn.bind(
            "click",
            on_increment,
            update_targets=[self.count_label],
            update_self=False,
        )

        btn_row.add_children([self.dec_btn, self.inc_btn])
        card.add_child(btn_row)

        # Reset button
        self.reset_btn = to_component("", "button")
        self.reset_btn.id = "ca-reset-btn"
        self.reset_btn.inner_html = "Reset"
        self.reset_btn.props["type"] = "button"
        self.reset_btn.style.update({
            **BASE_BTN,
            "background": "transparent",
            "color": "rgba(235,235,235,0.28)",
            "border": "1px solid rgba(255,255,255,0.07)",
            "padding": "8px 16px",
            "font-size": "0.78rem",
            "border-radius": "8px",
        })
        self.reset_btn.bind(
            "click",
            on_reset,
            update_targets=[self.count_label],
            update_self=False,
        )
        card.add_child(self.reset_btn)

        # View source — links directly to GitHub
        src_link = to_component("", "a")
        src_link.klass = "counterapp-src-toggle"
        src_link.props["href"] = "https://github.com/duckframework/duck/blob/main/duck/etc/apps/counterapp/views/__init__.py"
        src_link.props["target"] = "_blank"
        src_link.props["rel"] = "noopener noreferrer"
        src_link.inner_html = "<span class='bi bi-github'></span> View source on GitHub"
        card.add_child(src_link)

        root.add_child(card)

        # ── Powered badge ─────────────────────────────────────────
        badge = to_component("", "div")
        badge.klass = "counterapp-badge"
        dot = to_component("", "span")
        dot.klass = "counterapp-badge-dot"
        badge_text = to_component("", "span")
        badge_text.inner_html = (
            "Powered by <a href='https://duckframework.xyz' "
            "target='_blank' rel='noopener noreferrer'>Duck Framework</a> "
            "— real-time UI, pure Python"
        )
        badge.add_children([dot, badge_text])
        root.add_child(badge)

        self.add_to_body(root)

        # Ring sync + bump script — runs after Lively patches the DOM
        self.add_to_body(Script(inner_html=PAGE_SCRIPT))
        self.add_to_body(Script(inner_html="""
// Sync ring on every Lively DOM patch
document.addEventListener('DOMContentLoaded', function() {
    var observer = new MutationObserver(function() {
        var el = document.getElementById('ca-count');
        if (el) {
            var n = parseInt(el.getAttribute('data-count') || el.innerText, 10) || 0;
            window.caUpdateRing && window.caUpdateRing(n);
            window.caBumpCount && window.caBumpCount();
        }
    });
    var target = document.getElementById('ca-count');
    if (target) observer.observe(target, { childList: true, characterData: true, subtree: true });
});
"""))


class HomeView(View):
    """
    CounterApp home view.
    """
    def run(self):
        page = HomePage(self.request)
        return to_response(page)
