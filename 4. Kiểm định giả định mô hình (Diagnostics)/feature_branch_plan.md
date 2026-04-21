### 4. Kiểm định giả định mô hình (Diagnostics)
- [x] VIF → kiểm tra đa cộng tuyến (đặc biệt khi dùng cả Age + Experience) -> outputs/vif_table.csv
- [x] Breusch-Pagan test → kiểm tra phương sai sai số thay đổi (heteroskedasticity) -> outputs/breusch_pagan_results.csv
- [x] Nếu có heteroskedasticity → dùng robust standard errors (HC1/HC3) -> outputs/all_models_coefficients_hc3.csv
- [x] QQ-plot / Jarque-Bera → kiểm tra phân phối phần dư -> outputs/qqplot_*.png, outputs/jarque_bera_results.csv

Ket qua chinh de dua vao bao cao 3.f:
- Da bo sung outlier detection cho Salary (hybrid: IQR + log modified z-score) -> outputs/salary_outlier_report.csv
- Da center Age cho Model 3 (Age_c, Age2_c) de giam structural multicollinearity.
- VIF Model 1-2: Age va Experience van cao (~8.7-8.8). VIF Model 3 cua Age2_c da giam manh (xuong ~2.38), nhung da cong tuyen van ton tai do Experience va interaction terms.
- Breusch-Pagan: heteroskedasticity phat hien o ca 3 model (f_p_value < 0.05) sau khi xu ly outlier.
- Jarque-Bera: Model 2 khong bac bo normality sau khi loai outlier cuc tri; Model 1 va 3 van bac bo normality.
- Khuyen nghi su dung HC3 robust SE cho suy luan thong ke o tat ca model.

> nhắc lại chú ý part 3 :
 Một điểm nhỏ cần lưu ý:

Khi dùng --cov-type HC3, result.aic và result.bic trong model_stats_table 
vẫn lấy từ robust result object — nhưng AIC/BIC của robust SE về mặt lý 
thuyết không thay đổi (vì chỉ SE thay đổi, không phải log-likelihood). 
Statsmodels xử lý đúng điều này, nên không có vấn đề.

Workflow sử dụng đúng sẽ là:
```bash
# Bước 1: chạy nonrobust trước (mặc định)
python part3_ols_models.py

# Bước 2: chay diagnostics co xu ly outlier + centered age
python part4_diagnostics.py --outlier-mode hybrid

# Bước 3: chay lai uoc luong voi HC3 va cung mode outlier
python part3_ols_models.py --outlier-mode hybrid --cov-type HC3
```