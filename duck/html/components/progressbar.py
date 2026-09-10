"""
Progress bar component.
"""

from duck.html.components.theme import Theme
from duck.html.components.container import Container
from duck.html.components.script import Script


PROGRESS_BAR_SCRIPT = """
const PROGRESS_FILL_TRANSITION = 'transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)';

function updateProgressBar(progressBar, progress, autoHideWhenZero = true) {
  const progressBarInner = progressBar.querySelector('.progress-bar-inner');
  if (!progressBarInner) return;

  progress = Math.max(0, Math.min(100, progress));

  if (progress <= 0 && autoHideWhenZero) {
    hideProgressBar(progressBar);
    return;
  }

  // Cancel any hide currently in flight so it can't fight this update.
  cancelPendingHide(progressBar);

  const wasHidden = progressBar.style.opacity !== '1';

  if (wasHidden) {
    // Start from empty with no transition, force a reflow so the browser
    // commits that starting point, then restore the transition. Without
    // this, the display/opacity/transform changes can collapse into a
    // single frame and the fill jumps or flickers instead of animating
    // smoothly forward.
    progressBarInner.style.transition = 'none';
    progressBarInner.style.transform = 'scaleX(0)';
    progressBar.style.display = 'block';
    void progressBar.offsetHeight;
    progressBarInner.style.transition = PROGRESS_FILL_TRANSITION;
    progressBar.style.opacity = '1';
  }

  progressBarInner.style.transform = `scaleX(${progress / 100})`;
}

function hideProgressBar(progressBar) {
  const progressBarInner = progressBar.querySelector('.progress-bar-inner');
  const alreadyHidden = progressBar.style.opacity === '0';

  cancelPendingHide(progressBar);

  // Keep the fill exactly where it is — only opacity should move, so the
  // bar never appears to shrink backwards while it fades out.
  progressBar.style.opacity = '0';

  if (alreadyHidden) {
    finishHide(progressBar, progressBarInner);
    return;
  }

  const onFadeOut = (event) => {
    if (event.target !== progressBar || event.propertyName !== 'opacity') return;
    finishHide(progressBar, progressBarInner);
  };

  progressBar._hideHandler = onFadeOut;
  progressBar.addEventListener('transitionend', onFadeOut);
}

function finishHide(progressBar, progressBarInner) {
  cancelPendingHide(progressBar);
  progressBar.style.display = 'none';

  if (progressBarInner) {
    // Reset instantly, with no transition, now that the bar is invisible,
    // so the next show animates forward from empty instead of rewinding
    // from wherever the fill last stopped.
    progressBarInner.style.transition = 'none';
    progressBarInner.style.transform = 'scaleX(0)';
    void progressBarInner.offsetHeight;
    progressBarInner.style.transition = PROGRESS_FILL_TRANSITION;
  }
}

function cancelPendingHide(progressBar) {
  if (progressBar._hideHandler) {
    progressBar.removeEventListener('transitionend', progressBar._hideHandler);
    progressBar._hideHandler = null;
  }
}
"""


class ProgressBar(Container):
    """
    iOS-style linear progress bar with JavaScript and Python update helpers.

    Colors are themeable: they default to Theme.current.progress_color and
    Theme.current.progress_track_color when the active Theme.current defines them, and can
    always be overridden per-instance via set_progress_color/set_track_color.
    """

    TRACK_HEIGHT = "3px"
    FILL_TRANSITION = "transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
    FADE_TIP = True
    FADE_MASK = "linear-gradient(to right, black 0%, black 88%, transparent 100%)"

    # Colors
    FILL_COLOR = getattr(Theme.current, "progress_color", getattr(Theme.current, "accent_color", "#F5C842"))
    TRACK_COLOR = getattr(Theme.current, "progress_track_color", "rgba(0, 0, 0, 0.1)")

    def on_create(self) -> None:
        """
        Initialize and compose the progress bar.
        """
        super().on_create()

        # Component setup
        self.bg_color = self.TRACK_COLOR
        self.props.setdefault("id", "progress-bar")
        self.style.update({
            "width": "100%",
            "height": self.TRACK_HEIGHT,
            "overflow": "hidden",
            "display": "none",
            "opacity": "0",
            "transition": "opacity 0.2s ease",
            "border-radius": Theme.current.border_radius,
        })

        # Component children
        inner_style = {
            "width": "100%",
            "height": "100%",
            "transform-origin": "left",
            "transform": "scaleX(0)",
            "will-change": "transform",
            "transition": self.FILL_TRANSITION,
            "border-radius": Theme.current.border_radius,
        }

        if self.FADE_TIP:
            inner_style["-webkit-mask-image"] = self.FADE_MASK
            inner_style["mask-image"] = self.FADE_MASK

        self._progress_bar = Container(
            klass="progress-bar-inner",
            bg_color=self.FILL_COLOR,
            style=inner_style,
        )

        self.add_children([
            self._progress_bar,
            Script(inner_html=PROGRESS_BAR_SCRIPT),
        ])

    # Public API

    def update_progress(self, progress: int) -> None:
        """
        Update the progress bar from Python.

        Args:
            progress: Progress percentage between ``0`` and ``100``.

        Raises:
            TypeError: If progress is not an integer.
            ValueError: If progress is outside ``0`` to ``100``.
        """
        if not isinstance(progress, int):
            raise TypeError("Progress must be an integer.")

        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100.")

        visible = progress > 0

        # Update track style
        self.style.update({
            "display": "block" if visible else "none",
            "opacity": "1" if visible else "0",
        })

        if visible:
            self._progress_bar.style.update({
                "transition": self.FILL_TRANSITION,
                "transform": f"scaleX({progress / 100})",
            })
        else:
            # Snap the fill back to empty without animating it — the
            # track's opacity fade above is the only motion that should
            # be visible, so the bar never appears to run backwards
            # before it hides.
            self._progress_bar.style.update({
                "transition": "none",
                "transform": "scaleX(0)",
            })

    def set_progress_color(self, color: str) -> None:
        """
        Set the filled progress indicator color.

        Args:
            color: CSS color value.
        """
        self._progress_bar.bg_color = color

    def set_track_color(self, color: str) -> None:
        """
        Set the progress track/background color.

        Args:
            color: CSS color value.
        """
        self.bg_color = color

    def set_fade_tip(self, enabled: bool) -> None:
        """
        Toggle the soft fade at the leading edge of the progress fill.

        Args:
            enabled: Whether the fade should be applied.
        """
        self._progress_bar.style.update({
            "-webkit-mask-image": self.FADE_MASK if enabled else "none",
            "mask-image": self.FADE_MASK if enabled else "none",
        })
