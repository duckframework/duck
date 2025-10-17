"""
Video HTML Component.

This module provides a customizable `Video` component for embedding video content into HTML.

**Arguments:**
- **source (str, required)**:  
  The source URL of the video. This is the path to the video file or external URL.
  
- **alt (str, optional)**:  
  A text description for the video. It serves as an alternative when the video cannot be played.
  
- **width (str, optional)**:  
  Specifies the width of the video element in pixels (or percentage).
  
- **height (str, optional)**:  
  Specifies the height of the video element in pixels (or percentage).
  
- **autoplay (bool, optional)**:  
  Indicates if the video should automatically play when loaded. Defaults to `False`.
  
- **loop (bool, optional)**:  
  Specifies if the video should loop when finished. Defaults to `False`.
  
- **muted (bool, optional)**:  
  Determines whether the video should be muted by default. Defaults to `False`.
  
- **playsinline (bool, optional)**:  
  Allows the video to play inline on mobile devices (i.e., not in full-screen mode). Defaults to `False`.

**Example Usage:**

```py
video = Video(
    source="path/to/video.mp4",
    alt="A sample video",
    width="800px",
    height="450px",
    autoplay=True,
    loop=True,
    muted=False,
    playsinline=True
)
component.add_child(video)
"""
from duck.html.components import InnerComponent


class Video(InnerComponent):
    """
    HTML Video component.
    
    Args:
        source (str): Video source url
        alt (str): Video alternative text
        width (str): Video width
        height (str): Video height
        autoplay (bool): Whether to autoplay video
        loop (bool): Whether to loop video
        muted (bool): Whether to mute video
        playsinline (bool): Whether to turn on playsinline
        
    """
    def get_element(self):
        return "video"
        
    def on_create(self):
        super().on_create()
        self.props.setdefault("type", "video/mp4")
        
        if "source" in self.kwargs:
            self.props["src"] = self.kwargs.get("source")
        
        if "alt" in self.kwargs:
            self.props["alt"] = self.kwargs.get("alt")
        
        if "width" in self.kwargs:
            self.style["width"] = self.kwargs.get("width")
            
        if "height" in self.kwargs:
            self.style["height"] = self.kwargs.get("height", '')
        
        if self.kwargs.get("autoplay"):
            self.props["autoplay"] = "true"
        
        if self.kwargs.get("loop"):
            self.props["loop"] = "true"
            
        if self.kwargs.get("muted"):
            self.props["muted"] = "true"
        
        if self.kwargs.get("playsinline"):
            self.props["playsinline"] = "true"
