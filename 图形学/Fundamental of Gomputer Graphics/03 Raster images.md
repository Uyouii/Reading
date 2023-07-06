# Raster Images

Most computer graphics images are presented to the user on some kind of ***raster display***.  Raster displays show images as rectangular arrays of ***pixels***. 

Because rasters are so prevalent in devices, ***raster images*** are the most common way to store and process images.  A raster image is simply a 2D array that stores the ***pixel value*** for each pixel—usually a color stored as three numbers, for red, green, and blue.A raster image stored in memory can be displayed by using each pixel in the stored image to control the color of one pixel of the display.

## Raster Devices

 A few familiar raster devices can be categorized into a simple hierarchy:

- Output
  - Display
    - Transmissive: liquid crystal display (LCD)
    - Emissive: light-emitting diode (LED) display
  - Hardcopy
    - Binary: ink-jet printer
    - Continuous tone: dye sublimation printer
- Input
  - 2D array sensor: digital camera
  - 1D array sensor: flatbed scanner

### Displays

- Emissive displays:  which use pixels that directly emit controllable amounts of light
- Transmissive displays:  in which the pixels themselves don’t emit light but instead vary the amount of light that they allow to pass through them

## Images, Pixels, and Geomerty

a raster image is a big array of pixels, each of which stores information about the color of the image at its grid point.

in the physical world, images are functions deﬁned over two-dimensional areas—almost always rectangles. So we can abstract an image as a function
$$
I(x,y): R \rightarrow V, R \subset \mathbb{R}^2
$$
V is the set of possible pixel values.



![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\Coordinates of a four pixel × three pixel screen..PNG)

>  Coordinates of a four pixel × three pixel screen. Note that in some APIs the y-axis will point downward.

A mundane but important question is where the pixels are located in 2D space. (This is only a matter of convention, but establishing a consistent convention is important!)

The rectangular domain of the image has width $n_x$ and height $n_y $and is centered on this grid, meaning that it extends half a pixel beyond the last sample point on each side. So the rectangular domain of a $n_x \times n_y$ image is
$$
R = [-0.5, n_x - 0.5] \times [-0.5, n_y - 0.5]
$$

### Pixel Values

Less range is required for images that are meant to be displayed directly.  in many contexts it is perfectly sufﬁcient for pixels to have a bounded range, usually taken to be [0, 1] for simplicity. 

Images stored with ﬂoating-point numbers, allowing a wide range of values, are often called ***high dynamic range* (HDR)** images to distinguish them from ﬁxed-range, or ***low dynamic range* (LDR)** images that are stored with integers

Reducing the number of bits used to store each pixel leads two distinctive types of artifacts, or artificially introduced flaws, in images.

- First, encoding images with ﬁxed-range values produces ***clipping*** when pixels that would otherwise be brighter than the maximum value are set, or clipped, to the maximum representable value. 
- Second,  encoding images with limited precision leads to ***quantization*** artifacts, or ***banding***, when the need to round pixel values to the nearest representable value introduces visible jumps in intensity or color. 

### Monitor Intensities and Gamma

All modern monitors take digital input for the “value” of a pixel and convert this to an intensity level. The human perception of intensity is nonlinear and will not be part of the present discussion.

There are two key issues that must be understood to produce correct images on monitors. 

**The ﬁrst is that monitors are nonlinear with respect to input.**

As an approximate characterization of this nonlinearity, monitors are commonly characterized by a $\gamma$(“gamma”) value. This value is the degree of freedom in the formula
$$
displayed\space intensity = (maximum \space intensity)a^{\gamma}
$$
where *a* is the input pixel value between zero and one.

 A nice visual way to gauge the nonlinearity is to ﬁnd what value of a gives an intensity halfway between black and white. This a will be
$$
0.5 = a^{\gamma}
$$
If we can ﬁnd that *a*, we can deduce $γ$ by taking logarithms on both sides:
$$
\gamma = \frac{ln0.5}{ln\space a}
$$
Once we know γ, we can ***gamma correct*** our input so that a value of a = 0.5 is displayed with intensity halfway between black and white. This is done with the transformation
$$
a{'} = a^{\frac{1}{\gamma}}
$$
we get:
$$
displayed \space intensity = (a{'})^{\gamma} = {(a^{\frac{1}{\gamma}})}^{\gamma} (maximum \space intensity) = a(maximum \space intentisy)
$$
**Another important characteristic of real displays is that they take quantized(量化的) input values.**

So while we can manipulate intensities in the ﬂoating point range [0, 1], the detailed input to a monitor is a ﬁxed-size integer. 

 The most common range for this integer is 0–255 which can be held in 8 bits of storage. This means that the possible values for a are not any number in [0, 1] but instead
$$
possible \space values \space for \space a = \{ \frac{0}{255}, \frac{2}{255},\frac{2}{255},...,\frac{254}{255},\frac{255}{255}\}
$$
This means the possible displayed intensity values are approximately
$$
\{ M{(\frac{0}{255})}^{\gamma},M{(\frac{1}{255})}^{\gamma},M{(\frac{2}{255})}^{\gamma},...,M{(\frac{254}{255})}^{\gamma},M{(\frac{255}{255})}^{\gamma} \}
$$
where M is the maximum intensity.

## RGB Color

Most computer graphics images are deﬁned in terms of red-green-blue (RGB) color.

The basic idea of RGB color space is that the color is displayed by mixing three ***primary*** lights: one red, one green, and one blue. The lights mix in an ***additive*** manner.

In RGB additive color mixing we have:

- read +  green = yellow
- green + blue = cyan
- blue + red = magenta
- red + green + blue = white

![](https://github.com/Uyouii/LearnGraphics/raw/master/Real%20Time%20Rending%20Image/The%20additive%20mixing%20rules%20for%20colors%20red%20green%20blue..PNG)

> The additive mixing rules for colors red/green/blue.



## Alpha Compositing

Often we would like to only partially overwrite the contents of a pixel. A common example of this occurs in ***compositing***, where we have a background and want to insert a foreground image over it.

-  For opaque(不透明的) pixels in the foreground, we just replace the background pixel.
-  For entirely transparent foreground pixels, we do not change the background pixel.
-  For ***partially*** transparent pixels, some care must be taken.

 the most frequent case where foreground and background must be blended is when the foreground object only partly covers the pixel, either at the edge of the foreground object, or when there are sub-pixel holes such as between the leaves of a distant tree.

The most important piece of information needed to blend a foreground object over a background object is the ***pixel coverage***, which tells the fraction of the pixel covered by the foreground layer. We can call this fraction $\alpha$.

If we want to composite a foreground color $c_f $over background color $c_b $, and the fraction of the pixel covered by the foreground is α, then we can use the formula
$$
\mathbf{c} = \alpha \mathbf{c}_f + (1 - \alpha)\mathbf{c}_b
$$
The $α$ values for all the pixels in an image might be stored in a separate grayscale image, which is then known as an ***alpha mask*** or ***transparency mask***.

Or the information can be stored as a fourth channel in an RGB image, in which case it is called the ***alpha channel***, and the image can be called an RGBA image.

### Image Storage

Most RGB image formats use eight bits for each of the red, green, and blue channels. 

To reduce the storage requirement, most image formats allow for some kind of compression.At a high level, such compression is either ***lossless***(无损的) or ***lossy***(有损的).

Popular image storage formats include:

- **jpeg**. This lossy format compresses image blocks based on thresholds in the human visual system. This format works well for natural images.
- **tiff**. This format is most commonly used to hold binary images or losslessly compressed 8- or 16-bit RGB although many other options exist.
- **ppm**.  This very simple lossless, uncompressed format is most often used for 8-bit RGB images although many options exist.
- **png**. This is a set of lossless formats with a good set of open source management tools.

 