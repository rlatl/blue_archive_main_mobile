# -*- encoding=utf8 -*-
__author__ = "KIM"

from airtest.core.api import *
import os
import time
import json
import argparse
from datetime import datetime

# 장치 연결
auto_setup(__file__)
connect_device("Android:///")

# 설정
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

REPEAT = config["settings"].get("repeat", 3)
SLOW_DELAY = config["settings"].get("slow_case_delay", 9)
NORMAL_DELAY = config["settings"].get("normal_case_delay", 5)

# 경로
DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(DIR, "images")
RESULT_PATH = os.path.join(DIR, "test_results.txt")
LOG_PATH = os.path.join(DIR, "test_log.txt")
CASE_PATH = os.path.join(DIR, "test_cases.json")

#테스트 로그를 텍스트 파일로 저장하는 함수
def write_log(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {msg}\n")

#테스트 결과를 텍스트 파일로 저장하는 함수
def write_result(case, result):
    with open(RESULT_PATH, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {case}: {result}\n")

#테스트 진행 중 예기치 못한 화면으로 이동했을때 복구 함수        
def attempt_recovery():
    back_pos = Template(os.path.join(IMG_DIR, "back_button.png"))
    main_img = Template(os.path.join(IMG_DIR, "main_event.png"))
    notice_close = Template(os.path.join(IMG_DIR, "notice_close.png"))

    for attempt in range(5):
        if exists(main_img):
            write_log("Recovery success: main screen detected")
            return
        if exists(notice_close):
            touch(notice_close)
            write_log(f"Recovery attempt {attempt}: Closed notice")
        else:
            keyevent("BACK")
            write_log(f"Recovery attempt {attempt}: Pressed BACK")
        sleep(5)

#닫기 함수 : 테스트 수행 이후 메인화면으로 복귀함        
def close_case(case):
    close_img = Template(os.path.join(IMG_DIR, f"{case}_close.png"))
    sleep(2)
    if not exists(close_img):
        write_log(f"{case}: close image not found, attempting recovery...")
        attempt_recovery()
    else:
        touch(close_img)
        sleep(SLOW_DELAY if case == "cafe" else NORMAL_DELAY)

#공지 사항 테스트 함수 : 공지 사항 진입 후 notice1 (테스트 희망 공지사항) 이미지 진입후
#해당 공지 사항에서 타겟 이미지 나올때까지 스크롤 내려서 타겟 이미지 찾음, 테스트 후 공지 사항 닫고 메인 화면 복귀   
def run_notice_test():
    case = "notice"
    write_log(f"--- Start test: {case} ---")
    btn_img = Template(os.path.join(IMG_DIR, f"{case}_button.png"))
    notice1 = Template(os.path.join(IMG_DIR, "notice1.png"))
    target_img = Template(os.path.join(IMG_DIR, "notice_target.png"))

    if not exists(btn_img):
        write_log(f"{case}: button not found, attempting recovery...")
        attempt_recovery()
        if not exists(btn_img):
            write_result(case, "FAIL (button not found after recovery)")
            return
    touch(btn_img)
    sleep(NORMAL_DELAY)
    sleep(3)

    if not touch(notice1):
        write_result(case, "FAIL (notice1 not found)")
        attempt_recovery()
        return

    sleep(2)
    found = False
    for _ in range(15):
        if exists(target_img):
            found = True
            break
        swipe((600, 900), (600, 400))
        sleep(1)

    write_result(case, "PASS" if found else "FAIL (target not found after scrolling)")
    close_case(case)

#학생 목록 테스트 함수
#학생 화면 진입 후 스트라이커에서 타겟 학생2명, 스페셜에서 타겟 학생 1명이 있는지 확인함
#만약 학생 진입 시 스페셜 학생 목록이 활성화 되있으면 스트라이커 학생 목록으로 변경함
def run_students_test():
    case = "students"
    write_log(f"--- Start test: {case} ---")
    btn_img = Template(os.path.join(IMG_DIR, f"{case}_button.png"))
    striker_img = Template(os.path.join(IMG_DIR, "striker.png"))
    special_btn = Template(os.path.join(IMG_DIR, "students_special_button.png"))
    target1 = Template(os.path.join(IMG_DIR, "students_target1.png"))
    target2 = Template(os.path.join(IMG_DIR, "students_target2.png"))
    target3 = Template(os.path.join(IMG_DIR, "students_special_target.png"))
    special_activate = Template(os.path.join(IMG_DIR, "special_activate.png"))

    if not exists(btn_img):
        write_log(f"{case}: button not found, attempting recovery...")
        attempt_recovery()
        if not exists(btn_img):
            write_result(case, "FAIL (button not found after recovery)")
            return
    touch(btn_img)
    sleep(NORMAL_DELAY)

    if exists(special_activate):
        touch(striker_img)
        sleep(2)

    ok1 = exists(target1)
    ok2 = exists(target2)

    if touch(special_btn):
        sleep(2)
        ok3 = exists(target3)
    else:
        ok3 = False

    write_result(case, "PASS" if ok1 and ok2 and ok3 else "FAIL (target check failed)")
    close_case(case)

#공지, 학생 목록을 제외한 일반 항목 테스트 함수
#항목 진입 후 타겟 이미지가 있으면 PASS, 이후 close 함수로 메인 화면으로 되돌아감
#카페 테스트시에는 로딩이 길어서 slow delay 를 대기시간으로 가짐
def run_generic_test(case):
    write_log(f"--- Start test: {case} ---")
    btn_img = Template(os.path.join(IMG_DIR, f"{case}_button.png"))
    target_img = Template(os.path.join(IMG_DIR, f"{case}_target.png"))

    if not exists(btn_img):
        write_log(f"{case}: button not found, attempting recovery...")
        attempt_recovery()
        if not exists(btn_img):
            write_result(case, "FAIL (button not found after recovery)")
            return
    touch(btn_img)
    sleep(SLOW_DELAY if case == "cafe" else NORMAL_DELAY)

    if exists(target_img):
        write_result(case, "PASS")
    else:
        write_result(case, "FAIL (target not found)")
        attempt_recovery()

    close_case(case)    

#테스트 실행 및 반복
def run_tests_from(start_idx=0):
    with open(CASE_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    for run in range(REPEAT):
        write_log(f"==== Run {run+1}/{REPEAT} ====")
        for i, case in enumerate(test_cases):
            if i < start_idx:
                continue
            if case == "notice":
                run_notice_test()
            elif case == "students":
                run_students_test()
            else:
                run_generic_test(case)
        write_log(f"==== Run {run+1} complete ====")
    print("테스트 완료.")

# CLI 진입점
if __name__ == "__main__":
    start_index = 0  #이곳의 숫자값을 변경하여 테스트 시작 시점을 결정 할 수 있습니다.
# 0 : 공지
# 1 : 모모톡
# 2 : 미션
# 3 : 청휘석 구입
# 4 : 카페
# 5 : 스케쥴
# 6 : 학생
# 7 : 편성
# 8 : 소셜
# 9 : 제조
# 10 : 상점
# 11 : 모집
    run_tests_from(start_index)

