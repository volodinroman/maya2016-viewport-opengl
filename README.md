# ViewportPainter class

This class is an example of a user defined interactive tool, that simplifies a viewport callbacks creation process for drawing OpenGL primitives and filtering user actions.

####How it works:
ViewportPainter class contains two methods that are responsible for initialization and uninitialization of a viewport redrawing callbacks as well as eventFilters for Maya main window. 

When a viewport callback is initialized it calls "Update" method for every refresh of the view, after the scene is drawn but before any 2d adornments are drawn.

To create your own interactive tool, you need to inherit ViewportPainter class and override "Update" method with your own actions and OpenGL drawing process. 

####Usage:
- download the project files and place them in MAYA_SCRIPT_PATH folder;
- use the next script to run the example

####Python
```
import example
example.main()
```
- The example creates a context where a user draws lines on a surface which will be converted into a lofted polygonal mesh.
- When you initialize an instance of "Example" class, press CTRL and then Left Mouse Button to start drawing curves on a surface. As soon as you release Left Mouse Button it will create a curve. Draw several curves and only then release CTRL key to get a lofted polyMesh.


