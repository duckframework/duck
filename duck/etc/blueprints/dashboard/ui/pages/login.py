"""
LoginPage — authentication gateway for the Duck Framework dashboard.

Renders a full-page login form. On successful credential submission,
authenticates via duck.contrib.auth, issues a JWT token, and redirects
to the dashboard. Incorrect credentials re-render the form with an
animated error state.
"""
import asyncio

from duck.html.components.page import Page
from duck.html.components.container import Container
from duck.html.components.form import Form
from duck.html.components.input import Input
from duck.html.components.button import Button
from duck.html.components.paragraph import Paragraph
from duck.html.components.style import Style
from duck.shortcuts import static, resolve


# The default dashboard user ID
DASHBOARD_USER_ID = 9999


class LoginPage(Page):
    """
    Full-page login screen for the dashboard JWT authentication flow.

    On submit, validates credentials, issues a
    JWT via the jwt backend, and redirects to the dashboard index.
    An error message animates in on failure without a full page reload.
    """

    def on_create(self) -> None:
        """
        Sets up page metadata, injects styles, and builds the login layout.
        """
        super().on_create()

        # Page metadata
        self.set_title("Login · Duck Dashboard")
        self.set_description("Sign in to access the Duck Framework server dashboard.")
        self.set_accessibility(lang="en")
        self.set_robots("noindex, nofollow")

        # Inject dashboard stylesheet for shared tokens + login styles
        self.add_stylesheet(static("dashboard/css/dashboard.css"))

        # Build the error label — updated reactively on bad credentials
        self.error_label = Paragraph(
            id="login-error",
            klass="login-error login-error--hidden",
            text="",
        )

        # Build and bind the form
        self.login_form = self._build_form()

        # Assemble full layout
        self.add_to_body(self._build_layout())
        self.add_to_body(self._build_login_styles())

    # ── Layout ─────────────────────────────────────────────────────────

    def _build_layout(self) -> Container:
        """
        Returns the full-screen centered login shell.

        Returns:
            A Container wrapping the login card.
        """
        return Container(
            id="login-shell",
            children=[
                self._build_background_grid(),
                self._build_card(),
            ],
        )

    def _build_background_grid(self) -> Container:
        """
        Returns a decorative SVG grid overlay for the background.

        Returns:
            A Container with the SVG background element.
        """
        return Container(
            id="login-bg-grid",
            inner_html=(
                '<svg class="login-bg-svg" viewBox="0 0 800 600" '
                'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">'
                '<defs>'
                '<radialGradient id="login-glow" cx="50%" cy="50%" r="50%">'
                '<stop offset="0%" stop-color="#F5A623" stop-opacity="0.06"/>'
                '<stop offset="100%" stop-color="#F5A623" stop-opacity="0"/>'
                '</radialGradient>'
                '</defs>'
                '<rect width="100%" height="100%" fill="url(#login-glow)"/>'
                '</svg>'
            ),
        )

    def _build_card(self) -> Container:
        """
        Returns the centered login card with header, form, and footer.

        Returns:
            A Container styled as the login card.
        """
        return Container(
            id="login-card",
            children=[
                self._build_card_header(),
                self.login_form,
                self.error_label,
                self._build_card_footer(),
            ],
        )

    def _build_card_header(self) -> Container:
        """
        Returns the card header with brand dot, title, and subtitle.

        Returns:
            A Container with the login card heading markup.
        """
        return Container(
            id="login-header",
            inner_html=(
                '<div class="login-brand">'
                '<span class="db-brand-dot"></span>'
                '<span class="login-brand-text">Duck Dashboard</span>'
                '</div>'
                '<h1 class="login-title">Sign in</h1>'
                '<p class="login-subtitle">Enter your credentials to access the server dashboard.</p>'
            ),
        )

    def _build_card_footer(self) -> Container:
        """
        Returns the card footer with security notice.

        Returns:
            A Container with the footer notice text.
        """
        return Container(
            id="login-footer",
            inner_html=(
                '<p class="login-footer-text">'
                '<span class="login-lock-icon">🔒</span>'
                ' Secured'
                '</p>'
            ),
        )

    # ── Form ────────────────────────────────────────────────────────────

    def _build_form(self) -> Form:
        """
        Returns the login Form component with username, password, and submit.

        Returns:
            A Form component with bound submit handler.
        """
        # Username field
        username_field = Container(
            id="login-field-username",
            klass="login-field",
            children=[
                Container(
                    inner_html='<label class="login-label" for="login-username">Username</label>',
                ),
                Input(
                    id="login-username",
                    klass="login-input",
                    input_type="text",
                    name="username",
                    placeholder="Enter your username",
                    required=True,
                    autocomplete="username",
                ),
            ],
        )

        # Password field
        password_field = Container(
            id="login-field-password",
            klass="login-field",
            children=[
                Container(
                    inner_html='<label class="login-label" for="login-password">Password</label>',
                ),
                Input(
                    id="login-password",
                    klass="login-input",
                    type="password",
                    name="password",
                    placeholder="Enter your password",
                    required=True,
                    autocomplete="current-password",
                ),
            ],
        )

        # Submit button
        self.submit_btn = Button(
            id="login-submit-btn",
            klass="login-submit-btn",
            type="submit",
            inner_html=(
                '<span id="login-btn-text">Sign in</span>'
                '<span id="login-btn-spinner" class="login-spinner login-spinner--hidden">'
                '<svg width="14" height="14" viewBox="0 0 14 14" fill="none">'
                '<circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.5" '
                'stroke-dasharray="20" stroke-dashoffset="20" class="spin-circle"/>'
                '</svg>'
                '</span>'
            ),
        )

        form = Form(
            id="login-form",
            children=[username_field, password_field, self.submit_btn],
        )

        # Bind form submit to the async login handler
        form.bind(
            "submit",
            self.handle_login,
            update_self=False,
            update_targets=[self.error_label],
        )

        return form

    # ── Event handler ───────────────────────────────────────────────────

    async def handle_login(self, form, event: str, form_inputs: dict, ws) -> None:
        """
        Handles the login form submission.

        Authenticates via duck.contrib.auth, issues a JWT via the jwt
        backend on success, and redirects to the dashboard. Shows an
        animated error message on failure.

        Args:
            form: The Form component that fired the event.
            event: The event name string ("submit").
            form_inputs: Dict of {name: value} from all named form inputs.
            ws: The active LivelyWebSocketView instance.
        """
        from duck.contrib.auth import async_login
        from ...utils import check_username_and_pwd
        
        # Show spinner while processing
        await ws.execute_js(
            "document.getElementById('login-btn-text').textContent='Signing in...';"
            "document.getElementById('login-btn-spinner').classList.remove('login-spinner--hidden');"
            "document.getElementById('login-submit-btn').disabled=true;"
        )
        
        # Sleep a little for the spinner to be bit visible.
        await asyncio.sleep(.5)
        
        # Resolve provided username and password
        username = form_inputs.get("username", "").strip()
        password = form_inputs.get("password", "")

        # Validate non-empty inputs client-side
        if not username or not password:
            await self._show_error_async("Username and password are required.", ws)
            return

        # Authenticate against the configured backend
        credentials_correct = check_username_and_pwd(username, password)
        
        if not credentials_correct:
            await self._show_error_async("Invalid username or password.", ws)
            return

        # Issue JWT token using the jwt backend and log user in
        await async_login(request=self.request, user_id=DASHBOARD_USER_ID, backend="jwt")
        
        # Redirect to the dashboard on successful login
        dashboard_url = resolve("dashboard.index")
        await ws.execute_js(f"window.open('{dashboard_url}');")

    async def _show_error_async(self, message: str, ws) -> None:
        """
        Updates the error label with an animated error message.

        Args:
            message: The error string to display.
            ws: The active WebSocket connection for JS execution.
        """
        # Update the error label text and make it visible
        self.error_label.text = message
        self.error_label.props["class"] = "login-error login-error--visible"

        # Reset the button state
        await ws.execute_js(
            "document.getElementById('login-btn-text').textContent='Sign in';"
            "document.getElementById('login-btn-text').style.opacity='1';"
            "document.getElementById('login-btn-spinner').classList.add('login-spinner--hidden');"
            "document.getElementById('login-submit-btn').disabled=false;"
            # Shake the card for tactile error feedback
            "var card=document.getElementById('login-card');"
            "card.classList.add('login-card--shake');"
            "setTimeout(()=>card.classList.remove('login-card--shake'),500);"
        )

    # ── Styles ──────────────────────────────────────────────────────────

    def _build_login_styles(self) -> Style:
        """
        Returns all login-page-specific CSS rules.

        Returns:
            A Style component with login UI styles.
        """
        return Style(
            inner_html="""
/* ── Login shell ── */
#login-shell {
  position: relative;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  overflow: hidden;
}

/* Background radial glow SVG */
.login-bg-svg {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

/* ── Card ── */
#login-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 380px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2.25rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: card-enter 0.5s cubic-bezier(0.22,1,0.36,1) both;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.03), 0 24px 64px rgba(0,0,0,0.6);
}

@keyframes card-enter {
  from { opacity: 0; transform: translateY(20px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.login-card--shake {
  animation: login-shake 0.45s cubic-bezier(0.36,0.07,0.19,0.97);
}

@keyframes login-shake {
  0%,100% { transform: translateX(0); }
  15%     { transform: translateX(-8px); }
  30%     { transform: translateX(7px); }
  45%     { transform: translateX(-5px); }
  60%     { transform: translateX(4px); }
  75%     { transform: translateX(-2px); }
}

/* ── Header ── */
#login-header { display: flex; flex-direction: column; gap: 0.75rem; }

.login-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.login-brand-text {
  font-family: var(--mono);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
}

.login-title {
  font-family: var(--mono);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1;
}

.login-subtitle {
  font-size: 0.8rem;
  color: var(--muted);
  line-height: 1.5;
}

/* ── Form fields ── */
#login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.login-label {
  font-family: var(--mono);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--muted);
}

.login-input {
  width: 100%;
  background: var(--surface-3);
  color: var(--text);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-sm);
  padding: 0.65rem 0.85rem;
  font-family: var(--mono);
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
}

.login-input:focus {
  border-color: var(--orange);
  box-shadow: 0 0 0 3px var(--orange-dim), inset 0 1px 3px rgba(0,0,0,0.3);
  background: var(--surface-2);
}

.login-input::placeholder { color: var(--muted); }

/* ── Submit button ── */
.login-submit-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--orange);
  color: #111;
  font-family: var(--mono);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s, box-shadow 0.15s;
  box-shadow: 0 2px 12px rgba(245,166,35,0.25);
  margin-top: 0.25rem;
}

.login-submit-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(245,166,35,0.35);
}

.login-submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Spinner inside button ── */
.login-spinner { display: inline-flex; }
.login-spinner--hidden { display: none; }

.spin-circle {
  animation: draw-circle 0.8s linear infinite;
  transform-origin: center;
}

@keyframes draw-circle {
  0%   { stroke-dashoffset: 20; transform: rotate(0deg); }
  50%  { stroke-dashoffset: 5; }
  100% { stroke-dashoffset: 20; transform: rotate(360deg); }
}

/* ── Error label ── */
.login-error {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--red);
  background: var(--red-dim);
  border: 1px solid rgba(224,82,82,0.18);
  border-radius: var(--radius-sm);
  padding: 0.6rem 0.85rem;
  text-align: center;
  transition: opacity 0.2s, transform 0.2s;
}

.login-error--hidden {
  display: none;
}

.login-error--visible {
  display: block;
  animation: error-appear 0.25s ease both;
}

@keyframes error-appear {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Footer ── */
#login-footer {
  border-top: 1px solid var(--border-subtle);
  padding-top: 1rem;
}

.login-footer-text {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--muted);
  text-align: center;
  letter-spacing: 0.03em;
}

.login-lock-icon { font-size: 0.65rem; }
"""
        )
