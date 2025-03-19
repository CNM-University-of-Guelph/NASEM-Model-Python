import os
import random

import pandas as pd
import nasem_dairy as nd

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
    "mProd_eqn": 0,
    "MiN_eqn": 1,
    "NonMilkCP_ClfLiq": 0,
    "Monensin_eqn": 0,
    "mPrt_eqn": 0,
    "mFat_eqn": 1,
    "RumDevDisc_Clf": 0
    }

def select_feeds(feed_library: pd.DataFrame, feeds_to_choose_from: list) -> dict:
    # NOTE: Change the feeds_to_choose_from list to change number of feeds
    # feeds_to_choose_from = ["Silage", "Hay", "Hay", "Energy", "Fat Supp.", "Protein Supp."]
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
            straw_options = feed_library[
                (feed_library["Fd_Type"] == "Forage") & 
                (feed_library["Fd_Name"].str.contains("Straw", case=False, na=False))
            ]
            forage_options = pd.concat([hay_options, straw_options])
            forage = forage_options.sample(1)
            feed_name = forage["Fd_Name"].values[0]
            select_feeds[feed_name] = "Hay"
            # if not hay_options.empty and not straw_options.empty:
                # second_forage = hay_options.sample(n=1) if random.choice([True, False]) else straw_options.sample(n=1)
            # elif not hay_options.empty:
            #     second_forage = hay_options.sample(n=1)
            # elif not straw_options.empty:
            #     second_forage = straw_options.sample(n=1)
            # else:
            #     second_forage = pd.DataFrame()  # fallback in case both are missing


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


def assign_weights(selected_feeds: dict, feed_options: dict, total_intake: int) -> dict:
    diet_data = { 
        "Feedstuff": [],
        "kg_user": []
    }
    for feed_name, feed_type in selected_feeds.items():
        diet_data["Feedstuff"].append(feed_name)
        feed_weight = random.uniform(feed_options[feed_type][0], feed_options[feed_type][1]) * total_intake
        diet_data["kg_user"].append(feed_weight)
    
        # NOTE: Need to scale the kg_user column, see the notes below
        # diet_data["kg_user"] = diet_data["kg_user"] * x

        # values = [5, 10 , 5]

        # expected_total = 25
        # actual_total = sum(values) = 20

        # what is x?
        # (5 * x) + (10*x) + (5*x) = 25
    return diet_data


def create_diet(feed_library: pd.DataFrame, feed_options: dict, total_intake: float = 25):
    feeds_to_choose_from = feed_options.keys()
    selected_feeds = select_feeds(feed_library, feeds_to_choose_from)
    # print(selected_feeds)
    diet_data = assign_weights(selected_feeds, feed_options, total_intake)
    diet = pd.DataFrame(diet_data)
    return diet


if __name__ == "__main__":
    feed_library = pd.read_csv(
        os.path.join(os.path.dirname(__file__),
                    # "../../src/nasem_dairy/data/feed_library/NASEM_feed_library.csv")
                    "../data/melanie_feed.csv")
        )
    # print(feed_library)  

    feed_options = {
        "Silage": (0.3, 0.6), #this is a range 30%-60 ; example
        "Hay": (0.2, 0.3),
        "Energy": (0.2, 0.3),
        "Fat Supp.": (0.05, 0.1),
        "Protein Supp.": (0.1, 0.2)
    }
    diet = create_diet(feed_library, feed_options, 25.0)
    output = nd.nasem(diet, animal_input, equation_selection)
    print(f"Created Diet: {diet}")
    print(f"Sum of Diet: {sum(diet['kg_user'])}")
    print(f"Milk Fat: {output.get_value('MlkFat_Milk') * 100}%")
    print(f"Milk Protein: {output.get_value('MlkNP_Milk') * 100}%")

    # diet, animal, equations, _ = nd.demo("lactating_cow_test")
    # output = nd.nasem(
    #     diet, animal, equations
    # )
    # print(output)
    # print(output.search("Fat"))
    # print(output.export_to_JSON("demo_diet.json"))
    # print(output.get_value("Mlk_Fat_g"))

    print("Script finished running")
