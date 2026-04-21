# Part 4 - Diagnostics Summary

- Input data: Group13_DSEB66A_part1_cleaned.xlsx
- Number of observations (before outlier handling): 426
- Number of observations (after outlier handling): 425
- Salary outlier mode: hybrid
- Alpha level: 5%

## Key Findings
- Salary outlier detection (IQR rule): 0 outlier(s), including 0 low and 0 high outlier(s).
- Salary outlier detection (log modified z-score): 1 outlier(s). Hybrid flagged outliers: 1.
- Model 3 uses centered age terms (Age_c, Age2_c) to reduce structural multicollinearity.
- VIF: High multicollinearity exists for variables listed below (VIF >= 8).
```text
                    model                                                           variable       vif
       model1_level_level                                           Q('Years of Experience')  8.801253
       model1_level_level                                                                Age  8.692773
         model2_log_level                                           Q('Years of Experience')  8.801253
         model2_log_level                                                                Age  8.692773
model3_log_level_extended                                                          Exp_x_PhD 27.953591
model3_log_level_extended                                           Q('Years of Experience') 24.214560
model3_log_level_extended                                                       Exp_x_Master 14.980954
model3_log_level_extended C(Q('Education Level'), Treatment(reference='High School'))[T.PhD] 10.179130
model3_log_level_extended                                                     Exp_x_Bachelor  9.929415
model3_log_level_extended                                                              Age_c  9.214786
```
- Breusch-Pagan: Heteroskedasticity detected in model(s): model1_level_level, model2_log_level, model3_log_level_extended
- Recommendation: Use HC3 robust standard errors for inference.
- Jarque-Bera: Residual normality rejected in model(s): model1_level_level, model3_log_level_extended

## Output Files
- vif_table.csv
- breusch_pagan_results.csv
- jarque_bera_results.csv
- all_models_coefficients_nonrobust.csv
- all_models_coefficients_hc3.csv
- salary_outlier_report.csv
- qqplot_model1_level_level.png
- qqplot_model2_log_level.png
- qqplot_model3_log_level_extended.png