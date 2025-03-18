import os

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

if __name__ == "__main__":


    feed_library = pd.read_csv(
        os.path.join(os.path.dirname(__file__),
                    # "../../src/nasem_dairy/data/feed_library/NASEM_feed_library.csv")
                    "../data/melanie_feed.csv")
        )
    print(feed_library)


    def create_diet(feed_library: pd.DataFrame, total_intake: float = 25):
        diet_data = { 
            "Feedstuff": [],
            "kg_user": []
        }
    
    diet_data["Feedstuff"].extend(silage["Fd_Name"].values)
    diet_data["kg_user"].extend([forage_weights[0]])

    if not second_forage.empty:
        diet_data["Feedstuff"].extend(second_forage["Fd_Name"].values)
        diet_data["kg_user"].extend([forage_weights[1]])

    diet_data["Feedstuff"].append(energy_conc["Fd_Name"].values[0])
    diet_data["kg_user"].append(energy_weight)

    diet_data["Feedstuff"].append(fat_supp["Fd_Name"].values[0])
    diet_data["kg_user"].append(fat_weight)

    diet_data["Feedstuff"].append(protein_supp["Fd_Name"].values[0])
    diet_data["kg_user"].append(protein_weight)

        index = 0
        feed_options = {
            "Silage": (0.3, 0.6), #this is a range 30%-60 ; example
            "Hay": 0.2,
            "Energy": 0.2,
            "Fat Supp.": 0.05,
            "Protein Supp.": 0.1
        }
        while sum(diet_data["kg_user"]) < total_intake:
            random_feed = feed_library["Fd_Name"]. sample(n=1).values[0]
            diet_data["Feedstuff"].append(random_feed)
            diet_data["kg_user"].append(total_intake * feed_options [index]) #edit this to make sure it doesnt go over total intake
            index += 1
        
    # 1. select ONE silage (must include "Silage" in Fd_Name)
    silage_options = feed_library[
        (feed_library["Fd_Type"] == "Forage") & 
        (feed_library["Fd_Name"].str.contains("Silage", case=False, na=False))
    ]
    
    if not silage_options.empty:
        silage = silage_options.sample(n=1)
    else:
        raise ValueError("No silage options available in feed library.")

    # 2. select ONE from hay OR straw (but not both)
    hay_options = feed_library[
        (feed_library["Fd_Type"] == "Forage") & 
        (feed_library["Fd_Name"].str.contains("Hay", case=False, na=False))
    ]

    straw_options = feed_library[
        (feed_library["Fd_Type"] == "Forage") & 
        (feed_library["Fd_Name"].str.contains("Straw", case=False, na=False))
    ]

    if not hay_options.empty and not straw_options.empty:
        second_forage = hay_options.sample(n=1) if random.choice([True, False]) else straw_options.sample(n=1)
    elif not hay_options.empty:
        second_forage = hay_options.sample(n=1)
    elif not straw_options.empty:
        second_forage = straw_options.sample(n=1)
    else:
        second_forage = pd.DataFrame()  # fallback in case both are missing

    # select concentrates
    energy_conc = feed_library[
        (feed_library["Fd_Type"] == "Concentrate") & 
        (feed_library["Fd_Category"].str.contains("Energy", case=False, na=False))
    ].sample(n=1)

    fat_supp = feed_library[
        (feed_library["Fd_Type"] == "Concentrate") & 
        (feed_library["Fd_Category"].str.contains("Fat", case=False, na=False))
    ].sample(n=1)

    protein_supp = feed_library[
        (feed_library["Fd_Type"] == "Concentrate") & 
        (feed_library["Fd_Category"].str.contains("Protein", case=False, na=False))
    ].sample(n=1)

    # combine selected feeds
    selected_feeds = pd.concat([silage, second_forage, energy_conc, fat_supp, protein_supp])

    # assign proportional intake weights
    forage_weight = random.uniform(feed_options["Forage"][0], feed_options["Forage"][1]) * total_intake
    energy_weight = feed_options["Energy"] * total_intake
    fat_weight = feed_options["Fat Supp."] * total_intake
    protein_weight = feed_options["Protein Supp."] * total_intake

    # distribute weight between silage and the second forage
    num_forage = len([silage, second_forage])
    forage_weights = [forage_weight / num_forage] * num_forage

    diet = pd.DataFrame(diet_data)
    return diet
    

    diet = create_diet(feed_library, 25.0)
    output = nd.nasem(diet, animal_input, equation_selection)
    print(diet)
    print(output)

    # diet, animal, equations, _ = nd.demo("lactating_cow_test")
    # output = nd.nasem(
    #     diet, animal, equations
    # )
    # print(output)
    # print(output.search("Fat"))
    # print(output.export_to_JSON("demo_diet.json"))
    # print(output.get_value("Mlk_Fat_g"))

    # print(diet)
