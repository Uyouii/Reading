# The Graphics Processing Unit

> The display is the computer
>
> ​		—— Jen-Hsun Huang

## Data-Parallel Architectures

Much of a GPU’s chip area is dedicated to a large set of processors, called **shader cores**, often numbering in the thousands.

The GPU is a stream processor, in which ordered sets of similar data are processed in turn. Because
of this similarity the GPU can process these data in a massively **parallel fashion**. 

The GPU is optimized for **throughput**, deﬁned as the maximum rate at which data can be processed. However, this rapid processing has a cost. With less chip area dedicated to cache memory and control logic, **latency** for each shader core is generally considerably higher than what a CPU processor encounters.

GPUs separate the instruction execution logic from the data. Called **single instruction, multiple data (SIMD)**. The advantage of SIMD is that considerably less silicon (and power) needs to be dedicated to processing data and switching, compared to using an individual logic and dispatch unit to run each program. 

#### Warp

in modern GPU terms, each pixel shader invocation for a fragment is called a **thread**. This type of thread is unlike a CPU thread. It consists of a bit of memory for the input values to the shader, along with any register space needed for the shader’s execution. 

Threads that use the same shader program are bundled into groups, called **warps** by NVIDIA and **wavefronts** by AMD. A warp/wavefront is scheduled for execution by some number GPU shader cores, anywhere from 8 to 64, using SIMD-processing. 

#### Occupancy

The shader program’s structure is an important characteristic that inﬂuences eﬃciency. A major factor is the amount of register use for each thread. The more registers needed by the shader program associated with each thread, the fewer threads, and thus the fewer warps, can be resident in the GPU. A shortage of warps can mean that a stall cannot be mitigated by swapping. 

Warps that are resident are said to be “in ﬂight,” and this number is called the **occupancy**. 

- High occupancy means that there are many warps available for processing, so that idle processors are less likely. 
- Low occupancy will often lead to poor performance.

The frequency of memory fetches also aﬀects how much latency hiding is needed.



Another factor aﬀecting overall eﬃciency is **dynamic branching**, caused by “if” statements and loops. 

if some threads, or even one thread, take the alternate path, then the warp must execute both branches, throwing away the results not needed by each particular thread. This problem is called **thread divergence**, where a few threads may need to execute a loop iteration or perform an “if” path that the other threads in the warp do not, leaving them idle during this time.



![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/Simpli%EF%AC%81ed%20shader%20execution%20example.PNG)

> Simpliﬁed shader execution example. A triangle’s fragments, called threads, are gathered into warps. Each warp is shown as four threads but have 32 threads in reality. The shader program to be executed is ﬁve instructions long. The set of four GPU shader processors executes these instructions for the ﬁrst warp until a stall condition is detected on the “txr” command, which needs time to fetch its data. The second warp is swapped in and the shader program’s ﬁrst three instructions are applied to it, until a stall is again detected. After the third warp is swapped in and stalls, execution continues by swapping in the ﬁrst warp and continuing execution. If its “txr” command’s data are not yet returned at this point, execution truly stalls until these data are available. Each warp ﬁnishes in turn.



## GPU Pipeline Overview

![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/GPU%20implementation%20of%20the%20rendering%20pipeline.PNG)

> GPU implementation of the rendering pipeline. The stages are color coded according to the degree of user control over their operation. Green stages are fully programmable. Dashed lines show optional stages. Yellow stages are conﬁgurable but not programmable, e.g., various blend modes can be set for the merge stage. Blue stages are completely ﬁxed in their function.

The **vertex shader** is a fully programmable stage that is used to implement the geometry processing stage. 

The **geometry shader** is a fully programmable stage that operates on the vertices of a primitive (point, line, or triangle). It can be used to perform per-primitive shading operations, to destroy primitives, or to create new ones.

The **tessellation stage** and **geometry shader** are both optional, and not all GPUs support them, especially on mobile devices.

The **clipping**, **triangle setup**, and **triangle traversal** stages are implemented by ﬁxed-function hardware. 

**Screen mapping** is aﬀected by window and viewport settings, internally forming a simple scale and repositioning. 

The **pixel shader** stage is fully programmable. 

Although the **merger** stage is not programmable, it is highly conﬁgurable and can be set to perform a wide variety of operations. It implements the “merging” functional stage, in charge of modifying the color, z-buﬀer, blend, stencil, and any other output-related buﬀers. 

pixel shader execution together with the merger stage form the conceptual pixel processing stage.

## The Programmable Shader Stage

shader languages:

- HLSL:  *DirectX’s High-Level Shading Language*

- GLSL: *OpenGL Shading Language*

DirectX’s HLSL can be compiled to virtual machine bytecode, also called the **intermediate language** (**IL** or **DXIL**), to provide hardware independence.



A **draw call** invokes the graphics API to draw a group of primitives, so causing the graphics pipeline to execute and run its shaders.

Each programmable shader stage has two types of inputs:

- uniform inputs, with values that remain constant throughout a draw call (but can be changed between draw calls)
-  varying inputs, data that come from the triangle’s vertices or from rasterization. 

#### Shader Virtual Machine Register

The underlying virtual machine provides special **registers** for the diﬀerent types of inputs and outputs. The number of available **constant registers** for uniforms is much larger than those registers available for varying inputs or outputs. 

This happens because:

- the varying inputs and outputs need to be stored separately for each vertex or pixel, so there is a natural limit as to how many are needed.  
- The uniform inputs are stored once and reused across all the vertices or pixels in the draw call.

The virtual machine also has general-purpose **temporary registers**, which are used for scratch space.

All types of registers can be array-indexed using integer values in temporary registers.



![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/Uni%EF%AC%81ed%20virtual%20machine%20architecture%20and%20register%20layout.PNG)

> Uniﬁed virtual machine architecture and register layout, under Shader Model 4.0. The maximum available number is indicated next to each resource. Three numbers separated by slashes refer to the limits for vertex, geometry, and pixel shaders (from left to right).



#### flow control

Instructions related to **ﬂow control** are used to implement high-level language constructs such as “if” and “case” statements, as well as various types of loops.

Shaders support two types of ﬂow control: 

- **Static ﬂow control** branches are based on the values of uniform inputs.  This means that the ﬂow of the code is constant over the draw call. 
- **Dynamic ﬂow control** is based on the values of varying inputs, meaning that each fragment can execute the code diﬀerently.

The primary beneﬁt of **static ﬂow control** is to allow the same shader to be used in a variety of diﬀerent situations (e.g., a varying numbers of lights). There is no thread divergence, since all invocations take the same code path.

Dynamic flow control is much more powerful than static ﬂow control but can cost performance, especially if the code ﬂow changes erratically between shader invocations.



## The Vertex Shader

A triangle mesh is represented by a set of vertices, each associated with a speciﬁc **position** on the model surface. Besides position, there are other optional properties associated with each vertex, such as a **color or texture coordinates**. Surface **normals** are deﬁned at mesh vertices as well.

The vertex shader provides a way to modify, create, or ignore values associated with each triangle’s vertex, such as its color, normal, texture coordinates, and position.

Normally the vertex shader program transforms vertices from **model space** to **homogeneous clip space** . At a minimum, a vertex shader must always output this **location**.

Since each vertex is treated independently, any number of shader processors on the GPU can be applied **in parallel** to the incoming stream of vertices.

#### Shader Effects

- vertex blending for animating joints(动画关节的定点混合)
- silhouette rendering（轮廓渲染）
- Object generation, by creating a mesh only once and having it be deformed by the vertex shader.
- Animating character’s bodies and faces using skinning and morphing（蒙皮） techniques.
- Procedural deformations（程序变形）, such as the movement of ﬂags, cloth, or water
- Particle creation, by sending degenerate (no area) meshes down the pipeline and having these be given an area as needed.
- Lens distortion（镜头扭曲）, heat haze（热雾）, water ripples（水波纹）, page curls（页面卷曲）, and other eﬀects, by using the entire framebuﬀer’s contents as a texture on a screen-aligned mesh undergoing procedural deformation.
- Applying terrain height ﬁelds by using vertex texture fetch



## The Tessellation Stage (曲面细分阶段)

The tessellation stage allows us to render curved surfaces. The GPU’s task is to take each surface description and turn it into a representative set of triangles. This stage is an optional GPU feature .



Advantages:

- Memory Savings
- Keep the bus between CPU and GPU from becoming the bottleneck for an animated character or object whose shape is changing each frame
- surface can be rendered efficiently by having an appropriate number of triangles generated for the given view. This ability to control the **level of detail** can also allow an application to control its performance



The tessellation stage always consists of three elements:

- hull shader: in OpenGL is the tessellation control shader
- tesssellator: in OpenGL is primitive genearator
- domain shader: in OpenGL is the tessellation evaluation shader



![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/The%20tessellation%20stage.PNG)

> The tessellation stage. The hull shader takes in a patch deﬁned by control points. It sends the tessellation factors (TFs 曲面细分因子) and type to the ﬁxed-function tessellator. The control point set is transformed as desired by the hull shader and sent on to the domain shader, along with TFs and related patch constants. The tessellator creates the set of vertices along with their barycentric coordinates. These are then processed by the domain shader, producing the triangle mesh (control points shown for reference).



### Hull Shader

The input to the hull shader is a special patch primitive. This consists of several control points deﬁning a subdivision surface（细分曲面）, B´ezier patch, or other type of curved element.

Hull Shader has two functions:

-  First, it tells the tessellator how many triangles should be generated, and in what conﬁguration. 
-  Second, it performs processing on each of the control points.

- Also, optionally, the hull shader can modify the incoming patch description, adding or removing control points as desired.

The hull shader outputs its set of control points, along with the tessellation control data, to the domain
shader.

### Tessellator

The tessellator is a fixed-function stage in the pipeline, only used with tessellation shaders. It has the task of adding several new vertices for the domain shader to process.

The hull shader sends the tessellator information about what type of tessellation surface is desired: triangle, quadrilateral, or isoline.( Isolines are sets of line strips, sometimes used for hair rendering.)

The other important values sent by the hull shader are the **tessellation factors** (tessellation levels in OpenGL). These are of two types: **inner and outer edge**.  

- The two inner factors determine how much tessellation occurs inside the triangle or quadrilateral.
- The outer factors determine how much each exterior edge is split

### Domain Shader

The control points for the curved surface from the hull shader are used by each invocation of the domain shader to compute the output values for each vertex. 

The domain shader has a data ﬂow pattern like that of a vertex shader, with each input vertex from the tessellator being processed and generating a corresponding output vertex. The triangles formed are then passed on down the pipeline.

The domain shader takes the barycentric coordinates（重心坐标） generated for each point and uses these in the patch’s evaluation equation to generate the position, normal（法线）, texture coordinates（纹理坐标）, and other vertex information desired.

## The Geometry Shader

Note that no output at all can be generated by the geometry shader. 

The geometry shader is designed for modifying incoming data or making a limited number of copies. 

The geometry shader is guaranteed to output results from primitives in the same order that they are input. This aﬀects performance, because if several shader cores run in parallel, results must be saved and ordered. 

## The Pixel Shader

This piece of a triangle partially or fully overlapping the pixel is called a **fragment**.

In OpenGL the **pixel shader** is known as the **fragment shader**, which is perhaps a better name. 

In programming terms, the vertex shader program’s outputs, interpolated across the triangle (or line), eﬀectively become the pixel shader program’s inputs.

With inputs in hand, typically the pixel shader computes and outputs a fragment’s color. It can also possibly produce an opacity value and optionally modify its z-depth.

A pixel shader also has the unique ability to discard an incoming fragment, i.e., generate no output. 

### MRT  multiple render targets 

Instead of sending results of a pixel shader’s program to just the color and z-buﬀer, multiple sets of values could be generated for each fragment and saved to diﬀerent buﬀers, each called a **render target**.

A single rendering pass could generate a color image in one target, object identiﬁers in another, and world-space distances in a third. This ability has also given rise to a diﬀerent type of rendering pipeline, called **deferred shading**, where visibility and shading are done in separate passes. The ﬁrst pass stores
data about an object’s location and material at each pixel. Successive passes can then eﬃciently apply illumination and other eﬀects. 

### limitation

The pixel shader’s limitation is that it can normally write to a render target at only the fragment location handed to it, and cannot read current results from neighboring pixels. That is, when a pixel shader program executes, it cannot send its output directly to neighboring pixels, nor can it access others’ recent changes. Rather, it computes results that aﬀect only its own pixel. 

But  an output image created in one pass can have any of its data accessed by a pixel shader in a later pass. 

#### Exception

There are exceptions to the rule that a pixel shader cannot know or aﬀect neighboring pixels’ results. 

- One is that the pixel shader can immediately access information for adjacent fragments (albeit indirectly) during the computation of gradient or derivative information.



## The Merging Stage

The **merging stage** is where the depths and colors of the individual fragments (generated in the pixel shader) are combined with the framebuﬀer. 

The merging stage occupies the middle ground between ﬁxed-function stages, such as triangle setup, and the fully programmable shader stages. Although it is **not programmable**, its operation is **highly conﬁgurable**.

On most traditional pipeline diagrams, this stage is where **stencil-buﬀer** and **z-buﬀer** operations occur. If the fragment is visible, another operation that takes place in this stage is **color blending**. 

- For **opaque** surfaces there is no real blending involved, as the fragment’s color simply replaces the previously stored color. Actual blending of the fragment and stored color is commonly used for **transparency** and **compositing** operations  



The fragment is culled if hidden. This functionality is called **early-z**.

## The Compute Shader

