### 3. Xây dựng và ước lượng 3 mô hình hồi quy OLS

| Model | Dạng | Biến phụ thuộc | Biến độc lập |
|-------|------|----------------|--------------|
| 1 | Level-Level | Salary | Age, Gender, Education, Experience |
| 2 | Log-Level | ln(Salary) | Age, Gender, Education, Experience |
| 3 | Log-Level mở rộng | ln(Salary) | Age_c, Age2_c, Gender, Education, Experience, Education×Experience |

Base category: Education = High School, Gender = Female

- [x] Da uoc luong du 3 mo hinh OLS bang Python (statsmodels)
- [x] Da xuat he so tung mo hinh: outputs/model1_level_level_coefficients.csv, outputs/model2_log_level_coefficients.csv, outputs/model3_log_level_extended_coefficients.csv
- [x] Da xuat bang tong hop he so: outputs/all_models_coefficients.csv
- [x] Da xuat thong ke do phu hop mo hinh: outputs/model_fit_stats.csv
- [x] Da xuat full summary text cua moi mo hinh va tom tat markdown: outputs/*_summary.txt, outputs/part3_summary.md
- [x] Da bo sung tuy chon robust SE cho script Part 3 (--cov-type: nonrobust, HC1, HC3) va xuat bo ket qua rieng theo tung covariance type
- [x] Da bo sung outlier handling cho Salary truoc khi uoc luong (--outlier-mode: none, iqr, hybrid)
- [x] Da bo sung bien center cho Model 3 (Age_c, Age2_c) de giam structural multicollinearity
- [x] Default outlier mode cua Part 3 da dong bo voi Part 4: hybrid (tranh lech so obs khi chay mac dinh)
Những gì đã ổn:
- --cov-type option hoạt động đúng: nonrobust / HC1 / HC3
- --outlier-mode option hoat dong dung: none / iqr / hybrid
- Output files tự động thêm suffix theo run (_hc3.csv, _hc3_hybrid.csv, ...) -> không ghi đè kết quả cũ
- coefficient_table() đã dùng np.asarray() để tránh lỗi khi result là 
robust wrapper
- model_stats_table() dùng getattr an toàn hơn

Một điểm nhỏ cần lưu ý:

Khi dùng --cov-type HC3, result.aic và result.bic trong model_stats_table 
vẫn lấy từ robust result object — nhưng AIC/BIC của robust SE về mặt lý 
thuyết không thay đổi (vì chỉ SE thay đổi, không phải log-likelihood). 
Statsmodels xử lý đúng điều này, nên không có vấn đề.

Workflow sử dụng đúng sẽ là:
```bash
# Bước 1: chạy nonrobust trước (mặc định)
python part3_ols_models.py

# Bước 2: sau khi Part 4 xác nhận có heteroskedasticity -> chạy lại với HC3
python part3_ols_models.py --cov-type HC3

# Bước 3 (khuyen nghi): chay sensitivity voi outlier handling + HC3
python part3_ols_models.py --outlier-mode hybrid --cov-type HC3
```