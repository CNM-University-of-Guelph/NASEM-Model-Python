import os
import random
import time

import pandas as pd
import nasem_dairy as nd

# TODO: Animal inputs for experiment?
animal_input = {
    "An_Parity_rl": 1,
    "Trg_MilkProd": 25.062,
    "An_BW": 624.795,
    "An_BCS": 3,
    "An_LactDay": 100,
    "Trg_MilkFatp": 4.55,
    "Trg_MilkTPp": 3.66,
    "Trg_MilkLacp": 4.85,
    "Trg_Dt_DMIn": 25.0,
    "An_BW_mature": 700,
    "Trg_FrmGain": 0.19,
    "An_GestDay": 46,
    "An_GestLength": 280,
    "Trg_RsrvGain": 0,
    "Fet_BWbrth": 44.1,
    "An_AgeDay": 820.8,
    "An_305RHA_MlkTP": 280,
    "An_StatePhys": "Lactating Cow",
    "An_Breed": "Holstein",
    "An_AgeDryFdStart": 14,
    "Env_TempCurr": 22,
    "Env_DistParlor": 0,
    "Env_TripsParlor": 0,
    "Env_Topo": 0
    }

equation_selection = {
    "Use_DNDF_IV": 0,
    "DMIn_eqn": 0,
    "mProd_eqn": 4, # NOTE: Which Mlk_Prod to use? Ask John
    "MiN_eqn": 1,
    "NonMilkCP_ClfLiq": 0,
    "Monensin_eqn": 0,
    "mPrt_eqn": 1, # NOTE have Melanie change this to 1
    "mFat_eqn": 1,
    "RumDevDisc_Clf": 0
    }

def get_feed_types(number_of_feeds: dict) -> list:
    feeds_to_choose_from = []
    for feed_type in number_of_feeds.keys():
        selected_number = random.choice(number_of_feeds[feed_type])

        for _ in range(0, selected_number):
            feeds_to_choose_from.append(feed_type)

    # print(feeds_to_choose_from)
    return feeds_to_choose_from


# TODO: Add feed column to make this more explicit isntead of matching on feed name?
def select_feeds(feed_library: pd.DataFrame, feeds_to_choose_from: list) -> dict:
    # Need to check feeds aren't chosen twice
    select_feeds = {}

    for feed_type in feeds_to_choose_from:
        if feed_type == "Silage":
            silage_options = feed_library[
                (feed_library["Fd_Type"] == "Forage") & 
                (feed_library["Fd_Name"].str.contains("Silage", case=False, na=False))
            ]
            if not silage_options.empty:
                silage = silage_options.sample(n=1)
            else:
                raise ValueError("No silage options available in feed library.")

            feed_name = silage["Fd_Name"].values[0]
            select_feeds[feed_name] = "Silage"


        elif feed_type == "Hay":
            hay_options = feed_library[
                (feed_library["Fd_Type"] == "Forage") & 
                (feed_library["Fd_Name"].str.contains("Hay", case=False, na=False))
            ]
            hay = hay_options.sample(1)
            feed_name = hay["Fd_Name"].values[0]
            select_feeds[feed_name] = "Hay"
            # if not hay_options.empty and not straw_options.empty:
                # second_forage = hay_options.sample(n=1) if random.choice([True, False]) else straw_options.sample(n=1)
            # elif not hay_options.empty:
            #     second_forage = hay_options.sample(n=1)
            # elif not straw_options.empty:
            #     second_forage = straw_options.sample(n=1)
            # else:
            #     second_forage = pd.DataFrame()  # fallback in case both are missing


        elif feed_type == "Straw":
            straw_options = feed_library[
                (feed_library["Fd_Type"] == "Forage") & 
                (feed_library["Fd_Name"].str.contains("Straw", case=False, na=False))
            ]
            straw = straw_options.sample(1)
            feed_name = straw["Fd_Name"].values[0]
            select_feeds[feed_name] = "Straw"


        elif feed_type == "Energy":
            energy_conc = feed_library[
                (feed_library["Fd_Type"] == "Concentrate") & 
                (feed_library["Fd_Category"].str.contains("Energy", case=False, na=False))
            ].sample(n=1)
            feed_name = energy_conc["Fd_Name"].values[0]
            select_feeds[feed_name] = "Energy"


        elif feed_type == "Fat Supp.":
            fat_supp = feed_library[
                (feed_library["Fd_Type"] == "Concentrate") & 
                (feed_library["Fd_Category"].str.contains("Fat", case=False, na=False))
            ].sample(n=1)
            feed_name = fat_supp["Fd_Name"].values[0]
            select_feeds[feed_name] = "Fat Supp."


        elif feed_type == "Protein Supp.":
            protein_supp = feed_library[
                (feed_library["Fd_Type"] == "Concentrate") & 
                (feed_library["Fd_Category"].str.contains("Protein", case=False, na=False))
            ].sample(n=1)
            feed_name = protein_supp["Fd_Name"].values[0]
            select_feeds[feed_name] = "Protein Supp."


        else:
            raise ValueError(f"feed_type {feed_type} is not a valid option")
        
    return select_feeds


def assign_weights(selected_feeds: dict, feed_options: dict, total_intake: int = 25) -> dict:
    diet_data = { 
        "Feedstuff": [],
        "kg_user": []
    }
    for feed_name, feed_type in selected_feeds.items():
        diet_data["Feedstuff"].append(feed_name)
        feed_weight = random.uniform(feed_options[feed_type][0], feed_options[feed_type][1]) * total_intake
        diet_data["kg_user"].append(feed_weight)
    
    total_kg = sum(diet_data["kg_user"])  
    if total_kg > 0:
        scaling_factor = total_intake / total_kg  
        diet_data["kg_user"] = [weight * scaling_factor for weight in diet_data["kg_user"]]

    return diet_data


def create_diet(feed_library: pd.DataFrame, feed_options: dict, number_of_feeds: dict, total_intake: float = 25):
    feeds_to_choose_from = get_feed_types(number_of_feeds)
    selected_feeds = select_feeds(feed_library, feeds_to_choose_from)
    diet_data = assign_weights(selected_feeds, feed_options, total_intake)
    diet = pd.DataFrame(diet_data)
    return diet


def create_wide_diet_dataframe(all_diets, all_outputs, number_of_feeds, output_variables):
    # Calculate total possible feeds
    total_feeds = sum([value[-1] for value in number_of_feeds.values()])
    
    # Create column names
    columns = []
    for num in range(total_feeds):
        columns.append(f"Feed_{num + 1}")
        columns.append(f"Feed_{num + 1}_kg")
    
    # Add output variable columns
    columns.extend(output_variables)
    
    # Create a list to store all rows
    all_rows = []
    
    # Populate rows
    for diet, output in zip(all_diets, all_outputs):
        feed_names = diet["Feedstuff"]
        feed_kg = diet["kg_user"]
        
        # Initialize new row with None values
        new_row = [None] * (total_feeds * 2 + len(output_variables))
        
        # Fill in feed data
        for i in range(min(len(feed_names), total_feeds)):
            new_row[i * 2] = feed_names[i]
            new_row[i * 2 + 1] = feed_kg[i]
        
        # Fill in output variables
        for i, var in enumerate(output_variables):
            new_row[total_feeds * 2 + i] = output.get_value(var)
        
        # Add row to list
        all_rows.append(new_row)
    
    # Create DataFrame with results
    wide_diets = pd.DataFrame(all_rows, columns=columns)
    
    # Replace None values with "NaN" string
    wide_diets = wide_diets.fillna("NaN")
    
    return wide_diets


if __name__ == "__main__":
    start_time = time.time()
    feed_library = pd.read_csv(
        os.path.join(os.path.dirname(__file__),
                    # "../../src/nasem_dairy/data/feed_library/NASEM_feed_library.csv")
                    "../data/melanie_feed.csv")
        )
    feed_options = {
        "Silage": (0.3, 0.6), 
        "Hay": (0.2, 0.3),
        "Straw": (0.2, 0.3), 
        "Energy": (0.2, 0.3),
        "Fat Supp.": (0.05, 0.1),
        "Protein Supp.": (0.1, 0.2)
    }
    number_of_feeds = {
        "Silage": [1, 2],
        "Hay": [0, 1, 2],
        "Straw": [0, 1],
        "Energy": [1, 2],
        "Fat Supp.": [0, 1],
        "Protein Supp.": [1, 2]
    }

    num_iterations = 100
    all_diets = []
    all_outputs = []

    for _ in range(num_iterations):
        diet = create_diet(feed_library, feed_options, number_of_feeds, 15)  
        output = nd.nasem(diet, animal_input, equation_selection)  

        # TODO: Should there be some evaluation of the diet to decide if we keep results
        # Ex. If a diet has 50% starch do we ignore it and keep sampling until we have n valid diets

        all_diets.append(diet.to_dict(orient='list'))  
        all_outputs.append(output)


    # for i, (diet, output) in enumerate(zip(all_diets, all_outputs)):
    #     print(f"Iteration {i+1}:")
    #     print(f"Created Diet: {diet}")  
    #     print(f"Sum of Diet: {sum(diet['kg_user'])}")  
    #     print(f"Milk Production: {output.get_value('Mlk_Prod')}")
    #     print(f"Milk Fat: {output.get_value('MlkFat_Milk') * 100}%")
    #     print(f"Milk Protein: {output.get_value('MlkNP_Milk') * 100}%")
    #     print("=" * 50)

    output_variables = ["Mlk_Prod", "MlkFat_Milk", "MlkNP_Milk"]
    wide_diets = create_wide_diet_dataframe(all_diets, all_outputs, number_of_feeds, output_variables)
    wide_diets.to_csv("test_100.csv", index=False)

    end_time = time.time()
    print(f"Script finished running in {end_time - start_time} seconds")
