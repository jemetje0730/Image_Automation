import os
import zipfile
import logging
from glob import glob

def manage_log_files(log_dir="logs/app", zip_log_size=10, keep_zips=10):
    log_dir = os.path.abspath(log_dir)  # 🔍 절대 경로로 변환
    log_files = sorted(glob(os.path.join(log_dir, "*.log")))

    if len(log_files) < zip_log_size:
        logging.info(f"[LOG CLEANUP] 압축할 로그가 아직 {zip_log_size}개 미만입니다. 현재: {len(log_files)}개")
        return

    # 압축 대상 로그 추출
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

    # 압축 파일 유지 제한
    zip_files = sorted(glob(os.path.join(log_dir, "archive_*.zip")))
    if len(zip_files) > keep_zips:
        to_delete = zip_files[:-keep_zips]
        for zip_path in to_delete:
            os.remove(zip_path)
            logging.info(f"[LOG CLEANUP] 오래된 압축파일 삭제: {os.path.basename(zip_path)}")
