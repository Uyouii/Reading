[TOC]


# 线性代数基础

## 向量

### 向量点乘

简写为：$a.b = \sum_{i=1}^{n}a_ib_i$
$$
\begin{bmatrix}
a_1\\  a_2\\  ...\\  a_{n-1}\\ a_{n}\\
\end{bmatrix} .
\begin{bmatrix}
b_1\\  b_2\\  ...\\  b_{n-1}\\ b_{n}\\
\end{bmatrix} =
a_1b_1 + a_2b_2 + ... + a_{n-1}b_{n-1} + a_nb_n
$$

#### 几何解释

点乘结果描述了两个向量的“相似”程度，点乘结果越大，两个向量越接近。

$a.b = \left \| a \right \| \left \| b \right \| cos\theta $

![](D:\projects\Learn OpenGL\Real Time Rending Image\向量点乘.PNG)

- a.b > 0 ,  $ 0 \leq \theta < 90$, a 和 b 同向
-  a.b = 0 ,  $ \theta = 90$, a 和 b 正交
- a.b < 0, $90 \leq \theta < 180$, a 和 b 反向

### 向量叉乘

叉乘公式为：
$$
\begin{bmatrix}
x_1\\  y_1\\  z_1\\ 
\end{bmatrix} \times
\begin{bmatrix}
x_2\\  y_2\\  z_2\\ 
\end{bmatrix} =
\begin{bmatrix}
y_1z_2 - z_1y_2\\  
z_1x_2 - x_1z_2\\  
x_1y_2 - y_1x_2\\ 
\end{bmatrix} 
$$
向量叉乘不满足交换律，但它满足反交换律：$a\times b = -(b \times a)$

叉乘也不满足结合律： $(a \times b ) \times c \neq  a \times ( b \times c)$

#### 几何解释

叉乘得到的向量垂直于原来的两个向量:

![](D:\projects\Learn OpenGL\Real Time Rending Image\向量叉乘.PNG)

$\left\| a \times b \right\| = \left\| a \right\| \left\| b \right\| sin\theta$

可以看到$\left\| a \times b \right\|$也等于 a 和 b 为两边的平行4边形的面积

![](D:\projects\Learn OpenGL\Real Time Rending Image\叉乘和平行四边形面积.PNG)

叉乘对零向量的解释为：它平行于任何其他向量，而点乘对零向量的解释为它和其他向量都垂直

叉乘的方向则和左右手坐标系有关



## 矩阵

### 矩阵的行列式

矩阵M的行列式记作|M|

矩阵行列式的一些性质：

- 矩阵积的行列式等于矩阵行列式的积：|AB| = |A||B|
- 矩阵转置的行列式等于原矩阵的行列式：$|M^T| = |M|$
- 交换矩阵的任意两行或两列，行列式变负
- 任意行或列的非零积加到另一行或列上不会改变行列式的值

#### 几何解释

2D中，行列式等于以基向量为两边的平行四边形的有符号面积

3D中，行列式等于以变换后的基向量为三边的平行六面体的有符号体积

### 转置矩阵 Transposed matrix

在线性代数中，矩阵A的转置是另一个矩阵 $A^T$，由下列等价动作建立：

- 把A的横列写为$A^T$的纵列
- 把A的纵列写为$A^T$的横行

形式上说，*m* × *n*矩阵*A*的转置是*n* × *m*矩阵:

$ A^T_{ij} = A_{ij} for 1 \leq i \leq n, 1 \leq j \leq m $

注：$A^T$ (转置矩阵)与$A^{-1}$(逆矩阵)不同

### 矩阵的逆 

#### 逆矩阵 Inverse matrix

在线性代数中，给定一个n阶方阵A，若存在一n阶方阵B，使得$AB=BA=I_n$，其中$I_n$为n阶单位矩阵，则称A是可逆的，且B是A的逆矩阵，记作 $A ^{-1} $。

只有正方形（n×n）的矩阵，亦即方阵，才可能、但非必然有逆矩阵。

矩阵的逆有一些重要的性质：

- 单位矩阵的逆是它本身：$I^{-1} = I$
- 矩阵转置的逆等于它的逆的转置: $(M^T)^{-1} = (M^{-1})^{T} $
- 矩阵乘积的逆等于矩阵的逆的相反顺序的乘积: $(AB)^{-1} = B^{-1}A^{-1}$



### 正交矩阵 orthogonal matrix

>  若方阵Q是正交的，当且仅当Q与它转置$Q^T$的乘积等于单位矩阵

在矩阵论中，正交矩阵是一个方块矩阵Q，其元素为实数，而且行与列皆为正交的单位向量（即矩阵的每一行都是单位向量，矩阵的所有行互相垂直），使得该矩阵的转置矩阵为其逆矩阵：
$$
Q^T = Q^{-1} \Leftrightarrow Q^TQ = QQ^T = I
$$
其中，I为单位矩阵。正交矩阵的行列式值必定为+1或者-1，因为：
$$
1 = det(I) = det(Q^TQ) = det(Q^T)det(Q) = (det(Q))^2 \Rightarrow |Q| = \pm1
$$
伴随矩阵的一些重要性值：

- 作为一个线性映射（变换矩阵），正交矩阵保持距离不变，所以它是一个[保距映射](https://zh.wikipedia.org/wiki/%E7%AD%89%E8%B7%9D%E5%90%8C%E6%9E%84)，具体例子为旋转与镜射
- 行列式值为+1的正交矩阵，称为**特殊正交矩阵**，它是一个旋转矩阵
- 行列式值为-1的正交矩阵，称为[瑕旋转](https://zh.wikipedia.org/wiki/%E7%91%95%E6%97%8B%E8%BD%89)矩阵。瑕旋转是旋转加上镜射。镜射也是一种瑕旋转。



旋转和镜像矩阵都是正交的






# Transforms

> What if angry vectors veer Round your sleeping head, and form.
> There’s never need to fear Violence of the poor world’s abstract storm.”
> ​		—Robert Penn Warren



A linear transform is one that preserves vector addition and scalar multiplication.
$$
f(x) + f(y) = f(x+y)
$$

$$
kf(x) = f(kx)
$$
Scaling and rotation transforms, in fact all linear transforms for three-element vectors, can be represented using a 3 × 3 matrix.

Adding a ﬁxed vector to another vector performs a **translation**

Combining **linear transforms** and **translations** can be done using an **aﬃne transform**（仿射变换）, typically stored as a 4 × 4 matrix. An aﬃne transform is one that performs a linear transform and then a translation. 

A direction vector is represented as  $ v = (v_x\quad v_y\quad v_z \quad 0)^T $ and a point as  $ v = (v_x\quad v_y\quad v_z \quad 1)^T $

All translation, rotation, scaling, reﬂection, and shearing matrices are aﬃne. The main characteristic of an aﬃne matrix is that it **preserves** the **parallelism of lines**, but not necessarily lengths and angles. 



## Basic Transforms

![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/Summary%20of%20most%20of%20the%20transforms.PNG)

>  Summary of most of the transform.



### Translation

A change from one location to another is represented by a translation matrix, **T**. This matrix translates an entity by a vector  $ t = (t_x , t_y , t_z ) $

$$
T(t) = T(t_x , t_y , t_z )=
\begin{pmatrix}
 1 & 0 & 0 & t_x\\ 
 0 & 1 & 0 & t_y\\ 
 0 & 0 & 1 & t_z\\ 
 0 & 0 & 0 & 1\\ 
\end{pmatrix}
$$
the multiplication of a point $ p = (p_x , p_y , p_z , 1 ) $ with **T(t)** yields a new point $ p′ = (p_x +t_x , p_y +t_y , p_z +t_z , 1) $ Notice that a vector $ v = (v_x , v_y , v_z , 0 ) $ is left unaﬀected by a multiplication by T, because a direction vector cannot be translated.

The **inverse** of a translation matrix is $ T^{-1}(t) = T(-t) $ that is, the vector t is negated.

### Rotation

it is a **rigid-body transform**, it preserves the distances between points transformed, and preserves
handedness.

In two dimensions, the rotation matrix is simple to derive. Assume that we have a vector,  $ v = (v_x, v_y)=(rcos\theta, rsin\theta) $ if we rotate that vector by φ radians, then we get  $ u = (rcos(\theta + \phi),rsin(\theta + \phi)) $

This can be rewritten as
$$
u = 
\begin{pmatrix}
 rcos(\theta + \phi)\\ 
 rsin(\theta + \phi)\\  
\end{pmatrix} = 
\begin{pmatrix}
 r(cos\theta cos\phi - sin\theta sin\phi)\\ 
 r(sin\theta cos\phi + cos\theta sin\phi)\\  
\end{pmatrix} = 
\begin{pmatrix}
 cos\phi & -sin\phi\\ 
 sin\phi & cos\phi \\  
\end{pmatrix}
\begin{pmatrix}
 rcos\theta\\ 
 rsin\theta\\  
\end{pmatrix} = R(\phi)v
$$
In three dimensions, commonly used rotation matrices are Rx (φ), Ry (φ), and Rz (φ), which rotate an entity φ radians around the x-, y-, and z-axes, respectively.
$$
R_x(\phi) =
\begin{pmatrix}
 1 & 0 & 0 & 0 \\
 0 & cos\phi & -sin\phi & 0 \\
 0 & sin\phi & cos\phi & 0 \\
 0 & 0 & 0 & 1 \\
\end{pmatrix}
$$

$$
R_y(\phi) =
\begin{pmatrix}
 cos\phi & 0 & sin\phi & 0 \\
 0 & 1 & 0 & 0 \\
 -sin\phi & 0 & cos\phi & 0 \\
 0 & 0 & 0 & 1 \\
\end{pmatrix}
$$

$$
R_z(\phi) =
\begin{pmatrix}
 cos\phi & -sin\phi & 0 & 0 \\
 sin\phi & cos\phi & 0 & 0 \\
 0 & 0 & 1 & 0 \\
 0 & 0 & 0 & 1 \\
\end{pmatrix}
$$


There is another way to obtain the **inverse**: $ R_i^{-1}(\phi)=R_i(-\phi) $ rotate in the opposite direction around the same axis.

### Scaling

a scaling matrix , $ S(s) = S(s_x, s_y, s_z) $.  scales an entity with factors sx, sy and sz along the x-, y-, and z-directions.

$$
S(s) =
\begin{pmatrix}
s_x & 0 & 0 & 0 \\
0 & s_y & 0 & 0 \\
0 & 0 & s_z & 0 \\
0 & 0 & 0 & 1 \\
\end{pmatrix}
$$
The scaling operation is called **uniform** if s x = s y = s z and **nonuniform** otherwise.

The **inverse** is  $ S^{-1}(s) = S(1/s_x, 1/s_y, 1/s_z) $

A negative value on one or three of the components of s gives a type of **reﬂection matrix**, also called a **mirror matrix**. It should be noted that a rotation matrix concatenated with a reﬂection matrix is also a reﬂection matrix.

To detect whether a given matrix reﬂects in some manner, compute the determinant of the upper left 3 × 3 elements of the matrix. If the value is negative, the matrix is reﬂective. 

### Shearing

There are six basic shearing matrices, and they are denoted $ H_{xy}(s),H_{xz}(s),H_{yx}(s),H_{yz}(s),H_{zx}(s),H_{zy}(s), $

![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/The%20e%EF%AC%80ect%20of%20shearing%20the%20unit%20square%20with%20H%20xz%20(s).PNG)

> The eﬀect of shearing the unit square with H xz (s). Both the y- and z-values are unaﬀected by the transform, while the x-value is the sum of the old x-value and s multiplied by the z-value, causing the square to become slanted. This transform is area-preserving, which can be seen in that the dashed areas are the same.
$$
H_{xz}(s) =
\begin{pmatrix}
1 & 0 & s & 0 \\
0 & 1 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{pmatrix}
$$
The eﬀect of multiplying this matrix with a point **p** yields a point:  $ (p_x + sp_z \quad p_y \quad p_z) ^ T $

The inverse of Hij(s) is generated by shearing in the opposite direction: 

$$
H_{ij}^{-1}(s) = H_{ij}(-s)
$$

### Concatenation of Transforms

Due to the **noncommutativity** of the multiplication operation on matrices, the order in which the matrices occur matters. Concatenation of transforms is therefore said to be **order-dependent**.

This composite matrix is **C = TRS**. Note the order here. The scaling matrix, **S**, should be applied to the vertices ﬁrst, and therefore appears to the right in the composition. 

### The Rigid-Body Transform

 Such a transform, consisting of concatenations of only translations and rotations, is called a **rigid-body transform**. It has the characteristic of preserving lengths, angles, and handedness.

Any rigid-body matrix, X, can be written as the concatenation of a translation matrix, T(t), and a rotation matrix, R. 
$$
X = T(t)R =
\begin{pmatrix}
r_{00} & r_{01} & r_{02} & t_x \\
r_{10} & r_{11} & r_{12} & t_y \\
r_{20} & r_{21} & r_{22} & t_z \\
0 & 0 & 0 & 1 \\
\end{pmatrix}
$$
The **inverse** of X is computed as:
$$
X^{-1} = (T(t)R)^{-1} = R^{-1}T(t)^{-1} = R^TT(-t)
$$
Another way to compute the inverse of **X** is to consider **R** (making R appear as 3 × 3 matrix) and **X** in the following notation
$$
\overline R = (r_{,0}\quad r_{,1}\quad r_{,2}) =
\begin{pmatrix}
r_0^T,\\
r_1^T,\\
r_2^T,\\
\end{pmatrix}, 
X = 
\begin{pmatrix}
\overline R & t\\
0^T & 1\\
\end{pmatrix},
$$
Some calculations yield the inverse in the expression shown:
$$
X^{-1} =
\begin{pmatrix}
r_0,& r_1, &r_2, &-{\overline R}^Tt\\
0 & 0 & 0 & 1
\end{pmatrix},
$$
### Normal Transform

Instead of multiplying by the matrix itself, the proper method is to use the **transpose of the matrix’s adjoint(伴随矩阵）**.





## Special Matrix Transforms and Operations

### The Euler Transform

The Euler transform is the multiplication of three matrices, More formally, the transform, denoted E: 
$$
E(h,p,r)=R_z(r)R_x(p)R_y(h)
$$

Since E is a concatenation of rotations, it is also clearly orthogonal(正交的). Therefore its inverse can be expressed as $E^{-1} = E^T = (R_zR_xR_y)^T = R_y^TR_x^TR_z^T$.

The Euler angles h, p, and r represent in which order and how much the **head**, **pitch**, and **roll** should rotate around their respective axes.  Also, “**head**” is sometimes known as “**yaw**”. 

![](https://github.com/Uyouii/LearnOpenGL/raw/master/Real%20Time%20Rending%20Image/The%20Euler%20transform.PNG)

#### Limitations

It is difficult to work with two sets of Euler angles in combination.For example, interpolation between one set and another is not a simple matter of interpolating each angle. In fact, two diﬀerent sets of Euler angles can give the same orientation, so any interpolation should not rotate the object at all. 



When you use Euler transforms, something called **gimbal lock** may occur. This happens when rotations are made so that one degree of freedom is lost.

关于gimbal lock的通俗解释：

> 这种现象的原因是 角度为 $\pm90$的第二次旋转使得第一次和第三次的旋转角相同，称作 **万向锁**

> 是指物体的两个旋转轴指向同一个方向。实际上，当两个旋转轴平行时，我们就说万向节锁现象发生了，换句话说，绕一个轴旋转可能会覆盖住另一个轴的旋转，从而失去一维自由度

> 通常说来，万向节锁发生在使用Eular Angles（欧拉角）的旋转操作中，原因是Eular Angles按照一定的顺序依次独立地绕轴旋转。让我们想象一个具体的旋转场景，首先物体先绕转X轴旋转，然后再绕Y轴，最后绕Z轴选择，从而完成一个旋转操作（飘飘白云译注：实际是想绕某一个轴旋转，然而Eular Angle将这个旋转分成三个独立的步骤进行），当你绕Y轴旋转90度之后万向节锁的问题就出现了，因为X轴已经被求值了，它不再随同其他两个轴旋转，这样X轴与Z轴就指向同一个方向（它们相当于同一个轴了）。



## Qutaternions

Quaternions are used to represent rotations and orientations. They are superior to both Euler angles and matrices in several ways. 

一个四元数包含一个标量分量和一个3D向量分量。经常记标量分量为w，记向量分量为单一的v或分开的x，y，z。两种记法分别为[w,v] 和 [w,(x,y,z)]

**Definition**: A quaternion $\hat{q}$ can be deﬁned in the following ways, all equivalent.

$\hat{\textbf{q}} = (\textbf{q}_v, q_w) = iq_x + jq_y + kq_z + q_w = \textbf{q}_v + q_w$

$\textbf{q}_v = iq_x + jq_y + kq_z = (q_x, q_y, q_z)$

$i^2 = j^2 = k^2 = -1, jk = -kj = i, ki = -ik = j, ij = -ji = k$

The variable $q_w$ is called the **real part** of a quaternion, $\hat{\textbf{q}} $. The imaginary part is $\textbf{q}_v ,$ and i, j, and k are called **imaginary units**.

> 具体内容看real time rendering4.3 和 3D数学基础：图形与游戏开发 10.4



#### 优缺点

- 平滑插值。slerp和squad提供了方位间的平滑插值，没有其他方法能提供平滑插值。
- 快速连接和角位移求逆。四元数叉乘能将角位移序列转换为单个角位移，用矩阵作同样的操作明显会慢一些。
- 能和矩阵形式快速转换。四元数和矩阵间的转换比欧拉角与矩阵间的转换稍微快一点。
- 仅用四个数。四元数包含4数，而矩阵用了9个数，比矩阵要“经济”的多。



## Vertex Blending

**Vertex blending** has several other names, such as **linear-blend skinning**, **enveloping**, or **skeleton-subspace deformation**.

**p** is the original vertex, and **u(t)** is the transformed vertex whose position depends on time t:

$\textbf u(t) = \sum_{i = 0}^{n - 1}w_iB_i(t)M_i^{-1}p$, where $\sum_{i = 0}^{n - 1}w_i = 1, w_i  \ge 0$

There are n bones inﬂuencing the position of **p**, which is expressed in world coordinates. The value w i is the weight of bone i for vertex **p**. The matrix $M_i$ transforms from the initial bone’s coordinate system to world coordinates.

In practice, the matrices $B_i(t)$ and $M_i^{-1}$ are concatenated for each bone for each frame of animation, and each resulting matrix is used to transform the vertices. The vertex **p** is transformed by the diﬀerent bones’ concatenated matrices, and then blended using the weights $w_i$ — thus the name *vertex blending*.



## Morphing

Morphing involves solving two major problems, namely, the *vertex correspondence* problem and the *interpolation* problem. 

we have a neutral model, *N* , and a set of diﬀerence poses, $D_i$ . Am orphed model *M* can then be obtained using the following formula:
$$
M = N + \sum_{i = 1}^kw_iD_i
$$

## Projection

### Orthographic Projection

A characteristic of an orthographic projection is that parallel lines remain parallel after the projection.When orthographic projection is used for viewing a scene, objects maintain the same size regardless of distance to the camera.

### Perspective Projection

Here, parallel lines are generally not parallel after projection; rather, they may converge to a single point at their extreme. Perspective more closely matches how we perceive the world, i.e., objects farther away are smaller.



