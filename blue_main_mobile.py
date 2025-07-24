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

def write_log(msg):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {msg}\n")

def write_result(case, result):
    with open(RESULT_PATH, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {case}: {result}\n")

def attempt_recovery():
    back_pos = Template(os.path.join(IMG_DIR, "back_button.png"))
    main_img = Template(os.path.join(IMG_DIR, "main_campaign.png"))
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

def run_step(case):
    btn_img = Template(os.path.join(IMG_DIR, f"{case}_button.png"))
    close_img = Template(os.path.join(IMG_DIR, f"{case}_close.png"))
    print(f"Testing: {case}")
    write_log(f"--- Start test: {case} ---")

    if not exists(btn_img):
        write_log(f"{case}: button not found, attempting recovery...")
        attempt_recovery()
        if not exists(btn_img):
            write_result(case, "FAIL (button not found after recovery)")
            return
    touch(btn_img)

    sleep(SLOW_DELAY if case == "cafe" else NORMAL_DELAY)

    if case == "students":
        striker_img = Template(os.path.join(IMG_DIR, "striker.png"))
        special_btn = Template(os.path.join(IMG_DIR, "students_special_button.png"))
        target1 = Template(os.path.join(IMG_DIR, "students_target1.png"))
        target2 = Template(os.path.join(IMG_DIR, "students_target2.png"))
        target3 = Template(os.path.join(IMG_DIR, "students_special_target.png"))
        special_activate = Template(os.path.join(IMG_DIR, "special_activate.png"))

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

    elif case == "notice":
        notice1 = Template(os.path.join(IMG_DIR, "notice1.png"))
        target_img = Template(os.path.join(IMG_DIR, "notice_target.png"))
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

    else:
        target_img = Template(os.path.join(IMG_DIR, f"{case}_target.png"))
        if exists(target_img):
            write_result(case, "PASS")
        else:
            write_result(case, "FAIL (target not found)")
            attempt_recovery()

    sleep(2)
    if not exists(close_img):
        write_log(f"{case}: close image not found, attempting recovery...")
        attempt_recovery()
    else:
        touch(close_img)
        sleep(SLOW_DELAY if case == "cafe" else NORMAL_DELAY)  # 메인 화면 돌아갈때 대기시간 카페만 8초 나머지 5초    

def run_tests_from(start_idx=0):
    with open(CASE_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    for run in range(REPEAT):
        write_log(f"==== Run {run+1}/{REPEAT} ====")
        for i, case in enumerate(test_cases):
            if i >= start_idx:
                run_step(case)
        write_log(f"==== Run {run+1} complete ====")
    print("테스트 완료.")

# CLI 진입점
if __name__ == "__main__":
    start_index = 0
    run_tests_from(start_index)


