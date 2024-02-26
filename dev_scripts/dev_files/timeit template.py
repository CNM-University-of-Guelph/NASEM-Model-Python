import timeit

# Assuming DI_run_NASEM is the function you want to test
def DI_run_NASEM_old():
    DI_run_NASEM(testmethod='old')

def DI_run_NASEM_new():
    DI_run_NASEM(testmethod='new')

# Run timeit to measure execution time for the 'old' method
time_old = timeit.timeit(DI_run_NASEM_old, number=200)

# Run timeit to measure execution time for the 'new' method
time_new = timeit.timeit(DI_run_NASEM_new, number=200)

# Print the results
print(f"DI_run_NASEM with 'old' method took {time_old:.6f} seconds.")
print(f"DI_run_NASEM with 'new' method took {time_new:.6f} seconds.")