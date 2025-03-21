# About the Examples

The VTK source distribution includes a sizeable number of [examples](https://gitlab.kitware.com/vtk/vtk/blob/master/Examples).
The goal of the VTK examples is to illustrate specific VTK concepts in a consistent and simple format. Some have been there since the inception of the toolkit. These examples have been subject to peer review and revision over the years. However, these examples only cover a small part of the capabilities of VTK.

Hundreds of tests are distributed with the toolkit source. The tests reside in ''Kit''/Testing directories (for example, Filters/Points/Testing) in the source distribution. However, these tests are meant to exercise the toolkit rather than illustrate how to use it. For the most part, the tests are not good educational resources.

We are now using [github pages](https://pages.github.com/) to provide examples that will help both new and experienced VTK users. The examples can be used to find examples that answer questions like, "How do I extract normals from a filter's output?", "How do I generate models from segmented data?", and "How do I compute the area of a triangle?", just to name a few.

Over time we hope that the examples will answer many of the users' questions. Some questions won't have a solution in the current example repertoire. For those questions, we encourage the user to create a simple example that illustrates either a dilemma or a new solution.

## Available Languages

Examples are available for the following programming languages:

* [C++](Cxx/)
* [The new Python interface for VTK](PythonicAPI/)
* [Python](Python/)
* [Java](Java/)
* [C#](CSharp/)
* [js](JavaScript/)

The above examples demonstrate how to *use* VTK functionalities. There are also examples specifically to demonstrate how to write code as a VTK filter using VTK techniques. This is helpful so that your custom code can be called in a fashion that other people are already familiar with. It is also necessary if you plan to contribute your classes to VTK.

### Test Data

Many of these examples require data in order to run. For most of the Python and C++ examples the required files will be specified in the source code or the description.

If you have checked out the **vtk-examples** repository, these data files are found in the folder `src/Testing/Data`. Otherwise individual data files can be downloaded from [here](https://gitlab.kitware.com/vtk/vtk-examples/-/tree/master/src/Testing/Data?ref_type=heads).

Be aware:

* For some examples, one or more subfolders in `src/Testing/Data` are needed. In this case you must download each individual file in the subfolder or, more simply, just checkout the whole repository.
* If there is no indication of the names of the data files and there is a C++ example then look in the relevant `CMakeLists.txt` file starting from `src/Cxx` or [here](https://gitlab.kitware.com/vtk/vtk-examples/-/tree/master/src/Cxx?ref_type=heads)

## Trame

* [Trame](Trame/)

These examples consist of tarfiles that you download, set up and run.

## Information about the VTK Examples

* [Users](Instructions/ForUsers/): If you just want to use the VTK Examples, this is the place for you. You will learn how to search for examples, build a few examples and build all of the examples.
* [Developers](Instructions/ForDevelopers/): If you want to contribute examples, this section explains everything you need to know. You will learn how to add a new example and the guidelines for writing an example.
* [Adminstrators](Instructions/ForAdministrators/): This section is for a VTK Example Administrators or people want to learn more about the process. You will learn how the VTK Examples repository is organized, how the repository is synced to the repository and how to add new topics, tests and regression baselines.

## How can I help?

This project has grown to be very large. We are always looking for people to help the cause. You can help by:

* Adding new examples (see procedure [here](Instructions/ForDevelopers/))
* Proof reading existing examples, for correctness, style, and clarity.
* Add comments to existing examples where they are unclear.
