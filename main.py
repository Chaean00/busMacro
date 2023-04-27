import threading
import requests
from tkinter import *
import time

def run() :
    # 로그인 데이터
    loginData = {
        "id":idEntry.get(),
        "pass":pwEntry.get(),
        "autoLogin":""
    }
    # 로그인 요청 URL
    loginUrl = "https://daejin.unibus.kr/api/index.php?ctrl=Main&action=loginProc"

    # 버스예약 요청 URL
    reserveUrl = "https://daejin.unibus.kr/api/index.php?ctrl=BusReserve&action=reserveAppProc"

    # 버스 리스트 url (노원하교)
    busListDownUrl = "https://daejin.unibus.kr/api/index.php?ctrl=BusReserve&action=busList&dir=DOWN&lineGroupSeq=27"

    # 버스 리스트 url (노원등교)
    busListUpUrl = "https://daejin.unibus.kr/api/index.php?ctrl=BusReserve&action=busList&dir=UP&lineGroupSeq=28"

    # 로그인
    session = requests.Session()
    response = session.post(loginUrl, json=loginData)
    if "OK" in response.text :
        print("로그인 성공")
        print("응답코드 = " + str(response.status_code))
        cookie = response.cookies.get_dict()

        # 로그인후 Authorization을 가져오기
        # {'result': 'OK', 'resultMsg': '', 'data': 'QedXyA83JFEG8nl8zeoM3mD693G7wbSFxu3lAgFeziWjPnRXcx+X5hECB2QZo3CB85wNBVHVcgOiU6W15FWH6g=='}
        response_json = response.json()
        token = response_json.get('data')
        header = {
            "Authorization": token
        }
        if token :
            # 하교(노원) 버스리스트 가져오기
            busDownResponse = session.get(busListDownUrl, cookies=cookie, headers=header)
            if busDownResponse.status_code == 200:
                downData = busDownResponse.json()
                for data in downData['data']['busList'] :
                    # 하교 버스 시간 설정
                    if data['operateTime'] == downEntry.get():
                        downBusSeq = (data['busSeq'])
            else:
                print("하교 리스트 가져오기 실패")

            # 등교(노원) 버스리스트 가져오기
            busUpResponse = session.get(busListUpUrl, cookies=cookie, headers=header)
            if busUpResponse.status_code == 200:
                upData = busUpResponse.json()
                for data in upData['data']['busList'] :
                    # 등교 버스 시간 설정
                    if data['operateTime'] == upEntry.get():
                        upBusSeq = (data['busSeq'])
            else:
                print("등교 리스트 가져오기 실패")
        else:
            print('로그인 실패! 인증 토큰이 없습니다.')

        # 하교 버스 데이터
        try:
            downReserveData = {
                "busSeq": downBusSeq,  # 버스번호
                "lineSeq": "27",  # 버스노선 - 노원등교: 28 / 노원하교: 27
                "stopSeq": 77,  # 하차위치 - 노원등교: 80 / 노원하교: 77
                "seatNo": int(downSeatEntry.get())  # 좌석번호
            }
        except NameError:
            pass

        # 등교 버스 데이터
        try :
            upReserveData = {
                "busSeq": upBusSeq,  # 버스번호
                "lineSeq": "28",  # 버스노선 - 노원등교: 28 / 노원하교: 27
                "stopSeq": 80,  # 하차위치 - 노원등교: 80 / 노원하교: 77
                "seatNo": int(upSeatEntry.get()) # 좌석번호
            }
        except NameError:
            pass
        # 등교 버스 예약 ㄱㄱ
        try :
            busUpReserve = session.post(reserveUrl, cookies=cookie, headers=header, json=upReserveData)
        except NameError:
            pass
        # 하교 버스 예약 ㄱㄱ
        try:
            busDownReserve = session.post(reserveUrl, cookies=cookie, headers=header, json=downReserveData)
        except NameError:
            pass
        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        print("result 값이 OK면 성공")
        try:
            print("등교 내역 = " + str(busUpReserve.json()))
        except NameError:
            pass
        try:
            print("하교 내역 = " + str(busDownReserve.json()))
        except NameError:
            pass
        runBtn.config(text="실행 중...", )
    else :
        print("로그인 실패")
        print(response.text)

def checkAt22() :
    now = time.localtime()
    if now.tm_hour >= 22:
        run()
    else:
        # 22시 - 현재 시간을 하여 변수에 담고 sleep을 통해 기다린뒤 실행
        remainingSeconds = (22 - now.tm_hour) * 3600 - now.tm_min * 60 - now.tm_sec
        time.sleep(remainingSeconds + 1)
        run()

# 스레드 생성
# 응답없음 해결
def excuteThread():
    thread = threading.Thread(target=checkAt22)
    thread.setDaemon(True)
    thread.start()
# 시계
def digital_clock():
    time_live = time.strftime("%H:%M:%S")
    timeLabel.config(text=time_live)
    timeLabel.after(200, digital_clock)

if __name__ == "__main__" :
    fonts = ('맑은고딕', 13, 'bold')
    window = Tk()
    window.title("셔틀버스 잡자")
    window.geometry("800x600")
    window.resizable(height=False, width=False)

    timeLabel = Label(window, font=fonts) # 시간
    timeLabel.place(x=150, y=350)

    idLabel = Label(window, text="ID", font=fonts) #id라벨
    idLabel.grid(column=0, row=0)

    pwLabel = Label(window, text="PW", font=fonts) #pw라벨
    pwLabel.grid(column=0, row=1)

    upLabel = Label(window, text="등교시간", font=fonts)  # 등교 라벨
    upLabel.grid(column=0, row=2)

    downLabel = Label(window, text="하교시간", font=fonts)  # 하교 라벨
    downLabel.grid(column=0, row=3)

    upSeatLabel = Label(window, text="등교좌석번호", font=fonts)  # 하교 라벨
    upSeatLabel.grid(column=0, row=4)

    downSeatLabel = Label(window, text="하교좌석번호", font=fonts)  # 하교 라벨
    downSeatLabel.grid(column=0, row=5)

    upList = Label(window, text="등교\n08:00\n08:10\n08:20\n08:30\n08:40\n08:50\n09:00\n09:20\n09:40\n09:50\n10:00\n10:10\n10:20\n10:40\n11:00\n11:20\n11:40\n12:00\n12:20")
    upList.place(x=600, y=10)

    downList = Label(window, text="하교\n09:20\n09:40\n10:00\n10:20\n10:40\n11:00\n11:20\n11:40\n12:30\n13:00\n13:30\n14:00\n14:30\n15:00\n15:10\n15:20\n15:30\n16:00\n16:30\n17:00\n17:10\n17:20\n17:30\n18:00\n18:30\n19:00")
    downList.place(x=650, y=10)

    seatList = Label(window, text="운전석\t\t\n1 2\t3 4\n5 6\t7 8\n9 10\t11 12\n13 14\t15 16\n17 18\t19 20\n21 21\t23 24\n25 26\t27 28\n29 30\t31 32\n33 34\t35 36\n37 38\t39 40\n\n가끔 오른쪽이\n1일때도 있음")
    seatList.place(x=450, y=10)

    text1 = Label(window, text="※ 등교시간 / 하교시간은 15:30, 11:30 과 같은 정확히 형태로 입력", font=fonts)  # text
    text1.place(x=50, y=410)

    text2 = Label(window, text="※ ☆실★패☆해★도☆책★임☆안★짐☆", font=('맑은고딕', 13, 'bold'))
    text2.place(x=50, y=450)

    text3 = Label(window, text="※ 실행버튼 누르면 10시1초에 자동실행", font=fonts)
    text3.place(x=50, y=430)

    text4 = Label(window, text="현재 시각 : ", font=fonts)
    text4.place(x=50, y=350)

    idEntry = Entry() # id입력창
    idEntry.grid(column=1, row=0)

    pwEntry = Entry() # pw입력창
    pwEntry.grid(column=1, row=1)

    upEntry = Entry() # 등교시간 입력창
    upEntry.grid(column=1, row=2)

    downEntry = Entry() # 하교시간 입력창
    downEntry.grid(column=1, row=3)

    upSeatEntry = Entry() # 등교좌석번호
    upSeatEntry.grid(column=1, row=4)

    downSeatEntry = Entry() # 하교 좌석번호
    downSeatEntry.grid(column=1, row=5)

    runBtn = Button(window, text="실행", height=3, width=10, command=excuteThread) # 실행버튼
    runBtn.place(x=350, y=500)

    digital_clock()
    window.mainloop()