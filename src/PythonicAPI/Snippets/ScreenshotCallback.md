
### Description

Write a screenshot to a file.

**Note**: The key to write the screenshot to the file is "**k**", change it to whatever you want. 

To use the snippet, click the *Copy to clipboard* at the upper right of the code blocks.

### Implementation

``` Python

# from pathlib import Path
# 
# from vtkmodules.vtkIOImage import (
#     vtkBMPWriter,
#     vtkJPEGWriter,
#     vtkPNGWriter,
#     vtkPNMWriter,
#     vtkPostScriptWriter,
#     vtkTIFFWriter
# )
# from vtkmodules.vtkRenderingCore import vtkWindowToImageFilter


class ScreenshotCallback:
    def __init__(self, caller, file_name, image_quality=1, rgba=True):
        """
        Set the parameters for writing the render window view to an image file.

        Image types supported are:
         BMP, JPEG, PNM, PNG, PostScript, TIFF.

        :param caller: The caller for the callback.
        :param file_name: The image file name.
        :param image_quality: The image quality.
        :param rgba: The buffer type, (if true, there is no background in the screenshot).
        """
        self.caller = caller
        self.image_quality = image_quality
        self.rgba = rgba
        if not file_name:
            self.path = None
            print('A file name is required.')
            return
        pth = Path(file_name).absolute()
        valid_suffixes = ['.bmp', '.jpg', '.jpeg', '.png', '.pnm', '.ps', '.tiff']
        if pth.suffix:
            ext = pth.suffix.lower()
        else:
            ext = '.png'
        if ext not in valid_suffixes:
            print(f'No writer for this file suffix: {ext}, using .png')
            ext = '.png'
        self.suffix = ext
        self.path = Path(str(pth)).with_suffix(ext)

    def __call__(self, caller, ev):
        if not self.path:
            print('A file name is required.')
            return
        # Save the screenshot.
        w2if = None
        if caller.GetKeyCode() == 'k':
            w2if = vtkWindowToImageFilter(input=caller.GetRenderWindow(),
                                          scale=(self.image_quality, self.image_quality),
                                          read_front_buffer=True)
            if self.rgba and self.suffix != '.ps':
                w2if.SetInputBufferTypeToRGBA()
            else:
                w2if.SetInputBufferTypeToRGB()
                # Do not read from the front buffer.
                w2if.ReadFrontBufferOff()

        if self.suffix == '.bmp':
            writer = vtkBMPWriter(file_name=self.path)
        elif self.suffix in ['.jpeg', '.jpg']:
            writer = vtkJPEGWriter(file_name=self.path)
        elif self.suffix == '.pnm':
            writer = vtkPNMWriter(file_name=self.path)
        elif self.suffix == '.ps':
            writer = vtkPostScriptWriter(file_name=self.path)
        elif self.suffix == '.tiff':
            writer = vtkTIFFWriter(file_name=self.path)
        else:
            writer = vtkPNGWriter(file_name=self.path)

        w2if >> writer
        writer.Write()
        print('Screenshot saved to:', self.path)
        
```


### Usage

Add these lines before you start the interactor (**iren**). 
``` Python

    screenshot_fn = 'SomeFileName.png'
    screenshot_cb = ScreenshotCallback(iren, screenshot_fn, 1, False)
    iren.AddObserver('KeyPressEvent', screenshot_cb)

```
