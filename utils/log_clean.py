import os
import zipfile
import logging
from glob import glob
from datetime import datetime

def manage_log_files(log_dir="logs/app", zip_log_size=10, keep_zips=10):
    log_dir = os.path.abspath(log_dir)
    log_files = sorted(glob(os.path.join(log_dir, "*.log")))

    if len(log_files) < zip_log_size:
        logging.info(f"[LOG CLEANUP] 압축할 로그가 아직 {zip_log_size}개 미만입니다. 현재: {len(log_files)}개")
        return

    # 로그 파일 중 가장 마지막 파일의 날짜 추출
    last_log_name = os.path.splitext(os.path.basename(log_files[-1]))[0]

    try:
        # 로그 파일명이 'YYYY-MM-DD.log' 형식이라고 가정
        last_log_date = datetime.strptime(last_log_name, "%Y-%m-%d").date()
    except ValueError:
        logging.warning(f"[LOG CLEANUP] 잘못된 로그 파일명 포맷: {last_log_name}")
        return

    today = datetime.now().date()

    # 마지막 로그가 오늘 로그면 아직 자정 안 지난 상태로 간주
    if last_log_date >= today:
        logging.info(f"[LOG CLEANUP] 오늘({today}) 로그가 포함되어 있어 아직 압축하지 않음")
        return

    # 압축할 로그 선정
    to_zip = log_files[:zip_log_size]
    first_date = os.path.splitext(os.path.basename(to_zip[0]))[0]
    last_date = os.path.splitext(os.path.basename(to_zip[-1]))[0]
    zip_filename = os.path.join(log_dir, f"archive_{first_date}_to_{last_date}.zip")

    # 압축 실행
    with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for file_path in to_zip:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
            os.remove(file_path)
            logging.info(f"[LOG CLEANUP] 압축 및 삭제: {arcname}")

    # 오래된 zip 삭제
    zip_files = sorted(glob(os.path.join(log_dir, "archive_*.zip")))
    if len(zip_files) > keep_zips:
        to_delete = zip_files[:-keep_zips]
        for zip_path in to_delete:
            os.remove(zip_path)
            logging.info(f"[LOG CLEANUP] 오래된 압축파일 삭제: {os.path.basename(zip_path)}")
