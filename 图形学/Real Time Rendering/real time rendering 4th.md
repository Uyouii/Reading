# The Graphics Rendering Pipeline

coarse division of the real-time rendering pipeline into four main stages:

- application  [CPU]
- geometry processing [GPU]
- rasterization [GPU]
- pixel processing [GPU]

![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/rendering%20pipeline.PNG)



## The Application Stage

- **collision detection** is commonly implemented in this stage.
- the application stage is also the place to take care of input from other sources, such as the keyboard, the mouse, or a head-mounted display
- Acceleration algorithms, such as particular culling algorithms are also implemented here, along with whatever else the rest of the pipeline cannot handle.

## Geometry Processing

The geometry processing stage on the GPU is responsible for most of the per-triangle and per-vertex operations. It is further divided into the following functional stages:

- vertex shading
- projection
- clipping
- screen mapping

### Vertex Shading

- two main tasks:
  - compute the position for a vertex
  - evaluate whatever the programmer may like to have as vertex output data

Traditionally much of the shade of an object was computed by applying lights to each vertex’s location and normal and storing only the resulting color at the vertex. These colors were then interpolated across the triangle. For this reason, this programmable vertex processing unit was named the **vertex shader**.



![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/veiw%20space.PNG)



**shading**: the operation of determining the effect of a light on a material.

### Projection

- orthographic projection
- perspective projection

Although these matrices transform one volume into another, they are called projections because after display, the z-coordinate is not stored in the image generated but is stored in a z-buﬀer. In this way, the models are projected from three to two dimensions.

### Clipping

- A primitive that lies fully inside the view volume will be passed on to the next stage as is. 
- Primitives entirely outside the view volume are not passed on further, since they are not rendered. 
- It is the primitives that are partially inside the view volume that require clipping.

### Screen Mapping

The x- and y-coordinates of each primitive are transformed to form **screen coordinates**.

Screen coordinates together with the z-coordinates are also called **window coordinates**.

## Rasterization 

Rasterization process is split up into two functional substages:

- triangle setup (primitive assembly)
  - In this stage the diﬀerentials, edge equations, and other data for the triangle are computed.
- triangle traversal
  -  Finding which samples or pixels are inside a triangle is often called triangle traversal

![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/rasterization%20and%20pixel%20processing.PNG)

## Pixel Processing

 Pixel processing is the stage where per-pixel or per-sample computations and operations are performed on pixels or samples that are inside a primitive.

 The pixel stage is divided into :
- pixel shading
- merging

### Pixel Shading

Any per-pixel shading computations are performed here, using the interpolated shading data as input. The end result is one or more colors to be passed on to the next stage. 

**texturing** is employed here.

### Merging

A **z-buﬀer** is the same size and shape as the color buﬀer, and for each pixel it stores the z-value to the currently closest primitive. 

This means that when a primitive is being rendered to a certain pixel, the z-value on that primitive
at that pixel is being computed and compared to the contents of the z-buﬀer at the same pixel. 
- If the new z-value is smaller than the z-value in the z-buﬀer, then the primitive that is being rendered is closer to the camera than the primitive that was previously closest to the camera at that pixel. 
- If the computed z-value is greater than the z-value in the z-buﬀer, then the color buﬀer and the z-buﬀer are left untouched. 

However, the z-buﬀer stores only a single depth at each point on the screen, so it cannot be used for partially transparent primitives. These must be rendered after all opaque primitives, and in back-to-front
order, or using a separate order-independent algorithm (Section 5.5). Transparency is one of the major weaknesses of the basic z-buﬀer.

The **alpha channel** is associated with the color buﬀer and stores a related opacity value for each pixel.

The **stencil buﬀer** is an oﬀscreen buﬀer used to record the locations of the rendered primitiveIt typically contains 8 bits per pixel. Primitives can be rendered into the stencil buﬀer using various functions, and the buﬀer’s contents can then be used to control rendering into the color buﬀer and z-buﬀer.

To avoid allowing the human viewer to see the primitives as they are being rasterized and sent to the screen, **double buﬀering** is used. This means that the rendering of a scene takes place oﬀ screen, in a back buﬀer. 

Once the scene has been rendered in the back buﬀer, the contents of the back buﬀer are swapped with the contents of the front buﬀer that was previously displayed on the screen. The swapping often occurs during **vertical retrace**, a time when it is safe to do so.