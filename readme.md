# introduction

This is a simple interface program for database operations.
But when I do stress testing through jmeter,

When there is a large amount of concurrency, a coroutine has not released the lock, and another coroutine also acquires the lock.



        test_aiorwlock/1.png
      




