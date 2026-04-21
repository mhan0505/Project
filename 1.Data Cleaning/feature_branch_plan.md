### 1. Xử lý dữ liệu (Data Cleaning)
- Drop duplicates: 243/669 rows bị trùng → còn 426 obs (hoặc giữ nguyên 669 nếu muốn đại diện tốt hơn, cần giải thích lý do)
- Chuẩn hóa Education Level: gộp 7 giá trị lộn xộn về 4 nhóm chuẩn:
  - "Bachelor's Degree" + "Bachelor's" → Bachelor
  - "Master's Degree" + "Master's" → Master
  - "PhD" + "phD" → PhD
  - "High School" giữ nguyên
- Tạo biến bổ sung: lnSalary = log(Salary), Age², biến tương tác Education × Experience