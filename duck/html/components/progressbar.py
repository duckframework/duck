"""
Progress bar component.
"""
from duck.html.components.container import Container
from duck.html.components.script import Script


class ProgressBar(Container):
    """
    A modern loading bar component with interactive JavaScript toggles and Python toggles.

    Attributes:
        progress_bar (Container): The progress bar element.
    """
    
    def on_create(self):
        """
        Initializes the loading bar component.

        Sets up the styles and adds the progress bar element.
        """
        super().on_create()
        
        # Set up the styles for the loading bar
        self.bg_color = "#f0f0f0"
        self.style["width"] = "100%"
        self.style["height"] = "3px"
        self.style["border-radius"] = "3px"
        self.style["overflow"] = "hidden"
        self.style["display"] = "none"
        self.style["transition"] = "display 0.1s ease"
        
        # Create a progress bar      
        self._progress_bar = Container(bg_color="#4CAF50", id="progress-bar-inner")
        self._progress_bar.style["width"] = "100%"
        self._progress_bar.style["height"] = "100%"
        self._progress_bar.style["transition"] = "transform 0.1s ease"
        self._progress_bar.style["will-change"] = "transform"
        self._progress_bar.style["transform-origin"] = "left"
        
        # Add the progress bar element to the loading bar
        self.add_child(self._progress_bar)

        # Add a JavaScript function to toggle the loading bar
        self.script = Script(
            inner_html="""
            function updateProgressBar(progressBar, progress, autoHideWhenZero = true) {
              // Clamp progress value to [0, 100] for safety
              progress = Math.max(0, Math.min(100, progress));
              
              // Find the inner progress bar element by id or class
              const progressBarInner =
                progressBar.querySelector('#progress-bar-inner') ||
                progressBar.querySelector('.progress-bar-inner');
            
              // Schedule updates for the next animation frame for smooth UI
              requestAnimationFrame(() => {
                if (!progressBarInner) return;
            
                if (progress > 0) {
                  // Show the progress bar if progress is nonzero
                  progressBar.style.display = 'inline-block';
                  // Animate the width (scaleX) to represent progress
                  progressBarInner.style.transform = `scaleX(${progress / 100})`;
                } else if (autoHideWhenZero) {
                  // Hide the bar and reset the inner transform if enabled
                  hideProgressBar(progressBar, false);
                } else {
                  // If not hiding, reset inner bar to zero width
                  progressBarInner.style.transform = 'scaleX(0)';
                }
              });
            }
            
            /**
             * Hides the progress bar and resets inner bar transform.
             * Useful for manual control or after navigation/transition.
             * @param {HTMLElement} progressBar - The outer progress bar element.
             * @param {boolean} nextAnimationFrame - Whether to run in the next animation frame. Defaults to true.
             */
            function hideProgressBar(progressBar, nextAnimationFrame = true) {
              // Find inner bar element
              const progressBarInner =
                progressBar.querySelector('#progress-bar-inner') ||
                progressBar.querySelector('.progress-bar-inner');
            
              if (nextAnimationFrame) {
                requestAnimationFrame(() => {
                  // Hide the outer bar
                  progressBar.style.display = 'none';
                  
                  // Reset inner bar transform for future use
                  if (progressBarInner) {
                    progressBarInner.style.transform = 'scaleX(0)';
                  }
                });
              }
              else {
                // Hide the outer bar
                progressBar.style.display = 'none';
                
                // Reset inner bar transform for future use
                if (progressBarInner) {
                  progressBarInner.style.transform = 'scaleX(0)';
                }
              }
            }
            """
        )
        self.add_child(self.script)

    def update_progress(self, progress: int):
        """
        Updates the progress of the loading bar.

        Args:
            progress (int): The progress percentage.
        """
        assert isinstance(progress, int), "Progress must be an integer."
        
        if progress > 0 and self.style.get("display") == "none":
            self.style["display"] = "inline-block"
        elif progress <= 0:
          self.style["display"] = "none"
          
        # Update the progress bar width
        self._progress_bar.style["width"] = f"{progress}%"
