import pandas as pd
import plotnine as pn
import numpy as np


if __name__ == "__main__":
    df = pd.read_csv("./100000_diets.csv")    
    # print(df.head(5))
    df["protein_fat_ratio"] = df["Mlk_Fat_g"] / df["Mlk_NP_g"]
    
    # Print descriptive statistics
    print("Statistics for protein-fat ratio:")
    print(df["protein_fat_ratio"].describe())
    
    # NOTE: Histogram of Protein Fat Ratio
    # hist_plot = (pn.ggplot(df, pn.aes(x="protein_fat_ratio"))
    #         + pn.geom_histogram(
    #             bins=50, # NOTE: can play around with this number
    #             fill="steelblue",
    #             color="black"
    #             )
    #         + pn.labs(title="Distribution of Protein-Fat Ratio", 
    #                     x="Protein-Fat Ratio (Mlk_Fat_g / Mlk_NP_g)", 
    #                     y="Count")
    #     )
    
    # hist_plot.save("./melanie_plots/protein_fat_ratio_histogram.png", width=10, height=6, dpi=300)
    


    # NOTE: Scatterplot of fat vs protein
    # scatter_plot_fat_vs_protein = (pn.ggplot(df, pn.aes(
    #     x="Mlk_NP_g", 
    #     y="Mlk_Fat_g", 
    #     color="Dt_CP" # NOTE Change this to another column name ex, Dt_CP
    #     ))
    #               + pn.geom_point(alpha=0.7)
    #               + pn.scale_color_gradient(low="blue", high="red")
    #               + pn.labs(title="Milk Protein vs Fat Content",
    #                        x="Milk Protein (g)",
    #                        y="Milk Fat (g)",
    #                        color="Diet CP %" # NOTE Change the legend title
    #                        )
    #             )
    # scatter_plot_fat_vs_protein.save("./melanie_plots/protein_vs_fat_scatter.png", width=16, height=12, dpi=300)



    # NOTE: Scatterplot ratio vs diet id
    # df["diet_id"] = df.index
    # scatter_plot_ratio_vs_diet_id = (pn.ggplot(df, pn.aes(x="diet_id", y="protein_fat_ratio"))
    #               + pn.geom_point(alpha=0.7)
    #               + pn.labs(title="Protein-Fat Ratio vs Diet ID",
    #                        x="Diet ID",
    #                        y="Protein-Fat Ratio")
    #             )
    # scatter_plot_ratio_vs_diet_id.save("./melanie_plots/ratio_vs_diet_id_scatter.png", width=10, height=8, dpi=300)



    # NOTE: Subset top and bottom 10%
    low_cutoff = df["protein_fat_ratio"].quantile(0.1)
    high_cutoff = df["protein_fat_ratio"].quantile(0.9)
    subset_df = df.copy()
    subset_df.loc[subset_df["protein_fat_ratio"] <= low_cutoff, "ratio_group"] = "bottom 10%"
    subset_df.loc[subset_df["protein_fat_ratio"] >= high_cutoff, "ratio_group"] = "top 10%"
    subset_df = subset_df[subset_df["ratio_group"].isin(["top 10%", "bottom 10%"])]



    # NOTE: Scatterplot coloured by ratio group
    scatter_plot_extremes = (pn.ggplot(subset_df, pn.aes(
        x="Mlk_NP_g", 
        y="Mlk_Fat_g", 
        color="ratio_group" 
        ))
                  + pn.geom_point(alpha=0.7)
                  + pn.scale_color_manual(values={"top 10%": "red", "bottom 10%": "blue"})
                  + pn.labs(title="Milk Protein vs Fat Content",
                           x="Milk Protein (g)",
                           y="Milk Fat (g)",
                           color="Ratio Group")
                  )
    scatter_plot_extremes.save("./melanie_plots/protein_vs_fat_extremes.png", width=16, height=12, dpi=300)



    # NOTE: Scatterplot coloured by nutrient
    scatter_plot_extremes = (pn.ggplot(subset_df, pn.aes(
        x="Mlk_NP_g", 
        y="Mlk_Fat_g", 
        color="Dt_CP" # NOTE: Change this value to another column name ex, Dt_CP
        ))
                  + pn.geom_point(alpha=0.7)
                  + pn.labs(title="Milk Protein vs Fat Content",
                           x="Milk Protein (g)",
                           y="Milk Fat (g)",
                           color="Diet CP %") # NOTE: Change the legend title
                  )
    scatter_plot_extremes.save("./melanie_plots/protein_vs_fat_CP.png", width=16, height=12, dpi=300)
