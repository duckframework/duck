"""
Progress bar component.
"""

from duck.html.components.theme import Theme
from duck.html.components.container import Container
from duck.html.components.script import Script


PROGRESS_BAR_SCRIPT = """
function updateProgressBar(progressBar, progress, autoHideWhenZero = true) {
  const progressBarInner = progressBar.querySelector('.progress-bar-inner');
  progress = Math.max(0, Math.min(100, progress));

  requestAnimationFrame(() => {
    if (!progressBarInner) return;

    if (progress > 0) {
      progressBar.style.display = 'block';

      // Flip display before opacity so the fade-in actually transitions
      requestAnimationFrame(() => {
        progressBar.style.opacity = '1';
      });

      progressBarInner.style.transform = `scaleX(${progress / 100})`;
    } else if (autoHideWhenZero) {
      hideProgressBar(progressBar);
    } else {
      progressBarInner.style.transform = 'scaleX(0)';
    }
  });
}

function hideProgressBar(progressBar) {
  const progressBarInner = progressBar.querySelector('.progress-bar-inner');

  const onFadeOut = (event) => {
    if (event.target !== progressBar || event.propertyName !== 'opacity') return;
    progressBar.style.display = 'none';
    progressBar.removeEventListener('transitionend', onFadeOut);
  };

  // Only hide from layout once the fade-out has actually finished
  progressBar.addEventListener('transitionend', onFadeOut);
  progressBar.style.opacity = '0';

  if (progressBarInner) {
    progressBarInner.style.transform = 'scaleX(0)';
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
            "border-radius": "999px",
            "overflow": "hidden",
            "display": "none",
            "opacity": "0",
            "transition": "opacity 0.2s ease",
            "border-radius": Theme.current.border_radius,
        })

        # Component children
        self._progress_bar = Container(
            klass="progress-bar-inner",
            bg_color=self.FILL_COLOR,
            style={
                "width": "100%",
                "height": "100%",
                "transform-origin": "left",
                "transform": "scaleX(0)",
                "will-change": "transform",
                "transition": "transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
                "border-radius": Theme.current.border_radius,
            },
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
        
        # Update progress style
        self._progress_bar.style.update({"transform": f"scaleX({progress / 100})"})

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
