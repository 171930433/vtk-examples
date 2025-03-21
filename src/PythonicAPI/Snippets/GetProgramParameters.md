### Description

Get the program parameters.

This particular snippet requires a file name and an optional figure number.

To use the snippet, click the *Copy to clipboard* at the upper right of the code blocks.

### Implementation

``` Python

def get_program_parameters():
    import argparse
    description = 'What the program does.'
    epilogue = '''
        An expanded description of what the program does.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='A required filename.')
    parser.add_argument('figure', default=0, type=int, nargs='?', help='An optional figure number.')
    args = parser.parse_args()
    return args.filename, args.figure


```

### Typical usage

``` Python

file_name, figure = get_program_parameters()

```
