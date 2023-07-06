[TOC]

# Introduction

## Graphics Areas

 major areas of computer graphics:

- **Modeling** deals with the mathematical speciﬁcation of shape and appearance properties in a way that can be stored on the computer.
- **Rendering** is a term inherited from art and deals with the creation of shaded images from 3D computer models.
- **Animation** is a technique to create an illusion of motion through sequences of images.  Animation uses modeling and rendering but adds the key issue of movement over time, which is not usually dealt with in basic modeling and rendering.

 related areas include the following:

- **User interaction** deals with the interface between input devices such as mice and tablets, the application, feedback to the user in imagery, and other sensory feedback. 

- **Virtual reality** attempts to immerse the user into a 3D virtual world.
- **Visualization**  attempts to give users insight into complex information via visual display. Often there are graphic issues to be addressed in a visualization problem.
- **Image processing** deals with the manipulation of 2D images and is used in both the ﬁelds of graphics and vision.
- **3D scanning** uses range-ﬁnding technology to create measured 3D models.
- **Computational photography**  is the use of computer graphics, computer vision, and image processing methods to enable new ways of photographically capturing objects, scenes, and environments.



## Graphics Pipeline

Every desktop computer today has a powerful 3D **graphics pipeline**. This is a special software/hardware subsystem that efﬁciently draws 3D primitives in perspective. Usually these systems are optimized for processing 3D triangles with shared vertices.

The basic operations in the pipeline map the 3D vertex locations to 2D screen positions and shade the triangles so that they both look realistic and appear in proper back-to-front order.

Although drawing the triangles in valid back-to-front order was once the most important research issue in computer graphics, it is now almost always solved using the **z-buffer**, which uses a special memory buffer to solve the problem in a brute-force manner.

It turns out that the geometric manipulation used in the graphics pipeline can be accomplished almost entirely in a 4D coordinate space composed of three traditional geometric coordinates and a fourth **homogeneous** coordinate that helps with perspective viewing. 

These 4D coordinates are manipulated using 4 × 4 matrices and 4-vectors. The graphics pipeline, therefore, contains much machinery for efﬁciently processing and composing such matrices and vectors.

The speed at which images can be generated depends strongly on the number of triangles being drawn.

In addition, if the model is viewed in the distance, fewer triangles are needed than when the model is viewed from a closer distance. This suggests that it is useful to represent a model with a varying **level of detail** (LOD).

## Numerical Issues

Almost all modern computers conform to the IEEE **ﬂoating-point standard** (IEEE Standards Association, 1985).

Three “special” values for real numbers in IEEE ﬂoating-point:

1. **Infinity($\infty $)**. This is a valid number that is larger than all other valid numbers.
2. **Minus infinity($-\infty $)**. This is a valid number that is smaller than all other valid numbers.
3. **Not a number(NaN)**. This is an invalid number that arises from an operation with undefined consequences, such as zero divided zero.

> IEEE ﬂoating-point has two representations for zero, one that is treated as positive and one that is treated as negative. The distinction between –0 and +0 only occasionally matters, but it is worth keeping in mind for those occasions when it does.

Speciﬁcally, for any positive real number a, the following rules involving division by inﬁnite values hold:
$$
+a / (+ \infty) = +0 \\
-a / (+ \infty) = -0 \\
+a / (- \infty) = -0 \\
-a / (- \infty) = +0
$$
Other operations involving inﬁnite values behave the way one would expect. Again for positive a, the behavior is as follows:
$$
\infty + \infty = + \infty \\
\infty - \infty = NaN \\
\infty \times \infty = \infty \\
\infty / \infty = NaN \\
\infty / a = \infty \\
\infty / 0 = \infty \\
0 / 0 = NaN \\
$$
The rules in a Boolean expression involving inﬁnite values are as expected:

1. All ﬁnite valid numbers are less than $+ \infty $
2. All ﬁnite valid numbers are greater than $-\infty$
3. $- \infty$ is less than $+ \infty$

The rules involving expressions that have NaN values are simple:

1. Any arithmetic expression that includes NaN results in NaN.
2. Any Boolean expression involving NaN is false.

for any positive real number a, the following rules involving division by zero values hold:
$$
+a / +0 = +\infty \\
-a / +0 = -\infty \\
$$

## Efficiency

There are no magic rules for making code more efﬁcient. Efﬁciency is achieved through careful tradeoffs, and these tradeoffs are different for different architectures.

> However, for the foreseeable future, a good heuristic is that programmers should pay more attention to **memory access patterns** than to **operation counts**. This is the opposite of the best heuristic of two decades ago. This switch has occurred because the speed of memory has not kept pace with the speed of processors. Since that trend continues, the importance of limited and coherent memory access for optimization should only increase.

A reasonable approach to making code fast is to proceed in the following order, taking only those steps which are needed:

1. Write the code in the most straightforward way possible. Compute intermediate results as needed on the ﬂy rather than storing them.
2.  Compile in optimized mode.
3.  Use whatever proﬁling tools exist to ﬁnd critical bottlenecks.
4.  Examine data structures to look for ways to improve locality. If possible, make data unit sizes match the cache/page size on the target architecture. 
5. If proﬁling reveals bottlenecks in numeric computations, examine the assembly code generated by the compiler for missed efﬁciencies. Rewrite source code to solve any problems you ﬁnd.

## Designing and Coding Graphics Programs

### Class Design

A key part of any graphics program is to have good classes or routines for geometric entities such as vectors and matrices, as well as graphics entities such as RGB colors and images. These routines should be made as clean and efﬁcient as possible.

This implies that some basic classes to be written include:

- **vector2**  A 2D vector class that stores an x- and y-component. It should store these components in a length-2 array so that an indexing operator can be well supported. You should also include operations for vector addition, vector subtraction, dot product, cross product, scalar multiplication, and scalar division.
-  **vector3**. A 3D vector class analogous to vector2.
-  **hvector**. A homogeneous vector with four components.
-  **rgb**. An RGB color that stores three components. You should also include operations for RGB addition, RGB subtraction, RGB multiplication, scalar multiplication, and scalar division.
- **transform**. A 4 × 4 matrix for transformations. You should include a matrix multiply and member functions to apply to locations, directions, and surface normal vectors.
- **image**. A 2D array of RGB pixels with an output operation.

### Float vs. Double

Modern architecture suggests that keeping memory use down and maintaining coherent memory access are the keys to efﬁciency. This suggests using single precision data. However, avoiding numerical problems suggests using double precision arithmetic. The tradeoffs depend on the program, but it is nice to have a default in your class deﬁnitions.

### Debugging Graphics Programs

#### The Scientific Method

we create an image and observe what is wrong with it. Then, we develop a hypothesis(假设) about what is causing the problem and test it.

#### Images as Coded Debugging Output

In many cases, the easiest channel by which to get debugging information out of a graphics program is the output image itself. 

If you want to know the value of some variable for part of a computation that runs for every pixel, you can just modify your program temporarily to copy that value directly to the output image and skip the rest of the calculations that would normally be done. 

#### Using a Debugger

A useful approach is to “set a trap” for the bug.

- First, make sure your program is deterministic—run it in a single thread and make sure that all random numbers are computed from ﬁxed seeds. 
- Then, ﬁnd out which pixel or triangle is exhibiting the bug and add a statement before the code you suspect is incorrect that will be executed only for the suspect case. 

#### Data Visualization for Debugging

make good plots and illustrations for yourself to understand what the data means.