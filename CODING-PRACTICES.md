# How Duck Code Should Be
- All functions, classes & modules must always have a docstring.
- Comments must be used to explain code.
- Avoid using recursion, use iterative approach instead (better performance and less overhead of attribute lookup)
- Typings are a must.
- Docs should be fully static, this is for best performance and also allow docs to be served easily from many compatible static site hosts like github pages, etc. If you want something dynamic in docs, just redirect user to a dynamic main page instead.
