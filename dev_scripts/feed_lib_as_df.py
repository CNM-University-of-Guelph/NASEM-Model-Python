import pandas as pd
import nasem_dairy as nd

diet_info, animal_input, equation_selection = nd.read_input('../src/nasem_dairy/data/input.txt')

feeds_to_get = diet_info['Feedstuff'].to_list()

# Feed library as pandas df:
feed_lib_df = pd.read_csv("./test_files/NASEM_feed_library_useredited.csv")

# Filter df using list from user
selected_feed_data = feed_lib_df[feed_lib_df["Fd_Name"].isin(feeds_to_get)]

# set names as index for downstream
selected_feed_data = selected_feed_data.set_index('Fd_Name')

# Clean names:
selected_feed_data.index = selected_feed_data.index.str.strip()

selected_feed_data