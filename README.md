# Hướng dẫn hoàn thiện báo cáo kinh tế lượng

Sườn báo cáo đã có tại `part5_report_3_1_3_8.md`. File này hướng dẫn những gì cần **bổ sung thêm** để đạt chuẩn học thuật.

---

## Nguồn số liệu chính xác để điền vào báo cáo

| Cần gì | Lấy từ file nào |
|---|---|
| Thống kê mô tả (mean, sd, min, max) | `2.Descriptive Statistics/outputs/descriptive_stats.csv` |
| Phân phối Gender, Education | `gender_distribution.csv`, `education_distribution.csv` |
| Ma trận tương quan | `correlation_matrix.csv` |
| Hệ số hồi quy 3 mô hình (HC3, hybrid) | `3. .../outputs/all_models_coefficients_hc3_hybrid.csv` |
| R², Adj-R², AIC, BIC | `model_fit_stats_hc3_hybrid.csv` |
| VIF | `4. .../outputs/vif_table.csv` |
| Breusch-Pagan | `breusch_pagan_results.csv` |
| Jarque-Bera | `jarque_bera_results.csv` |

---

## Những phần còn thiếu cần bổ sung

### 3.4 — Bảng thống kê mô tả (cần thêm bảng đẹp)

Thay đoạn text bằng bảng chuẩn học thuật:

| Variable | Mean | Std. Dev. | Min | Max |
|---|---|---|---|---|
| Age | 33.92 | 7.74 | 21 | 60 |
| Years of Experience | 8.46 | 6.50 | 0 | 34 |
| Salary (USD) | 114,572 | 53,046 | 350 | 240,000 |

*N = 426 (trước khi loại outlier). Nguồn: `descriptive_stats.csv`.*

**Bảng phân phối nhóm:**

| Education Level | n | % |
|---|---|---|
| Bachelor | 182 | 42.72% |
| Master | 124 | 29.11% |
| PhD | 86 | 20.19% |
| High School | 34 | 7.98% |

| Gender | n | % |
|---|---|---|
| Male | 231 | 54.23% |
| Female | 194 | 45.54% |
| Other | 1 | 0.23% |

**Bảng ma trận tương quan:**

| | Age | Experience | Salary | ln(Salary) |
|---|---|---|---|---|
| Age | 1.000 | | | |
| Experience | **0.939** | 1.000 | | |
| Salary | 0.720 | 0.791 | 1.000 | |
| ln(Salary) | 0.624 | 0.696 | 0.909 | 1.000 |

> Lưu ý: Corr(Age, Experience) = 0.939 → cảnh báo đa cộng tuyến.

**Hình minh họa cần chèn:**
- `2.Descriptive Statistics/outputs/scatter_age_salary.png` — Scatter: Salary vs Age
- `2.Descriptive Statistics/outputs/scatter_experience_salary.png` — Scatter: Salary vs Experience
- `2.Descriptive Statistics/outputs/boxplot_salary_by_education.png` — Boxplot theo Education
- `2.Descriptive Statistics/outputs/boxplot_salary_by_gender.png` — Boxplot theo Gender

---

### 3.5 — Bảng kết quả hồi quy (QUAN TRỌNG — phần hay bị thiếu nhất)

Cần trình bày bảng so sánh 3 mô hình cùng lúc theo chuẩn kinh tế lượng:

| | Model 1 (Level-Level) | Model 2 (Log-Level) | Model 3 (Log-Level Extended) |
|---|---|---|---|
| **Intercept** | 63,493.00*** | 10.719*** | 10.264*** |
| **Age** | −1,593.65** | −0.0158*** | — |
| **Age_c** | — | — | −0.0078 |
| **Age2_c** | — | — | −0.0009*** |
| **Experience** | 7,182.80*** | 0.0691*** | 0.0827*** |
| **Male** | 5,602.15. | 0.0629** | 0.0549. |
| **Other** | −26,771.07 | 0.1073 | −0.1600 |
| **Bachelor** | 36,908.32*** | 0.6943*** | 0.6185*** |
| **Master** | 48,751.38*** | 0.8468*** | 0.8575*** |
| **PhD** | 57,442.79*** | 0.8554*** | 1.0627*** |
| **Exp × Bachelor** | — | — | −0.0034 |
| **Exp × Master** | — | — | −0.0199*** |
| **Exp × PhD** | — | — | −0.0291*** |
| **R²** | 0.6968 | 0.7133 | 0.7485 |
| **Adj. R²** | 0.6917 | 0.7085 | 0.7418 |
| **AIC** | 9,957.4 | 189.2 | 141.6 |
| **N** | 425 | 425 | 425 |

*Ghi chú: `***` p<0.001, `**` p<0.01, `*` p<0.05, `.` p<0.1. SE dùng HC3 robust. Base: Female, High School.*
*Nguồn: `all_models_coefficients_hc3_hybrid.csv`, `model_fit_stats_hc3_hybrid.csv`.*

**Diễn giải mẫu chuẩn cho Model 2 (nên dùng làm mô hình chính):**

- **Experience**: β = 0.0691 → mỗi năm kinh nghiệm tăng thêm liên quan đến mức lương cao hơn khoảng **6.91%**, ceteris paribus (p < 0.001).
- **Male**: β = 0.0629 → nam giới có mức lương cao hơn nữ giới khoảng **exp(0.0629) − 1 ≈ 6.5%**, ceteris paribus (p = 0.039).
- **Bachelor**: β = 0.6943 → so với nhóm High School, nhóm Bachelor có mức lương cao hơn khoảng **exp(0.6943) − 1 ≈ 100.2%** (p < 0.001).
- **Master**: β = 0.8468 → cao hơn High School khoảng **exp(0.8468) − 1 ≈ 132.9%** (p < 0.001).
- **PhD**: β = 0.8554 → cao hơn High School khoảng **exp(0.8554) − 1 ≈ 135.2%** (p < 0.001).
- **Age**: β = −0.0158 → âm nhưng cần đọc cùng VIF (8.69) — dấu có thể bị lệch do đa cộng tuyến với Experience.

---

### 3.6 — Bảng kiểm định (cần thêm bảng số liệu)

**Bảng VIF (chỉ các biến quan trọng):**

| Variable | Model 1 | Model 2 | Model 3 |
|---|---|---|---|
| Age / Age_c | 8.69 | 8.69 | 9.22 |
| Experience | 8.80 | 8.80 | 24.21 |
| Age2_c | — | — | **2.38** ✓ |
| Exp × PhD | — | — | 27.95 |
| Exp × Master | — | — | 14.98 |
| Exp × Bachelor | — | — | 9.93 |

*Nguồn: `vif_table.csv`.*

**Bảng Breusch-Pagan:**

| Model | LM stat | p-value | Kết luận |
|---|---|---|---|
| Model 1 | 46.82 | < 0.001 | Có heteroskedasticity |
| Model 2 | 47.16 | < 0.001 | Có heteroskedasticity |
| Model 3 | 83.88 | < 0.001 | Có heteroskedasticity |

→ Tất cả 3 mô hình vi phạm giả định phương sai đồng đều → **dùng HC3 robust SE**.

**Bảng Jarque-Bera:**

| Model | JB stat | p-value | Skew | Kurtosis | Kết luận |
|---|---|---|---|---|---|
| Model 1 | 24.98 | < 0.001 | 0.583 | 3.224 | Bác bỏ normality |
| Model 2 | 0.18 | 0.912 | −0.040 | 3.062 | **Không bác bỏ** ✓ |
| Model 3 | 8.82 | 0.012 | 0.338 | 3.199 | Bác bỏ normality |

*Nguồn: `jarque_bera_results.csv`.*

**Hình minh họa cần chèn:**
- `4. .../outputs/qqplot_model1_level_level.png`
- `4. .../outputs/qqplot_model2_log_level.png`
- `4. .../outputs/qqplot_model3_log_level_extended.png`

> Với n = 425, vi phạm normality ở Model 1 và 3 ít nghiêm trọng hơn do Central Limit Theorem — nên ghi chú điều này trong báo cáo.

---

### Các phần khác thường có trong báo cáo kinh tế lượng nhưng hiện chưa có

**1. Residual vs Fitted plot** (kiểm tra heteroskedasticity trực quan)

Cần thêm vào Part 4 script hoặc vẽ tay:
```python
import matplotlib.pyplot as plt
fitted = result.fittedvalues
resid = result.resid
plt.scatter(fitted, resid, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Fitted values")
plt.ylabel("Residuals")
plt.title("Residuals vs Fitted — Model 2")
plt.tight_layout()
plt.savefig("resid_vs_fitted_model2.png", dpi=150)
```

**2. Bảng so sánh nonrobust vs HC3 SE** (minh bạch inference)

Nên có 1 bảng nhỏ cho Model 1 (mô hình bị heteroskedasticity nặng nhất) so sánh SE trước và sau khi dùng HC3, để thấy rõ tác động.

**3. Footnote về outlier**

Trong phần 3.4 hoặc 3.5, cần có footnote:
> "Một quan sát có Salary = $350 được xác định là outlier cực trị theo quy tắc hybrid (IQR + log modified z-score). Phân tích chính được thực hiện trên n = 425 sau khi loại quan sát này. Kết quả trên n = 426 (giữ nguyên outlier) không thay đổi đáng kể về dấu và mức ý nghĩa của các hệ số chính."

**4. Phần phụ lục (Appendix)**

Chuẩn học thuật thường có:
- Appendix A: Full regression output (statsmodels summary) — lấy từ `model2_log_level_summary_hc3_hybrid.txt`
- Appendix B: Outlier report — lấy từ `salary_outlier_report.csv`
- Appendix C: Python code (các file `.py` của 4 parts)

---

## Checklist trước khi nộp

- [ ] Chuyển toàn bộ `part5_report_3_1_3_8.md` sang tiếng Việt có dấu
- [ ] Chèn 4 biểu đồ từ Part 2 vào mục 3.4
- [ ] Chèn 3 QQ-plot từ Part 4 vào mục 3.6
- [ ] Thêm Residual vs Fitted plot cho Model 2
- [ ] Thay text thống kê mô tả bằng bảng chuẩn (xem mục 3.4 ở trên)
- [ ] Thêm bảng kết quả hồi quy 3 mô hình (xem mục 3.5 ở trên)
- [ ] Thêm bảng VIF, BP, JB với số liệu thực (xem mục 3.6 ở trên)
- [ ] Thêm footnote về outlier Salary = $350
- [ ] Thêm phụ lục code Python
- [ ] Kiểm tra format tài liệu tham khảo APA (3.8)
- [ ] Đảm bảo tất cả số liệu trong báo cáo lấy từ run `hc3_hybrid` (n = 425)
