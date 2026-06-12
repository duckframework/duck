"""
WelcomePage — the page shown to new users upon installing Duck Framework.

Assembles the navbar, hero, stats ticker, features grid, code showcase,
links section, and footer. Injects interactive JS for the cursor glow,
particle field, count-up stats, and install-command copy button.
"""

from duck.html.components.page import Page
from duck.html.components.container import Container, FlexContainer
from duck.html.components.script import Script
from duck.shortcuts import static

from ..components.nav_footer import NavBar, Footer
from ..components.hero import HeroSection
from ..components.stats_ticker import StatsTicker
from ..components.features_grid import FeaturesGrid
from ..components.code_showcase import CodeShowcase
from ..components.links_section import LinksSection


class WelcomePage(Page):
    """
    The welcome / onboarding page shown after installing Duck Framework.

    Static and purely presentational — all interactivity (cursor glow,
    particles, count-up, copy button) runs client-side via injected JS,
    since this page is shown before any project-specific setup exists.
    """

    def on_create(self) -> None:
        """
        Sets up SEO metadata, injects styles and scripts, and builds layout.
        """
        super().on_create()

        # SEO and page metadata
        self.set_title("Welcome · Duck Framework")
        self.set_description(
            "Duck Framework is installed and ready. Explore the docs, "
            "browse components, and start building your reactive Python web app."
        )
        self.set_favicon("/static/favicon.ico")
        self.set_accessibility(lang="en")

        # Inject welcome stylesheet
        self.add_stylesheet(static("welcome/css/welcome.css"))

        self.build_layout()
        self.add_interactive_script()

    def build_layout(self) -> None:
        """
        Constructs the full page layout and adds it to the body.
        """
        shell = FlexContainer(
            klass="wc-shell",
            style={
                "flex-direction": "column",
                "gap": "15px",
            },
            children=[
                self.build_background_layers(),
                NavBar(),
                HeroSection(),
                StatsTicker(),
                self.build_section_label("Why Duck Framework"),
                FeaturesGrid(),
                self.build_section_label("See It In Action"),
                CodeShowcase(),
                self.build_section_label("Learn More"),
                LinksSection(),
                Footer(),
            ],
        )

        self.add_to_body(shell)

    def build_background_layers(self) -> Container:
        """
        Returns the ambient background elements: glow orb, scan line,
        particle field, and mouse-follow glow.

        Returns:
            A Container holding all background decoration elements.
        """
        return Container(
            inner_html=(
                '<div class="wc-glow-orb" aria-hidden="true"></div>'
                '<div class="wc-scanline" aria-hidden="true"></div>'
                '<div class="wc-particles" id="wc-particles" aria-hidden="true"></div>'
                '<div class="wc-cursor-glow" id="wc-cursor-glow" aria-hidden="true"></div>'
            ),
        )

    def build_section_label(self, text: str) -> Container:
        """
        Returns a small uppercase section divider label.

        Args:
            text: The label text to display.

        Returns:
            A Container styled as a section label.
        """
        return Container(klass="wc-section-label", text=text)

    def add_interactive_script(self) -> None:
        """
        Injects the client-side JS powering all page interactivity.

        Covers: floating particles, mouse-follow ambient glow,
        count-up stat animation on scroll, and the install command
        copy-to-clipboard behaviour.
        """
        script = Script(inner_html=self.interactive_js())
        self.add_to_body(script)

    def interactive_js(self) -> str:
        """
        Returns the full interactive JS block as a string.

        Returns:
            JavaScript source code.
        """
        return """
        // Spawn floating ambient particles across the page
        (function spawnParticles() {
            const container = document.getElementById('wc-particles');
            if (!container) return;

            const count = 24;
            for (let i = 0; i < count; i++) {
                const dot = document.createElement('div');
                dot.className = 'wc-particle';
                const size = 1 + Math.random() * 2;
                dot.style.cssText = [
                    `left: ${Math.random() * 100}%`,
                    `width: ${size}px`,
                    `height: ${size}px`,
                    `--dur: ${8 + Math.random() * 12}s`,
                    `--delay: ${Math.random() * 10}s`,
                    `opacity: ${0.1 + Math.random() * 0.3}`,
                ].join(';');
                container.appendChild(dot);
            }
        })();

        // Mouse-follow ambient glow
        (function cursorGlow() {
            const glow = document.getElementById('wc-cursor-glow');
            if (!glow) return;

            // Disable on touch devices to avoid jank
            if (window.matchMedia('(pointer: coarse)').matches) {
                glow.style.display = 'none';
                return;
            }

            document.addEventListener('mousemove', function (e) {
                glow.style.left = e.clientX + 'px';
                glow.style.top = e.clientY + 'px';
            });
        })();

        // Count-up animation for the stats ticker, triggered on scroll into view
        (function countUpStats() {
            const ticker = document.getElementById('wc-stats-ticker');
            if (!ticker) return;

            const nums = ticker.querySelectorAll('.wc-stat-num');
            let animated = false;

            function animateNumbers() {
                if (animated) return;
                animated = true;

                nums.forEach(function (el) {
                    const target = parseInt(el.dataset.target, 10) || 0;
                    const suffix = el.dataset.suffix || '';
                    const duration = 1200;
                    const start = performance.now();

                    function tick(now) {
                        const progress = Math.min((now - start) / duration, 1);
                        const eased = 1 - Math.pow(1 - progress, 3);
                        const current = Math.round(eased * target);
                        el.textContent = current + suffix;
                        if (progress < 1) requestAnimationFrame(tick);
                    }
                    requestAnimationFrame(tick);
                });
            }

            const observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        animateNumbers();
                        observer.disconnect();
                    }
                });
            }, { threshold: 0.4 });

            observer.observe(ticker);
        })();

        // Install command — click to copy to clipboard
        (function installCopy() {
            const card = document.getElementById('wc-install-card');
            const label = document.getElementById('wc-copy-label');
            if (!card || !label) return;

            card.addEventListener('click', function () {
                const text = 'pip install duck-framework';
                navigator.clipboard.writeText(text).then(function () {
                    label.textContent = 'copied!';
                    card.classList.add('copied');
                    setTimeout(function () {
                        label.textContent = 'copy';
                        card.classList.remove('copied');
                    }, 1800);
                });
            });
        })();

        // Typing-style reveal for the tagline cursor — stop blinking after a pause
        (function taglineCursor() {
            const cursor = document.querySelector('.wc-typed-cursor');
            if (!cursor) return;

            setTimeout(function () {
                cursor.style.opacity = '0';
                cursor.style.transition = 'opacity 0.6s ease';
            }, 6000);
        })();
        """
