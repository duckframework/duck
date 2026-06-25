"""
Progress bar component.
"""
from duck.html.components.container import Container
from duck.html.components.script import Script


PROGRESS_BAR_SCRIPT = """
function updateProgressBar(progressBar, progress, autoHideWhenZero = true) {{
  const progressBarInner = progressBar.querySelector('.progress-bar-inner');
  progress = Math.max(0, Math.min(100, progress));
  
  requestAnimationFrame(() => {{
    if (!progressBarInner) return;

    if (progress > 0) {{
      progressBar.style.display = 'inline-block';
      progressBarInner.style.transform = `scaleX(${{progress / 100}})`;
    }} else if (autoHideWhenZero) {{
      hideProgressBar(progressBar, false);
    }} else {{
      progressBarInner.style.transform = 'scaleX(0)';
    }}
  }});
}}

function hideProgressBar(progressBar, nextAnimationFrame = true) {{
  const progressBarInner = progressBar.querySelector('.progress-bar-inner');

  const applyHiddenState = () => {{
    progressBar.style.display = 'none';

    if (progressBarInner) {{
      progressBarInner.style.transform = 'scaleX(0)';
    }}
  }};

  if (nextAnimationFrame) {{
    requestAnimationFrame(applyHiddenState);
    return;
  }}

  applyHiddenState();
}}
"""


class ProgressBar(Container):
    """
    Modern loading bar with JavaScript and Python update helpers.
    """
    
    def on_create(self) -> None:
        """
        Initialize and compose the progress bar.
        """
        super().on_create()

        # Component setup
        self.bg_color = "rgba(0, 0, 0, .1)"
        self.props.setdefault("id", "progress-bar")
        self.style.update({
            "width": "100%",
            "height": "3px",
            "border-radius": "3px",
            "overflow": "hidden",
            "display": "none",
            "transition": "display 0.1s ease",
        })

        # Component children
        self._progress_bar = Container(
            klass="progress-bar-inner",
            bg_color="#F5C842",
            style={
                "width": "100%",
                "height": "100%",
                "transition": "transform 0.1s ease",
                "will-change": "transform",
                "transform-origin": "left",
                "transform": "scaleX(0)",
            },
        )

        self.add_children([
            self._progress_bar,
            Script(inner_html=PROGRESS_BAR_SCRIPT.format(progress_bar_id=self.id)),
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

        self.style["display"] = "inline-block" if progress > 0 else "none"
        self._progress_bar.style["transform"] = f"scaleX({progress / 100})"

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
