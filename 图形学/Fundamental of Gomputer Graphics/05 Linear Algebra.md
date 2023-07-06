# Linear Algebra

## Determinants(行列式)

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\The signed area of the parallelogram is ab ,and in this case the area is positive..JPG)

> The signed area of the parallelogram is |**ab**| ,and in this case the area is positive.

For 2D vectors a and b, the determinant | **ab** | is the area of the parallelogram(平行四边形) formed by a and b.

This is a signed area, and the sign is positive if **a** and **b** are right-handed and negative if they are left-handed.This means$ | \mathbf{ab} | = −|  \mathbf{ba} |$

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\The signed volume of the parallelepiped shown is denoted by the determinant abc.JPG)

> The signed volume of the parallelepiped shown is denoted by the determinant |**abc**|, and in this
> case the volume is positive because the vectors form a righthanded basis.

For three 3D vectors, a, b, and c, the determinant | **abc** | is the signed volume of the parallelepiped (平行六面体)  formed by the three vectors.

Now let’s assume a Cartesian representation for **a** and **b**:

$$
|\mathbf{ab} | = (x_a\mathbf{x} + y_a\mathbf{y})(x_b\mathbf{x} + y_b\mathbf{y})| \\
= x_ay_b - y_ax_b
$$
This simpliﬁcation uses the fact that | **vv** | = 0 for any vector **v**

In three dimensions, the determinant of three 3D vectors a, b, and c is denoted | **abc** |
$$
|\mathbf{abc}| = |(x_a\mathbf{x} + y_a\mathbf{y} + z_a\mathbf{z})(x_b\mathbf{x} + y_b\mathbf{y} + z_b\mathbf{z})(x_c\mathbf{x} + y_c\mathbf{y} + z_c\mathbf{z})| \\
= x_ay_bz_c - x_az_by_c - y_ax_bz_c + y_az_bx_c + z_ax_by_c - z_ay_bx_c
$$
**Example**:
$$
\mathbf{c} = a_c\mathbf{a} + b_c\mathbf{b}
$$
![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\On the left, the vector c can be represented using two basis vectors as aca + bcb.JPG)

>  On the left, the vector c can be represented using two basis vectors as ac**a** + bc**b**. On the right, we see that the parallelogram formed by **a** and **c** is a sheared version of the parallelogram formed by bc**b** and **a**.

we get:
$$
|(b_c\mathbf{b})\mathbf{a}| = |\mathbf{ca}| \\
b_c = \frac{\mathbf{ca}}{\mathbf{ba}}
$$
then:
$$
a_c = \frac{\mathbf{bc}}{\mathbf{ba}}
$$

## Matrices

### Matric Arithmetic

For matric multiplication, we "multiply" rows of the first matrix with columns of the second matrix:

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\So the element p ij of the resulting product is.JPG)

So the element $p_{ij}$ of the resulting product is
$$
p_{ij} = a_{i1}b_{1j} + a_{i2}b_{2j} + ... + a_{im}b_{mj}
$$
Matrix multiplication is ***not*** commutative(交换) in most instances:
$$
AB \neq BA
$$
Also, if **AB** = **AC**, it does not necessarily follow that **B** = **C**.

Fortunately, matrix multiplication is associative and distributive:
$$
(AB)C = A(BC) \\
A(B + C) = AB + AC \\
(A + B)C = AC + BC
$$

### Operations on Matrices

#### Inverse Matrices

We need a matrix **I** that we can think of as a “matrix one.” This exists only for square matrices and is known as the ***identity matrix***;For example, the four by four identity matrix is
$$
\mathbf{I} = \begin{bmatrix}
1 & 0 & 0 & 0\\ 
0 & 1 & 0 & 0\\ 
0 & 0 & 1 & 0\\ 
0 & 0 & 0 & 1
\end{bmatrix}
$$
The inverse matrix $A^{− 1}$ of a matrix **A** is the matrix that ensures $AA^{− 1}= I$.

Note that the inverse of $A^{-1}$ is $A$. So $AA^{-1} = A^{-1}A = I$.

The inverse of a product of two matrices is the product of the inverses, but with the order reversed:
$$
(AB)^{-1} = B^{-1}A^{-1}
$$

#### Transpose Matrices

The ***transpose***  $A^T$ of a matrix $A$ has the same numbers but the rows are switched with the columns. If we label the entries of $A^T$ as a $a^{'}_{ij}$ then 
$$
a_{ij} = a^{'}_{ji}
$$
The transpose of a product of two matrices:
$$
(AB)^T = B^TA^T
$$

#### Determinant of Matrices

The determinant has several nice relationships to the matrix operations just discussed, which we list here for reference:
$$
|AB| = |A||B| \\
|A^{-1}| = \frac{1}{|A|} \\
|A^T| = |A|
$$

### Vector Operations in Matrix Form

If we consider the result of the dot product as a 1 × 1 matrix, it can be written
$$
\mathbf{a}.\mathbf{b} = \mathbf{a}^T\mathbf{b}
$$
For example, if we take two 3D vectors we get
$$
[x_a \space y_a \space z_a]
\begin{bmatrix}
x_b \\ 
y_b \\ 
z_b \\ 
\end{bmatrix} = 
[x_ax_b + y_ay_b + z_az_b]
$$
we can think of a 3 × 3 matrix as a collection of three 3D vectors in two ways: either it is made up of three column vectors side-by-side, or it is made up of three row vectors stacked up. 

For instance, the result of a matrix-vector multiplication $\mathbf{y = Ax}$ can be interpreted as a vector whose entries are the dot products of **x** with the rows of **A**. Naming these row vectors $\mathbf{r}_i$ , we have
$$
\begin{bmatrix}
| \\ 
\mathbf{y} \\ 
| \\ 
\end{bmatrix} = 
\begin{bmatrix}
- & \mathbf{r}_1 & - \\ 
- & \mathbf{r}_2 & - \\ 
- & \mathbf{r}_3 & - \\ 
\end{bmatrix} 
\begin{bmatrix}
| \\ 
\mathbf{x} \\ 
| \\ 
\end{bmatrix} \\
$$

$$
y_i = \mathbf{r}_i. \mathbf{x}
$$

Alternatively, we can think of the same product as a sum of the three columns $\mathbf{c}_i$ of A, weighted by the entries of **x**:
$$
\begin{bmatrix}
| \\ 
\mathbf{y} \\ 
| \\ 
\end{bmatrix} = 
\begin{bmatrix}
| & | & | \\ 
 \mathbf{c}_1 & \mathbf{c}_2 &  \mathbf{c}_3 \\ 
| & | & | \\ 
\end{bmatrix} 
\begin{bmatrix}
x_1 \\ 
x_2 \\ 
x_3 \\ 
\end{bmatrix} \\
$$

$$
\mathbf{y} = x_1\mathbf{c}_1 + x_2\mathbf{c}_2 + x_3\mathbf{c}_3
$$

### Special Types of Matrices

The identity matrix is an example of a ***diagonal matrix***(对角矩阵), where all nonzero elements occur along the diagonal.

The identity matrix also has the property that it is the same as its transpose. Such matrices are called ***symmetric***(对称性).

The identity matrix is also an ***orthogonal*** matrix(正交矩阵), because each of its columns considered as a vector has length 1 and the columns are orthogonal to one another.The same is true of the rows.The determinant of any orthogonal matrix is either +1 or − 1.

A very useful property of orthogonal matrices is that they are nearly their own inverses.

Multiplying an orthogonal matrix by its transpose results in the identity,
$R^TR = I = RR^T $ for orthogonal R

## Computing With Matrices and Determinants

If we have 2D vectors r and s, we denote the determinant |**rs**|; this value is the signed area of the parallelogram formed by the vectors. 

![](E:\projects\Uyouii git\LearnOpenGL\Real Time Rending Image\The 2D determinant in Equation 5.8 is the area of the parallelogram formed by the 2D vectors..JPG)

> The 2D determinant in Equation 5.8 is the area of the parallelogram formed by the 2D vectors.

Suppose we have two 2D vectors with Cartesian coordinates (a, b) and (A, B)
$$

$$
