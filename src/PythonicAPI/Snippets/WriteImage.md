### Description

Given a filename, render window and optionally a rgba value, take a screenshot of the render window and write it to a file. The extension of the filename determines what writer to use.

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


def write_image(file_name, ren_win, rgba=True):
    """
    Write the render window view to an image file.

    Image types supported are:
     BMP, JPEG, PNM, PNG, PostScript, TIFF.
    The default parameters are used for all writers, change as needed.

    :param file_name: The file name, if no extension then PNG is assumed.
    :param ren_win: The render window.
    :param rgba: Used to set the buffer type.
    :return:
    """

    if file_name:
        valid_suffixes = ['.bmp', '.jpg', '.png', '.pnm', '.ps', '.tiff']
        # Select the writer to use.
        parent = Path(file_name).resolve().parent
        path = Path(parent) / file_name
        if path.suffix:
            ext = path.suffix.lower()
        else:
            ext = '.png'
            path = Path(str(path)).with_suffix(ext)
        if path.suffix not in valid_suffixes:
            print(f'No writer for this file suffix: {ext}')
            return

        if ext == '.ps':
            rgba = False

        wtif = vtkWindowToImageFilter(input=ren_win, scale=1)
        if rgba:
            wtif.SetInputBufferTypeToRGBA()
        else:
            wtif.SetInputBufferTypeToRGB()
            # Read from the front buffer.
            wtif.ReadFrontBufferOff()
            wtif.update()

        if ext == '.bmp':
            writer = vtkBMPWriter(file_name=path)
        elif ext == '.jpg':
            writer = vtkJPEGWriter(file_name=path)
        elif ext == '.pnm':
            writer = vtkPNMWriter(file_name=path)
        elif ext == '.ps':
            writer = vtkPostScriptWriter(file_name=path)
        elif ext == '.tiff':
            writer = vtkTIFFWriter(file_name=path)
        else:
            writer = vtkPNGWriter(file_name=path)
            
        wtif >> writer
        writer.Write()
    else:
        raise RuntimeError('Need a filename.')

```

### Usage

``` Python

  write_image(file_name, ren_win, rgba=False)

```
