import nasem_dairy as nd
import pandas as pd

val1 = pd.Series([
    0.35, 0.41, 0.24
])

value = nd.calculate_UrDE_GEIn_percent(
    30.2
)

print(value)