import nasem_dairy as nd

if __name__ == "__main__":
    ### Run Analysis ###
    value_ranges = {
        "CP_GrUtWt": [0.1, 0.5],
        "K_305RHA_MlkTP": [0.1, 2],
        "Kl_ME_NE": [0.1, 5],
    }
    
    analyzer = nd.SensitivityAnalyzer("./dev/data/new_sensitivity.db")
    analyzer.run_sensitivity(
        value_ranges=value_ranges, 
        num_samples=4, 
        input_path="./src/nasem_dairy/data/demo/lactating_cow_test.json",
        feed_library_path="./src/nasem_dairy/data/feed_library/NASEM_feed_library.csv"
        # save_full_output=True
    )
    

    ### View Outputs ###
    problem_id = 1
    response_variable = 'Mlk_Prod'

    # # 1. View all problems
    problems_df = analyzer.get_all_problems()
    print(problems_df)

    # # 2. Get samples for a specific problem
    # samples_df = analyzer.get_samples_for_problem(problem_id)
    # print(samples_df)

    # # 3. Get a specific response variable
    # variable_name = 'Mlk_Prod'
    # response_df = analyzer.get_response_variables(problem_id, variable_name)
    # print(response_df)

    # # 4. Get problem details
    # details_df = analyzer.get_problem_details(problem_id)
    # print(details_df)

    # # 5. Get multiple response variables
    # variable_names = ['Mlk_Prod', 'An_MEuse', 'CH4out_g']
    # responses_df = analyzer.get_response_variables(problem_id, variable_names)
    # print(responses_df)

    # # 6. Get summary statistics for response variables
    # summary_df = analyzer.get_response_variable_summary(problem_id)
    # print(summary_df)

    # # 7. List available response variables
    # available_variables = analyzer.list_response_variables()
    # print(available_variables)

    # 8. Get problems that use a given coefficient
    # print(analyzer.get_problems_by_coefficient("K_305RHA_MlkTP"))

    # 9. Get the coefficients used for a given problem
    # print(analyzer.get_coefficients_by_problem(problem_id))

    ### Perform Analysis ###
    # results_df = analyzer.analyze(
    #     problem_id,
    #     response_variable
    # )

    # View results
    # print(results_df)
