# General memory allocation function
id : 233835

The goal of the `AllocZeroedInternal` function is to allocate a block of memory from a specified heap and initialize it to zero. 

```c
void *AllocZeroedInternal(void *heapStart, u32 size)
```

The `AllocZeroedInternal` function combines memory allocation and initialization. It allocates a block of memory from the specified heap and ensures that the entire block is set to zero. This is useful in scenarios where you need to ensure that the allocated memory does not contain any residual data from previous allocations.

