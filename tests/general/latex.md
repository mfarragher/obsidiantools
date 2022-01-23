# Note with LaTeX
## GEE $\beta$
Regression coefficients $\beta$ estimated through GEE are **asymptotically normal**:
$\hat{\beta}_{GEE} \xrightarrow{D} N(\beta_{0}, \Sigma(\beta_{0}))$

_The underscore chars above need to be caught through MathJax - capture subscripts rather than emphasis in the `markdown` parsing._

## GEE estimation
_A few eqs more using deeper LaTeX functionality:_

Equations for GEE are solved for the regression parameters $\beta$ using:
$$U_{GEE}(\beta, \alpha, \phi) = \sum_{i=1}^{n} D_{i}^T~V_{i}(\alpha; \phi)^{-1} (y_{i} - \mu_{i}) = 0 \tag{1} \label{eq1}$$

Taking the expectation of the equation system in $\eqref{eq1}$ _..._
