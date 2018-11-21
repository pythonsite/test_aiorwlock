# introduction

This is a simple interface program for database operations.
But when I do stress testing through jmeter,

When there is a large amount of concurrency, a coroutine has not released the lock, and another coroutine also acquires the lock.

Below is the configuration I tested with jumeter

![1](https://github.com/pythonsite/test_aiorwlock/blob/master/1.png)
      
![1](https://github.com/pythonsite/test_aiorwlock/blob/master/2.png)

![1](https://github.com/pythonsite/test_aiorwlock/blob/master/3.png)

