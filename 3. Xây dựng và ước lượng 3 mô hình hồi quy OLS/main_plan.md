## task (theo thứ tự)

### 1. Xử lý dữ liệu (Data Cleaning)
- Drop duplicates: 243/669 rows bị trùng → còn 426 obs (hoặc giữ nguyên 669 nếu muốn đại diện tốt hơn, cần giải thích lý do)
- Chuẩn hóa Education Level: gộp 7 giá trị lộn xộn về 4 nhóm chuẩn:
  - "Bachelor's Degree" + "Bachelor's" → Bachelor
  - "Master's Degree" + "Master's" → Master
  - "PhD" + "phD" → PhD
  - "High School" giữ nguyên
- Tạo biến bổ sung: lnSalary = log(Salary), Age², biến tương tác Education × Experience

### 2. Thống kê mô tả (Descriptive Statistics)
- Mean, SD, min/max cho Age, Experience, Salary
- Phân phối Gender và Education Level
- Ma trận tương quan (chú ý Age và Experience tương quan cao → nguy cơ đa cộng tuyến)
- Biểu đồ: scatter plot, boxplot theo nhóm

### 3. Xây dựng và ước lượng 3 mô hình hồi quy OLS

| Model | Dạng | Biến phụ thuộc | Biến độc lập |
|-------|------|----------------|--------------|
| 1 | Level-Level | Salary | Age, Gender, Education, Experience |
| 2 | Log-Level | ln(Salary) | Age, Gender, Education, Experience |
| 3 | Log-Level mở rộng | ln(Salary) | Age, Age², Gender, Education, Experience, Education×Experience |

Base category: Education = High School, Gender = Female

### 4. Kiểm định giả định mô hình (Diagnostics)
- VIF → kiểm tra đa cộng tuyến (đặc biệt khi dùng cả Age + Experience)
- Breusch-Pagan test → kiểm tra phương sai sai số thay đổi (heteroskedasticity)
- Nếu có heteroskedasticity → dùng robust standard errors (HC1/HC3)
- QQ-plot / Jarque-Bera → kiểm tra phân phối phần dư

### 5. Viết báo cáo theo cấu trúc 3.a–3.h
- **3.a Introduction** — mục tiêu, phạm vi nghiên cứu
- **3.b Theoretical Background** — Human Capital Theory (Becker 1964, Mincer 1974), Mincer wage equation
- **3.c Model Specification & Hypotheses** — đặt giả thuyết kỳ vọng cho từng biến
- **3.d Descriptive Statistics** — bảng thống kê + biểu đồ
- **3.e Model Estimation & Interpretation** — bảng kết quả 3 mô hình, diễn giải hệ số
- **3.f Diagnostic Checks** — bảng kiểm định, xử lý vi phạm
- **3.g Comments & Recommendations** — hạn chế, hàm ý chính sách
- **3.h References** — APA format (Wooldridge, Mincer, Becker, Blau & Kahn...)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Lưu ý quan trọng

- Khi dùng cả Age và Experience cùng lúc: VIF ~8.4 → cần giải thích hoặc chọn 1 trong 2, hoặc dùng robust SE
- Gender không significant ở Model 1 & 2, nhưng significant (p=0.013) khi kiểm soát Experience → đây là điểm thú vị để thảo luận về gender pay gap
- Model 2 (log-linear) được khuyến nghị làm mô hình chính vì R² tốt hơn và hệ số dễ diễn giải theo %
- Đính kèm code R vào phụ lục báo cáo