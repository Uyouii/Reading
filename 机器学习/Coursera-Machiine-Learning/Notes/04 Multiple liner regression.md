## Multiple features

![multiple_features_1](../../../images/machine-learning/multiple_features_1.png)

**Model**
$$
f_{w,b} = w_1x_1 + w_2x_2 + w_3x_3 + w_4x_4 + b
$$

**multiple liner regression **

![multiple_liner_regression](../../../images/machine-learning/multiple_liner_regression.png)



### Vectorization

![Vectorization1](../../../images/machine-learning/Vectorization1.png)

### Gradient descent for multiple linear regression

![image-20240407100109034](../../../images/machine-learning/image-20240407100109034.png)

![image-20240407101335265](../../../images/machine-learning/image-20240407101335265.png)

#### Normal Equation

Normal Equation:

- Only for linear regression
- Solve for w,b withour iterations.

Disadvantages

- Doesn’t generalize to other learning algorithms.
- Slow when number of features is large (> 10,000)

What you need to know

- Normal equation method may be used in machine learning libraries that implement linear regression
- Gradient descent is the recommended method for finding parameters w,b







