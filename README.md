### Overview

 이 프로젝트는 LIDAR(라이다)와 Arduino를 사용하여 낙상 사고를 감지하는 시스템입니다. 초기 설정 및 환경 데이터를 스캔하여 사용자의 상태를 모니터링하고, 변화된 데이터로부터 낙상 여부를 판단합니다. 시스템은 데이터베이스와 연동되어 사용자 상태를 업데이트하며, 비정상적인 상황을 감지하면 경고를 보냅니다.

![lidar_-removebg-preview](https://github.com/user-attachments/assets/f8ced2de-90de-45e6-9f86-dc4726454e21)
---

### Features

1. **초기 환경 설정 및 데이터 스캔**  
   - 라이다(LiDAR)를 사용하여 초기 스캔 데이터를 수집하고, 기준 경계값을 설정
   - Arduino 센서와 통신하여 사용자가 시스템을 활성화했는지 확인

2. **낙상 감지**  
   - 실시간으로 스캔 데이터를 수집하여 초기 데이터와 비교
   - 특정 각도에서 연속적으로 짧아진 거리(낙상을 의미)를 감지하면 경고를 발생

3. **데이터 시각화**  
   - 초기 스캔 데이터와 실시간 데이터를 Polar Plot 형태로 시각화하여 저장

4. **데이터베이스 업데이트**  
   - 사용자의 상태를 데이터베이스에 저장하여 추적 및 관리가 가능

---

### Systems

- **H/W**  
  - RPLidar: 환경 데이터 스캔  
  - Arduino: 사용자와의 상호작용 및 상태 감지  

- **S/W**  
  - Python: 데이터 처리, 분석, 시각화  
  - Matplotlib: 스캔 데이터의 시각화  
  - PyMySQL: 데이터베이스 연동  
  - dotenv: 환경 변수 관리

---

### Description

#### 1. **환경 초기화 및 통신 설정**
```python
env = LiDAR('/dev/ttyUSB0', baudrate=256000)  # LiDAR 장치 초기화
ardu = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=.1)  # Arduino 통신 설정
env.init()  # 라이다 초기화
```

#### 2. **라이다 스캔 데이터 처리**
- 초기 스캔 데이터를 수집하고 기준 경계값을 설정
- 데이터를 각도와 거리로 분류하여 평균값을 계산

#### 3. **낙상 여부 판단**
- 실시간 데이터를 초기 데이터와 비교
- 연속된 특정 각도에서 거리가 짧아지면 낙상을 감지
---

### Installtion

1. **필수 라이브러리 설치**
   ```bash
   pip install matplotlib numpy pandas pymysql python-dotenv pyserial
   ```

2. **코드 실행**
   - `.env` 파일에 데이터베이스 설정 정보를 추가
   - 아래 명령어를 통해 코드를 실행:
     ```bash
     python3 lidar_main.py
     ```

---

### Config (.env 파일)

`.env` 파일에 데이터베이스 설정 정보를 추가
```plaintext
db_config = '{"host": "localhost", "user": "root", "password": "password", "database": "home"}'
```

---

### Visualized results

- `initial_scan_visualization.png`: 초기 스캔 데이터를 시각화한 이미지  
- `manikin_scan_visualization.png`: 실시간 감지 데이터를 시각화한 이미지  

---

### Check-list

1. **라이다 및 Arduino 연결**
   - `/dev/ttyUSB0`와 `/dev/ttyACM0` 장치 경로를 실제 연결된 포트로 수정

2. **데이터베이스 설정**
   - 데이터베이스의 스키마가 `home_status` 테이블과 호환되는지 확인

---

### License

이 프로젝트는 MIT 라이선스를 따릅니다. 상세 내용은 LICENSE 파일을 참조하세요.
