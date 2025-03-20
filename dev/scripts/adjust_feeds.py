import nasem_dairy as nd

if __name__ == "__main__":
    diet, animal, equation, _ = nd.demo("lactating_cow_test")
    feed_library = nd.select_feeds([
        "Alfalfa meal",
        "Canola meal",
        "Corn silage, typical",
        "Corn grain HM, coarse grind"
      ])
    expected_diet = {
        "Dt_CP": 24.0,
        "Dt_NDF": 31.0,
        "Dt_ADF": 24.0,
        "Dt_CFat": 3.5,
        "Dt_St": 25.0,
    }
    nutrients_to_adjust = [
        ("Fd_CP", "Dt_CP"), 
        ("Fd_NDF", "Dt_NDF"), 
        ("Fd_ADF", "Dt_ADF"), 
        ("Fd_CFat", "Dt_CFat"), 
        ("Fd_St", "Dt_St")
    ]
    original_output = nd.nasem(
        diet, animal, equation, feed_library=feed_library
    )
    adjusted_feed_library, adjustments = nd.adjust_diet(
        animal, equation, diet, expected_diet, nutrients_to_adjust, feed_library
    )
    adjusted_output = nd.nasem(
        diet, animal, equation, feed_library=adjusted_feed_library
    )

    for _, output in nutrients_to_adjust:
        print(f"{output} (Original Feed Library): {original_output.get_value(output)}")
        print(f"{output} (Modified Feed Library): {adjusted_output.get_value(output)}")
        print(f"Target {output}: {expected_diet[output]}\n")
    print(adjustments)
