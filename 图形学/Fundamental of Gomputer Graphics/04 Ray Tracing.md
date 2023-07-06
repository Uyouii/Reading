# Ray Tracing

Fundamentally, ***rendering*** is a process that takes as its input a set of objects and produces as its output an array of pixels.

 rendering involves considering how each object contributes to each pixel; it can be organized in two
general ways:

- In ***object-order rendering***, each object is considered in turn, and for each object all the pixels that it inﬂuences are found and updated. 
-  In ***image-order rendering***, each pixel is considered in turn, and for each pixel all the objects that inﬂuence it are found and the pixel value is computed.

Image-order and object-order rendering approaches can compute exactly the same images, but they lend themselves to computing different kinds of effects and have quite different performance characteristics.

broadly speaking, image-order rendering is simpler to get working and more ﬂexible in the effects that can be produced, and usually (though not always) takes much more execution time to produce a comparable image.

## The Basic Ray-Tracing Algorithm

A ray tracer works by computing one pixel at a time, and for each pixel the basic task is to ﬁnd the object that is seen at that pixel’s position in the image.

Each pixel “looks” in a different direction, and any object that is seen by a pixel must intersect the ***viewing ray***, a line that emanates from the viewpoint in the direction that pixel is looking. 

The particular object we want is the one that intersects the viewing ray nearest the camera, since it blocks the view of any other objects behind it. 

Once that object is found, a ***shading*** computation uses the intersection point, surface normal, and other information (depending on the desired type of rendering) to determine the color of the pixel.

A basic ray tracer therefore has three parts:

1. ***ray generation***, which computes the origin and direction of each pixel’s viewing ray based on the camera geometry;
2.  ***ray intersection***, which ﬁnds the closest object intersecting the viewing ray;
3. ***shading***, which computes the pixel color based on the results of ray intersection.

The structure of the basic ray tracing program is:

```
for each pixel do
	compute viewing ray
	ﬁnd ﬁrst object hit by ray and its surface normal n
	set pixel color to value computed from hit point, light, and n
```

## Perspective

**Parallel Projection**

The simplest type of projection is ***parallel projection***, in which 3D points are mapped to 2D by moving them along a projection direction until they hit the image plane.  

The view that is produced is determined by the choice of projection direction and image plane.  If the image plane is perpendicular to the view direction, the projection is called ***orthographic***; otherwise it is called ***oblique***.

Parallel projections are often used for mechanical and architectural drawings because they keep parallel lines parallel and they preserve the size and shape of planar objects that are parallel to the image plane.

**Perspective Projection**

***perspective projection***: we simply project(投影) along lines that pass through a single point, the ***viewpoint***, rather than along parallel lines.

A perspective view is determined by the choice of viewpoint (rather than projection direction) and image plane. 

As with parallel views, there are oblique and non-oblique perspective views; the distinction is made based on the projection direction at the center of the image.

A surprising fact about perspective is that all the rules of perspective drawing will be followed automatically if we follow the simple mathematical rule underlying perspective: objects are projected directly toward the eye, and they are drawn where they meet a view plane in front of the eye.

## Computing Viewing Rays

A ray is really just an origin point and a propagation direction; a 3D parametric line is ideal for this. 

![](https://github.com/Uyouii/LearnGraphics/raw/master/Real%20Time%20Rending%20Image/The%20ray%20from%20the%20eye%20to%20a%20point%20on%20the%20image%20plane..PNG)

the 3D parametric line from the eye e to a point s on the image plane (Figure 4.6) is given by 
$$
\mathbf{p}(t) = \mathbf{e} + t(\mathbf{s} - \mathbf{e})
$$
The point **e** is the ray’s origin, and **s** − **e** is the ray’s direction.

Note that **p**(0) = **e**, and **p**(1) = **s**, and more generally, if 0 < $t_1 $< $t_2 $, then $\mathbf{p}(t_1 )$ is closer to the eye than $\mathbf{p}(t_2)$. Also, if t < 0, then **p**(t) is “behind” the eye.

> These facts will be useful when we search for the closest object hit by the ray that is not behind the eye.

All of our ray-generation methods start from an orthonormal coordinate frame known as the ***camera frame***,  which we’ll denote by **e**, for the *eye point*, or *view- point*, and **u**, **v**, and **w** for the three basis vectors, organized with **u** pointing rightward (from the camera’s view), **v** pointing upward, and **w** pointing backward, so that { **u**, **v**, **w** } forms a right-handed coordinate system.

![](https://github.com/Uyouii/LearnGraphics/raw/master/Real%20Time%20Rending%20Image/The%20vectors%20of%20the%20camera%20frame%2C%20together%20with%20the%20view%20direction%20and%20up%20direction..PNG)

> Since **v** and **w** have to be perpendicular, the up vector and **v** are not generally the same. But setting the up vector to point straight upward in the scene will orient the camera in the way we would think of as “upright.”

### Orthographic Views

For an orthographic view, all the rays will have the direction$ −\mathbf{w}$. 

The viewing rays should start on the plane deﬁned by the point e and the vectors u and v; the only remaining information required is where on the plane the image is supposed to be. 

We’ll deﬁne the image dimensions with four numbers, for the four sides of the image: l and r are the positions of the left and right edges of the image, as measured from e along the **u** direction; and b and t are the positions of the bottom and top edges of the image, as measured from e along the **v** direction.

to fit an image with $n_x \times n_y$ pixels into a rectangle of size (r- l) x (t - b), the pixel at position (i, j) in the raster image has the position
$$
u = l + (r - l)( i + 0.5) / nx, \\
v = b + (t - b)(j + 0.5) / ny, \\
$$
In an orthographic view, we can simply use the pixel’s image-plane position as the ray’s starting point, and we already know the ray’s direction is the view direction. The procedure for generating orthographic viewing rays is then:

```
compute u and v
ray.direction <-- -W
ray.origin <-- E + u U + v V
```

It’s very simple to make an oblique parallel view: just allow the image plane normal **w** to be speciﬁed separately from the view direction **d**. The procedure is then exactly the same, but with **d** substituted for − **w**. Of course w is still used to construct **u** and **v**.

![](https://github.com/Uyouii/LearnGraphics/raw/master/Real%20Time%20Rending%20Image/Ray%20generation%20using%20the%20camera%20frame.JPG)

### Perspective Views

For a perspective view, all the rays have the same origin, at the viewpoint; it is the directions that are different for each pixel.

The image plane is no longer positioned at **e**, but rather some distance d in front of **e**; this distance is the image ***plane distance***, often loosely called the ***focal length***, because choosing *d* plays the same role as choosing focal length in a real camera.

The direction of each ray is deﬁned by the viewpoint and the position of the pixel on the image plane.

 resulting procedure：

```
compute u and v using (4.1)
ray.direction <-- d W + u U + v V
ray.origin <-- E
```

As with parallel projection, oblique perspective views can be achieved by specifying the image plane normal separately from the projection direction, then replacing − d**w** with d**d** in the expression for the ray direction.

## Ray-Object Intersection

### Ray-Sphere Intersection

Intersection points occur when points on the ray satisfy the implicit equation, so we solve the equation:
$$
f(\mathbf{p}(t)) = 0 \space \space or \space \space f(e + t\mathbf{d}) = 0
$$
A sphere with center c = (x c , y c , z c ) and radius R can be represented by the implicit equation
$$
(x - x_c)^2 + (y - y_c)^2 +(z - z_c)^2 - R^2 = 0
$$
We can write this same equation in vector form:
$$
(\mathbf{p} - \mathbf{c}) . (\mathbf{p} - \mathbf{c}) - R^2 = 0
$$
Any point p that satisﬁes this equation is on the sphere. If we plug points on the ray **p**(t) = **e** + t**d** into this equation, 
$$
(\mathbf{e} + t\mathbf{d}- \mathbf{c}) . (\mathbf{e} + t\mathbf{d} - \mathbf{c}) - R^2 = 0
$$
Rearranging terms yields:
$$
(\mathbf{d}.\mathbf{d})t^2 + 2\mathbf{d}.(\mathbf{e} - \mathbf{c})t + (\mathbf{e} - \mathbf{c})(\mathbf{e} - \mathbf{c}) - R^2 = 0
$$
 a classic quadratic equation in t, meaning it has the form
$$
AT^2 + Bt + C = 0
$$
The term under the square root sign in the quadratic solution, $B^2 − 4AC$, is called the ***discriminant*** and tells us how many real solutions there are.

- If the discriminant is negative, its square root is imaginary and the line and sphere do not intersect.
-  If the discriminant is positive, there are two solutions: one solution where the ray enter the sphere and one where it leaves.
- If the discriminant is zero, the ray grazes the sphere, touching it at exactly one point.

Plugging in the actual terms for the sphere and canceling a factor of two, we get:
$$
t = \frac{-\mathbf{d}.(\mathbf{e} - \mathbf{c})\pm \sqrt{(\mathbf{d}.(\mathbf{e} - \mathbf{c})^2) - (\mathbf{d}.\mathbf{d})((\mathbf{e} - \mathbf{c}).(\mathbf{e} - \mathbf{c}) - R^2)}}{(\mathbf{d}.\mathbf{d})}
$$
the normal vector at point p is given by the gradient n = 2(**p** − **c**). The unit normal is (**p** − **c**)/R.

### Ray-Triangle Intersection

We will present the form that uses **barycentric coordinates**（重心坐标系） for the parametric plane containing the triangle, because it requires no long-term storage other than the vertices of the triangle
$$
\left.\begin{matrix}
x_e + tx_d = f(u,v)\\ 
y_e + ty_d = g(u,v)\\ 
z_e + tz_d = h(u,v)\\
\end{matrix}\right\} or,
\mathbf{e} + t\mathbf{d} = \mathbf{f}(u,v)
$$

![](https://github.com/Uyouii/LearnGraphics/raw/master/Real%20Time%20Rending%20Image/The%20ray%20hits%20the%20plane%20containing%20the%20triangle%20at%20point%20p.JPG)

> the ray hits the plane containing the triangle at point p

the intersection will occur when:
$$
\mathbf{e} + t\mathbf{d} = \mathbf{a} + \beta(\mathbf{b} - \mathbf{a}) + \gamma(\mathbf{c} - \mathbf{a})
$$

from section 2.7.2, we know that the intersection is inside the triangle if and only if β > 0, γ > 0 and β + γ < 1.

expand the equation from its vector form into three equations for the three coordinates:
$$
x_e + tx_d = x_a + \beta(x_b - x_a) + \gamma(x_c - x_a) \\
y_e + ty_d = y_a + \beta(y_b - y_a) + \gamma(y_c - y_a) \\
z_e + tz_d = z_a + \beta(z_b - z_a) + \gamma(z_c - z_a) \\
$$
......

The algorithm for the ray-triangle intersection for which we need the linear solution can have some conditions for early termination. Thus, the function should look something like:

```c
boolean raytri (ray r, vector3 a, vector3 b, vector3 c,interval [t0 , t1 ])
compute t
if (t < t0 ) or (t > t1 ) then
	return false
compute γ
if (γ < 0) or (γ > 1) then
	return false
compute β
if (β < 0) or (β > 1 − γ) then
	return false
return true
```

### Ray-Polygon(多边形) Intersection

Given a planar polygon with m vertices $\mathbf{p_1}$ through $mathbf{p_m}$ and surface normal **n**,w e ﬁrst compute the intersection points between the ray **e** + t**d** and the plane containing the polygon with implicit equation
$$
(\mathbf{p} - \mathbf{p_1}).\mathbf{n} = 0
$$
We do this by setting **p** = **e** + t**d** and solving for t to get
$$
t = \frac{(\mathbf{p}_1 - \mathbf{e}). \mathbf{n}}{\mathbf{d}. \mathbf{n}}
$$
This allows us to compute **p**. If **p** is inside the polygon, then the ray hits it; otherwise, it does not.

We can answer the question of whether **p** is inside the polygon by projecting the point and polygon vertices to the *xy* plane and answering it there. 

The easiest way to do this is to send any 2D ray out from **p** and to count the number of intersections between that ray and the boundary of the polygon. If the number of the intersection is odd, then the point is inside the polygon; otherwise it is not.

To make computation simple, the 2D ray may as well propagate along the x-axis:
$$
\begin{bmatrix}
x\\ 
y
\end{bmatrix} = 
\begin{bmatrix}
x_p\\ 
y_p
\end{bmatrix} + s
\begin{bmatrix}
1\\ 
0
\end{bmatrix}
$$
A problem arises, however, for polygons whose projection into the xy plane is a line. To get around this, we can choose among the *xy, yz, or zx* planes for whichever is best. 

If we implement our points to allow an indexing operation, e.g., **p**(0) = x p then this can be accomplished as follows:

```c
if (abs(zn ) > abs(xn )) and (abs(zn ) > abs(yn )) then
	index0 = 0
	index1 = 1
else if (abs(yn ) > abs (xn )) then
	index0 = 0
	index1 = 2
else
	index0 = 1
	index1 = 2
```

Now, all computations can use p(index0) rather than $x_p$ , and so on.

Another approach to polygons, one that is often used in practice, is to replace them by several triangles.

### Intersecting a Group of Objects

 A simple way to implement this is to think of a group of objects as itself being another type of object

To intersect a ray with a group, you simply intersect the ray with the objects in the group and return the intersection with the smallest t value. The following code tests for hits in the interval t ∈ [ t0, t1 ]:

```c
hit = false
for each object o in the group do
	if ( o is hit at ray parameter t and t ∈ [ t0, t1 ]) then
		hit = true
		hitobject = o
		t1 = t
	return hit
```

## Shading

Most shading models, one way or another, are designed to capture the process of light reﬂection, whereby surfaces are illuminated by light sources and reﬂect part of the light to the camera. 

### Lambertian Shading

the amount of energy from a light source that falls on an area of surface depends on the angle of the surface to the light.

-  A surface facing directly toward the light receives maximum illumination; 
- a surface tangent to the light direction (or facing away from the light) receives no illumination; 
- in between the illumination is proportional to the cosine of the angle θ between the surface normal and the light source 

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\Geometry for Lambertian shading.JPG)

This leads to the ***Lambertian shading model***:
$$
L = k_dImax(0, \mathbf{n}.\mathbf{l})
$$

- L is the pixel color

- $k_d$ is the ***diffuse coefficient*** or the surface color

- I is the intensity(强度) of the light source

Because **n** and **l** are unit vectors, we can use **n · l** as a convenient shorthand for cos θ

This equation applies separately to the three color channels

### Blinn-Phong Shading

Lambertian shading is ***view independent***: the color of a surface does not depend on the direction from which you look.

Many real surfaces show some degree of shininess, producing highlights, or ***specular reﬂections***(镜面反射), that appear to move around as the viewpoint changes.

many shading models add a ***specular component*** to Lambertian shading; the Lambertian part is then the
***diffuse component***(漫反射成分 )

The idea is to produce reﬂection that is at its brightest when **v** and **l** are symmetrically(对称的) positioned across the surface normal, which is when mirror reﬂection would occur;the reﬂection then decreases smoothly as the vectors move away from a mirror conﬁguration.

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\Geometry for Blinn-Phong shading.JPG)

We can tell how close we are to a mirror conﬁguration by comparing the half vector **h** to the surface normal.

If the half vector is near the surface normal, the specular component should be bright; if it is far away it should be dim.

This result is achieved by computing the dot product between **h** and **n**, then taking the result to a power p > 1 to make it decrease faster.

the Blinn-Phong shading model is as follows:
$$
\mathbf{h} = \frac{\mathbf{v} + \mathbf{l}}{\left \| \mathbf{v} + \mathbf{l} \right \|} \\
L = k_dImax(0,\mathbf{n}.\mathbf{l}) + k_sImax(0,\mathbf{n}.\mathbf{h})^p
$$
where $k_s$ is the **specular coefficient**, or the specular color, of the surface

### Ambient Shading

A crude but useful heuristic to avoid black shadows  is to add a constant component to the shading model, one whose contribution to the pixel color depends only on the object hit, with no dependence on the surface geometry at all. This is known as ***ambient shading***—it is as if surfaces were illuminated by “ambient” light that comes equally from everywhere.

Together with the rest of the Blinn-Phong model, ambient shading completes the full version of a simple and useful shading model:
$$
L = k_aI_a + k_dImax(0, \mathbf{n}.\mathbf{l}) + k_sImax(0,\mathbf{n}.\mathbf{h})^n
$$
where $k_a$ is the surface’s ambient coefﬁcient, or “ambient color,” and $I_a$ is the ambient light intensity

### Multiple Point Lights

A very useful property of light is ***superposition*** -- the effect caused by more than on light source is simply the sum of the effects of the light sources individually.

our simple shading model can easily be extended to handle N light sources:
$$
L = k_aI_a + \sum_{i = 1}^{N}[ k_dI_imax(0, \mathbf{n}.\mathbf{l}_i) + k_sI_imax(0,\mathbf{n}.\mathbf{h}_i)^p ]
$$
where $\mathit{I}_i$ , $\mathbf{l}_i$ , and $\mathbf{h}_i$ are the intensity, direction, and half vector of the $i^{th}$ light source.

## A Ray-Tracing Problem

```c
for each pixel do
	compute viewing ray
	if( ray hits an object with t ∈ [0, ∞)) then
		compute n
		evaluate shading model and set pixel to that color
	else
		set pixel color to background color
```

 ## Shadows

The rays that determine in or out of shadow are called ***shadow rays*** to distinguish them from viewing rays.

To get the algorithm for shading, we add an if statement to determine whether the point is in shadow.

In a naive implementation, the shadow ray will check for t ∈ [0, ∞ ), but because of numerical imprecision, this can result in an intersection with the surface on which p lies. Instead, the usual adjustment to avoid that problem is to test for t ∈ [	 $\epsilon $, ∞ ) where $\epsilon $ is some small positive constant

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\By testing in the interval starting at e, we avoid numerical imprecision causing the ray to hit the surface p is on.JPG)

> By testing in the interval starting at e, we avoid numerical imprecision causing the ray to hit the surface p is on

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\implement shadow rays for Phong lighting.JPG)

> E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\implement shadow rays for Phong lighting.JPG



## Ideal Specular Reflection

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\When looking into a perfect mirror.JPG)

> When looking into a perfect mirror, the viewer looking in direction **d** will see whatever the viewer “below” the surface would see in direction **r**.

$$
\mathbf{r} = \mathbf{d} - 2(\mathbf{d}.\mathbf{n})\mathbf{n}
$$

In the real world, some energy is lost when the light reﬂects from the surface, and this loss can be different for different colors. This can be implemented by adding a recursive call in ***raycolor***:
$$
color c = c + k_mraycolor(\mathbf{p} + s\mathbf{r}, \epsilon, \infty)
$$
where $k_m$ (for “mirror reﬂection”) is the specular RGB color. 

The problem with the recursive call above is that it may never terminate. For example, if a ray starts inside a room, it will bounce forever. This can be ﬁxed by adding a maximum recursion depth.

