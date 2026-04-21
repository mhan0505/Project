# Bao cao 3.1-3.8: Phan tich yeu to anh huong den Salary

## 3.1 Introduction of your work
Muc tieu cua nghien cuu la dinh luong tac dong cua tuoi (Age), gioi tinh (Gender), trinh do hoc van (Education Level), va kinh nghiem (Years of Experience) den muc luong (Salary).

Pham vi du lieu su dung la bo Group13_DSEB66A_part1_cleaned.xlsx sau khi xu ly du lieu Part 1. Trong quy trinh diagnostics, nghien cuu phat hien 1 quan sat luong cuc tri (Salary = 350) theo quy tac hybrid outlier va thuc hien sensitivity analysis voi mau 425 quan sat (tu 426 ban dau).

## 3.2 Reviewing theoretical background and methods
Nghien cuu dua tren Human Capital Theory (Becker, 1964) va ham tien luong Mincer (Mincer, 1974), trong do thu nhap phan anh tich luy von nhan luc qua giao duc va kinh nghiem.

Dang tong quat cua mo hinh Mincer:

ln(Salary_i) = beta_0 + beta_1 Education_i + beta_2 Experience_i + beta_3 Experience_i^2 + u_i

Trong bo du lieu nay, Education duoc mo hinh hoa bang bien gia (dummy) theo tung nhom hoc van; Experience duoc giu o dang muc do nam kinh nghiem; Age duoc dua vao de bat nhung khac biet vong doi lao dong.

## 3.3 Model specification and hypotheses
Ba mo hinh OLS da uoc luong:

- Model 1 (Level-Level): Salary ~ Age + Experience + Gender + Education
- Model 2 (Log-Level): lnSalary ~ Age + Experience + Gender + Education
- Model 3 (Log-Level Extended): lnSalary ~ Age_c + Age2_c + Experience + Gender + Education + Education x Experience

Base category:
- Gender = Female
- Education Level = High School

Gia thuyet ky vong:
- H1: Experience co tac dong duong den Salary/lnSalary.
- H2: Nhom hoc van cao hon co luong ky vong cao hon so voi High School.
- H3: Age co tac dong duong o muc thap va co the giam dan theo tuoi (phi tuyen).
- H4: Interaction Education x Experience co the cho thay toc do tang luong theo kinh nghiem khac nhau giua cac nhom hoc van.

## 3.4 Descriptive statistics
Thong ke mo ta (mau 426 quan sat, truoc khi loai outlier):

- Age: mean = 33.92, sd = 7.74, min = 21, max = 60
- Years of Experience: mean = 8.46, sd = 6.50, min = 0, max = 34
- Salary: mean = 114,572.46, sd = 53,045.52, min = 350, max = 240,000

Phan bo nhom:
- Gender: Male 54.23%, Female 45.54%, Other 0.23%
- Education: Bachelor 42.72%, Master 29.11%, PhD 20.19%, High School 7.98%

Tuong quan:
- Corr(Age, Experience) = 0.9388 (rat cao), cho thay rui ro da cong tuyen trong cac mo hinh dua dong thoi hai bien nay.

## 3.5 Model estimation, significance tests, and interpretation
Ket qua duoc dien giai tren bo uoc luong nhat quan voi diagnostics: outlier-mode = hybrid, cov-type = HC3, n = 425.

Do phu hop mo hinh:
- Model 1: R2 = 0.6968
- Model 2: R2 = 0.7133
- Model 3: R2 = 0.7485

Dien giai ket qua chinh:

Model 1 (Level-Level):
- Experience co y nghia thong ke cao va duong (beta ~ 7,182.8; p < 0.001): moi nam kinh nghiem bo sung lien quan den muc luong tang trung binh khoang 7,183 don vi tien luong, giu cac yeu to khac khong doi.
- Age am va co y nghia (beta ~ -1,593.6; p = 0.0117), can dien giai tham trong do da cong tuyen voi Experience.
- Education effects lon va duong so voi High School; tat ca co y nghia cao.

Model 2 (Log-Level):
- Experience duong, co y nghia cao (beta = 0.0691; p < 0.001), xap xi +6.91% luong cho moi nam kinh nghiem.
- Male co he so duong va co y nghia o muc 5% (beta = 0.0629; p = 0.0388), xap xi chenhlech +6.29% so voi Female khi giu cac yeu to khac co dinh.
- Education co tac dong duong rat manh:
  - Bachelor: beta = 0.6943, exp(beta)-1 = 1.0024 -> luong cao hon khoang 100.24% so voi High School.
  - Master: beta = 0.8468, exp(beta)-1 = 1.3320 -> luong cao hon khoang 133.20%.
  - PhD: beta = 0.8554, exp(beta)-1 = 1.3523 -> luong cao hon khoang 135.23%.
- Age am va co y nghia (beta = -0.0158; p = 0.0063), nhac lai can doc cung diagnostics.

Model 3 (Log-Level Extended, centered age):
- Age_c khong con y nghia (p = 0.2409), trong khi Age2_c am va co y nghia (beta = -0.000914; p = 0.0086), ham y quan he phi tuyen co do cong am.
- Experience van duong va co y nghia cao (beta = 0.0827; p < 0.001).
- Interaction:
  - Exp_x_Bachelor: khong y nghia
  - Exp_x_Master: am, co y nghia (p = 0.0033)
  - Exp_x_PhD: am, co y nghia (p = 0.0018)

Tuy Model 3 co R2 cao nhat, phan interaction va da cong tuyen can duoc can nhac khi dien giai kinh te hoc.

## 3.6 Multicollinearity and heteroscedasticity checks
Kiem dinh duoc thuc hien tren pipeline hybrid outlier + centered age:

- VIF:
  - Model 1-2: Age va Experience van cao (xap xi 8.7-8.8)
  - Model 3: Age2_c giam ve 2.38 (cai thien ro structural multicollinearity), nhung Age_c van cao (~9.21) do tuong quan voi Experience; dong thoi Experience va interaction van cao (nhieu bien > 8)

- Breusch-Pagan:
  - Heteroskedasticity duoc phat hien o ca 3 model (f_p_value < 0.05)
  - He qua: can dung robust standard errors HC3 cho suy luan thong ke

- Jarque-Bera:
  - Model 2: khong bac bo normality sau khi loai outlier cuc tri
  - Model 1 va Model 3: van bac bo normality

Ket luan diagnostics:
- Su dung HC3 la lua chon chinh thong nhat cho inference.
- Bao cao can ghi ro da cong tuyen (Age-Experience va interaction structures) va canh bao ve dien giai he so Age.

## 3.7 Comments and recommendations
Nhan xet tong quan:
- Experience va Education la hai cum bien giai thich manh nhat cho luong.
- Sau khi xu ly outlier, mo hinh log-level (dac biet Model 2) cho tinh on dinh va de dien giai theo phan tram.
- Model 3 cung cap thong tin bo sung (phi tuyen va interaction) nhung doi mat da cong tuyen cao hon.

Khuyen nghi trinh bay trong bao cao:
- Chon Model 2 (log-level) lam mo hinh co so de dien giai chinh sach vi can bang giua tinh don gian, do phu hop va tinh on dinh.
- Dung Model 3 nhu mo hinh mo rong/sensitivity, nhan manh rang he so interaction co the nhay cam voi dac ta mo hinh.
- Luon bao cao ket qua HC3 ben canh ket qua nonrobust (neu can) de minh bach inference.

Gioi han nghien cuu:
- Bien Gender = Other co qua it quan sat (gan nhu 1 dong), nen uoc luong khong on dinh.
- Du lieu la cross-section, khong the ket luan nhan qua manh.
- Co the con bien bo sot (industry, region, occupation, firm size, skill score).

Huong mo rong:
- Thu regularization hoac reduced-form de giam da cong tuyen.
- Bo sung bien bo tro va check do nhay ket qua theo cac quy tac outlier khac nhau.

## 3.8 References (APA style)
Becker, G. S. (1964). Human capital: A theoretical and empirical analysis, with special reference to education. University of Chicago Press.

Breusch, T. S., & Pagan, A. R. (1979). A simple test for heteroscedasticity and random coefficient variation. Econometrica, 47(5), 1287-1294.

Jarque, C. M., & Bera, A. K. (1980). Efficient tests for normality, homoscedasticity and serial independence of regression residuals. Economics Letters, 6(3), 255-259.

Mincer, J. (1974). Schooling, experience, and earnings. Columbia University Press.

Wooldridge, J. M. (2019). Introductory econometrics: A modern approach (7th ed.). Cengage.
