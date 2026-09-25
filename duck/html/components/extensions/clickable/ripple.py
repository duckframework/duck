"""
Ripple extension for HTML components.

Gives a container component a Material-style press ripple: a translucent circle
that grows from the pointer position and fades out once released, for a native
touch feel.

**Usage example:**

```py
from duck.html.components.button import Button
from duck.html.components.extensions.clickable import RippleExtension

class RippleButton(RippleExtension, Button):
    pass

btn = RippleButton(text="Save", ripple_color="rgba(255, 255, 255, 0.4)")
```

**Keyword arguments:**

- `ripple_color` (str): CSS color of the ripple. Defaults to the text color.
- `ripple_duration` (int): Time in milliseconds the ripple takes to fully grow.
- `ripple_centered` (bool): Start every ripple from the center (e.g. icon buttons).

**Notes:**

- The component must be able to contain children, so void elements are rejected.
- The host gets `position: relative` and `overflow: hidden` unless you set them.
- No ripple is shown once the press turns into a scroll or swipe.
- The ripple never calls `preventDefault` or `stopPropagation`, and its DOM write
  is deferred a couple of frames, so the underlying component's own click
  listeners keep firing normally.
"""

from json import dumps
from string import Template

from duck.html.components.script import Script
from duck.html.components.extensions import Extension, ExtensionError


# Identifiers shared between the Python and browser sides
HOST_CLASS = "duck-ripple"
WAVE_CLASS = "duck-ripple-wave"
STYLE_ELEMENT_ID = "duck-ripple-style"
READY_FLAG = "duckRippleReady"
COLOR_VARIABLE = "--duck-ripple-color"
DURATION_ATTRIBUTE = "data-ripple-duration"
CENTERED_ATTRIBUTE = "data-ripple-centered"

# Ripple look and timing
DEFAULT_DURATION_MS = 550
FADE_DURATION_MS = 300
WAVE_OPACITY = 0.25
EXPAND_EASING = "cubic-bezier(0.4, 0, 0.2, 1)"

# Gesture detection: how far a pointer may move before a press counts as a
# scroll or swipe instead, in CSS pixels
SCROLL_MOVE_THRESHOLD_PX = 10

# Inline styles a host needs, applied only when the component has not set them
HOST_STYLE_DEFAULTS = {
    "position": "relative",
    "overflow": "hidden",
    "-webkit-tap-highlight-color": "transparent",
}

# Values substituted into the style and script templates below
TEMPLATE_VALUES = {
    "host_class": HOST_CLASS,
    "wave_class": WAVE_CLASS,
    "style_id": STYLE_ELEMENT_ID,
    "ready_flag": READY_FLAG,
    "color_variable": COLOR_VARIABLE,
    "duration_attribute": DURATION_ATTRIBUTE,
    "centered_attribute": CENTERED_ATTRIBUTE,
    "wave_opacity": WAVE_OPACITY,
    "easing": EXPAND_EASING,
    "fade_ms": FADE_DURATION_MS,
    "move_threshold": SCROLL_MOVE_THRESHOLD_PX,
}

# Styles for the wave element that the script creates on every press
STYLE_TEMPLATE = """
.$wave_class {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  background: var($color_variable, currentColor);
  opacity: $wave_opacity;
  transform: scale(0);
  will-change: transform, opacity;
}
"""

# Script that installs the styles and one delegated pointer handler per page
SCRIPT_TEMPLATE = """
(function () {
  if (window.$ready_flag) {
    return;
  }
  window.$ready_flag = true;

  // Inject the shared wave styles once per page
  var style = document.createElement("style");
  style.id = "$style_id";
  style.textContent = $style;
  document.head.appendChild(style);

  // Resolve once the same pointer is released or its gesture is cancelled
  function whenReleased(pointerId, signal) {
    return new Promise(function (resolve) {
      var done = function (event) {
        if (event.pointerId === pointerId) {
          resolve();
        }
      };
      document.addEventListener("pointerup", done, { signal: signal });
      document.addEventListener("pointercancel", done, { signal: signal });
    });
  }

  // Create a wave centered on the press point, sized to reach the farthest corner
  function spawnWave(host, originEvent) {
    var box = host.getBoundingClientRect();
    var centered = host.getAttribute("$centered_attribute") === "true";
    var x = originEvent.clientX - box.left - host.clientLeft;
    var y = originEvent.clientY - box.top - host.clientTop;
    if (centered) {
      x = host.clientWidth / 2;
      y = host.clientHeight / 2;
    }
    var radius = Math.hypot(
      Math.max(x, host.clientWidth - x),
      Math.max(y, host.clientHeight - y)
    );

    var wave = document.createElement("span");
    wave.className = "$wave_class";
    wave.style.width = wave.style.height = radius * 2 + "px";
    wave.style.left = x - radius + "px";
    wave.style.top = y - radius + "px";
    host.appendChild(wave);
    return wave;
  }

  // Grow the wave, then fade it out once fully grown and released
  function animateWave(wave, duration, released) {
    var grow = wave.animate(
      { transform: ["scale(0)", "scale(1)"] },
      { duration: duration, easing: "$easing", fill: "forwards" }
    );
    var remove = function () {
      wave.remove();
    };

    Promise.all([grow.finished, released])
      .then(function () {
        return wave.animate(
          { opacity: 0 },
          { duration: $fade_ms, fill: "forwards" }
        ).finished;
      })
      .then(remove, remove);
  }

  // Track one press from pointerdown, deciding late whether it was a tap
  function trackPress(host, originEvent) {
    var pointerId = originEvent.pointerId;
    var startX = originEvent.clientX;
    var startY = originEvent.clientY;
    var stop = new AbortController();
    var wave = null;
    var cancelled = false;

    // Drop the pending or growing wave without touching the click itself
    function cancel() {
      if (cancelled) {
        return;
      }
      cancelled = true;
      stop.abort();
      if (wave) {
        wave.remove();
      }
    }

    // Treat enough movement on this pointer as a scroll or swipe, not a tap
    document.addEventListener(
      "pointermove",
      function (moveEvent) {
        if (moveEvent.pointerId !== pointerId) {
          return;
        }
        var dx = moveEvent.clientX - startX;
        var dy = moveEvent.clientY - startY;
        if (Math.hypot(dx, dy) > $move_threshold) {
          cancel();
        }
      },
      { signal: stop.signal, passive: true }
    );

    // Treat any scroll, including inside a nested scroller, the same way
    window.addEventListener("scroll", cancel, {
      signal: stop.signal,
      passive: true,
      capture: true,
    });

    var released = whenReleased(pointerId, stop.signal);

    // Wait two frames before writing to the DOM so this never lands inside
    // the browser's own handling of the press, which can otherwise cancel
    // the click it would have produced
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        if (cancelled) {
          return;
        }
        wave = spawnWave(host, originEvent);
        animateWave(
          wave,
          Number(host.getAttribute("$duration_attribute")),
          released
        );
      });
    });
  }

  // Handle presses for every ripple host, including ones added later.
  // Never calls preventDefault or stopPropagation, so scrolling and the
  // host's own click handling both continue exactly as if this never ran.
  document.addEventListener(
    "pointerdown",
    function (event) {
      // Ignore secondary mouse buttons
      if (event.pointerType === "mouse" && event.button !== 0) {
        return;
      }

      // Find the closest enabled ripple host
      var host = event.target.closest(".$host_class");
      if (!host || host.matches(":disabled, [aria-disabled='true']")) {
        return;
      }

      trackPress(host, event);
    },
    { passive: true }
  );
})();
"""

# Render the templates once, at import time
RIPPLE_STYLE = Template(STYLE_TEMPLATE).substitute(TEMPLATE_VALUES)
RIPPLE_SCRIPT = Template(SCRIPT_TEMPLATE).substitute(
    TEMPLATE_VALUES,
    style=dumps(RIPPLE_STYLE),
)


class RippleExtension(Extension):
    """
    Extension adding a native-style press ripple to container components.

    The component only carries a class, a few attributes and one small script.
    The script installs the wave styles and a single delegated pointer handler
    the first time it runs, so ripples also work on components added later.
    """

    def apply_extension(self) -> None:
        """
        Apply the ripple effect to the component.

        Marks the component as a ripple host, applies the ripple options from
        `kwargs` and attaches the script that drives the animation.
        """
        super().apply_extension()
        
        # Prepare the host box and the ripple options
        self.apply_ripple_extension_host_style()
        self.apply_ripple_extension_options()
        
    def load(self):
        """
        Load component, modified by RippleExtension.
        """
        # Only add script after component has been loaded - by default, apply_extension is called before load()
        super().load()
        
        # Add script to component tree
        self.add_ripple_extension_script()
        
    def add_ripple_extension_script(self):
        """
        Adds ripple extension script to component or component's parent.
        """
        # Import lazily to avoid circular imports, like the other extensions
        from duck.html.components import InnerComponent
        from duck.html.components.script import Script
        
        if not getattr(self, "_ripple_extension_script_added", False):
            target_container = self

            # Ripples are rendered as child elements, so the target must be an
            # InnerComponent capable of containing children.
            if not isinstance(target_container, InnerComponent):
                if target_container.parent is not None:
                    target_container = target_container.parent
                    
                if not isinstance(target_container, InnerComponent):
                    raise ExtensionError(
                        f"Ripple requires an InnerComponent, but {type(self).__name__} "
                        "cannot contain children. Use an InnerComponent or exclude the "
                        "Ripple extension with exclude_extensions=[RippleExtension]."
                    )
        
            script = Script(inner_html=RIPPLE_SCRIPT)
    
            # Attach the shared script that installs the styles and pointer handler.
            # This avoids the component error raised when children and inner_html
            # are both populated.
            if target_container.inner_html:
                target_container.inner_html += script.render()
            
            else:
                target_container.add_child(script)
            
            # Update flag
            self._ripple_extension_script_added = True
        
    def apply_ripple_extension_host_style(self) -> None:
        """
        Mark the component as a ripple host and give it a clipping box.

        The wave is absolutely positioned and must be clipped by the host, so the
        host needs a positioned box with hidden overflow. Values the component has
        already set are kept.
        """
        # Add the host class without dropping existing classes
        existing_classes = self.props.get("class", "")
        self.klass = f"{existing_classes} {HOST_CLASS}".strip()

        # Apply the box styles unless the component already defines them
        for property_name, value in HOST_STYLE_DEFAULTS.items():
            if property_name not in self.style:
                self.style[property_name] = value

    def apply_ripple_extension_options(self) -> None:
        """
        Apply the ripple options from `kwargs`.

        The color goes through a CSS variable read by the wave styles, while the
        duration and origin are attributes read by the script on every press.
        """
        # Apply the ripple color when one is provided
        color = self.kwargs.get("ripple_color")

        if color is not None:
            self.style[COLOR_VARIABLE] = color

        # Apply the growth time, falling back to the default
        self.props[DURATION_ATTRIBUTE] = str(
            self.kwargs.get("ripple_duration", DEFAULT_DURATION_MS)
        )

        # Apply the centered origin when requested
        if self.kwargs.get("ripple_centered", False):
            self.props[CENTERED_ATTRIBUTE] = "true"
