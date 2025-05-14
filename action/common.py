import time
import logging

def wait(duration: float):
    """지정된 시간 동안 대기하며 로그 출력"""
    logging.info(f"[WAIT] {duration:.2f}초 동안 대기합니다...")
    time.sleep(duration)
