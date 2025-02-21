# ViewportPainter Class

The `ViewportPainter` class is an example of a user-defined interactive tool that simplifies the process of creating viewport callbacks for drawing OpenGL primitives and filtering user actions.

[![Maya Interactive Tools Demo](https://i.gyazo.com/2beaf7ddd6cb7acaf5181e58efc610db.png)](https://vimeo.com/168770171 "Maya Interactive Tools Demo - Click to Watch!")

## How It Works
The `ViewportPainter` class contains methods responsible for initializing and uninitializing viewport redrawing callbacks, as well as installing `eventFilters` for the Maya main window.

When a viewport callback is initialized, it calls the `Update` method during every viewport refresh—after the scene is drawn but before any 2D adornments are rendered.

To create a custom interactive tool, inherit from the `ViewportPainter` class and override the `Update` method with custom actions and OpenGL drawing processes.

## Usage
1. Download the project files and place them in the `MAYA_SCRIPT_PATH` folder.
2. Use the following script to run the example:

### Python
```python
import example
example.main()
```

### Example Functionality
- The example creates a context where the user can draw lines on a surface, which are then converted into a lofted polygonal mesh.
- When an instance of the `Example` class is initialized:
  - Hold `CTRL` and press the **Left Mouse Button** to start drawing curves on a surface.
  - Release the **Left Mouse Button** to create a curve.
  - Draw multiple curves and release the `CTRL` key to generate a lofted polygonal mesh.

