### Description

A callback that gives you the camera position and focal point.

To use the snippet, click the *Copy to clipboard* at the upper right of the code blocks.

### Implementation

``` Python

def camera_modified_callback(caller, event):
    """
     Used to estimate positions similar to the book illustrations.
    :param caller:
    :param event:
    :return:
    """
    print(caller.class_name, "modified")
    # Print the interesting stuff.
    res = f'\tcamera = ren.active_camera\n'
    res += f'\tcamera.position = ({", ".join(map("{0:0.6f}".format, caller.position))})\n'
    res += f'\tcamera.focal_point = ({", ".join(map("{0:0.6f}".format, caller.focal_point))})\n'
    res += f'\tcamera.view_up = ({", ".join(map("{0:0.6f}".format, caller.view_up))})\n'
    res += f'\tcamera.distance = ({"{0:0.6f}".format(caller.GetDistance())})\n'
    res += f'\tcamera.clipping_range = ({", ".join(map("{0:0.6f}".format, caller.clipping_range))})\n'
    print(res)

```

### Usage

```python
    ren_win.Render()
    ren.active_camera.AddObserver('ModifiedEvent', camera_modified_callback)
```

Once you have the output, replace the `ren.GetActiveCamera().AddObserver...` line with the output data.
