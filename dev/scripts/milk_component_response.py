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
                    "../../src/nasem_dairy/data/feed_library/NASEM_feed_library.csv")
                    # "../data/melanie_feed.csv")
        )
    # print(feed_library)


    def create_diet(feed_library: pd.DataFrame, total_intake: float):
        diet_data = { 
            "Feedstuff": [],
            "kg_user": []
        }
        index = 0
        feed_options = {
            "Silage": (0.3, 0.6), #this is a range 30%-60 ; example)
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
