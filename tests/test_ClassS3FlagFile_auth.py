#!/usr/local/vbin/.venv/python3.9/bin/python
#
# Exercises ClassS3FlagFile's bucket|folder|file_mask authorization matching
# and $VAR environment-variable resolution (COMMON/Modules/ClassS3FlagFile.py).
# Uses a throwaway fixture file and fake, non-secret env vars only -
# never touches S3_Bucket_processing/info/s3_folder_mask_aws-key.info,
# AWS_KEY/.env-*, or real AWS/S3.
#
# Run from the repo root:
#   python3 tests/test_ClassS3FlagFile_auth.py

import os
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, 'COMMON'))

from Modules.ClassS3FlagFile import ClassS3FlagFile

FAKE_EVENT_BASE = {
    "FLAG-FILE-DIR": "S3_Bucket_processing",
    "BOTO-S3-C": None,
    "BUCKET": "fakebucket",
    "PREFIX": "fake/prefix",
    "TREAD": "1",
    "FILE-MASK-IN-S3": "*.FLAG",
}


def _write_fixture(line):
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    tmp.write(line + '\n')
    tmp.close()
    return tmp.name


def test_matching_combination_resolves_env_vars():
    fixture = _write_fixture('fakebucket|fake/prefix|*.FLAG|$TEST_KEY_ID|$TEST_KEY_SECRET')
    os.environ['TEST_KEY_ID'] = 'FAKEIDVALUE'
    os.environ['TEST_KEY_SECRET'] = 'FAKESECRETVALUE'
    try:
        event = dict(FAKE_EVENT_BASE, **{"FILE-WITH-AWS-KEY": fixture})
        obj = ClassS3FlagFile(event)
        creds = obj.session.get_credentials()
        assert creds.access_key == 'FAKEIDVALUE', creds.access_key
        assert creds.secret_key == 'FAKESECRETVALUE', creds.secret_key
    finally:
        os.environ.pop('TEST_KEY_ID', None)
        os.environ.pop('TEST_KEY_SECRET', None)
        os.unlink(fixture)


def test_missing_env_var_exits():
    fixture = _write_fixture('fakebucket|fake/prefix|*.FLAG|$TEST_KEY_ID_MISSING|$TEST_KEY_SECRET_MISSING')
    try:
        event = dict(FAKE_EVENT_BASE, **{"FILE-WITH-AWS-KEY": fixture})
        try:
            ClassS3FlagFile(event)
            raise AssertionError("expected SystemExit for unset env var")
        except SystemExit:
            pass
    finally:
        os.unlink(fixture)


def test_no_matching_combination_exits():
    fixture = _write_fixture('otherbucket|other/prefix|*.FLAG|$TEST_KEY_ID|$TEST_KEY_SECRET')
    try:
        event = dict(FAKE_EVENT_BASE, **{"FILE-WITH-AWS-KEY": fixture})
        try:
            ClassS3FlagFile(event)
            raise AssertionError("expected SystemExit for no matching bucket/folder/mask")
        except SystemExit:
            pass
    finally:
        os.unlink(fixture)


if __name__ == "__main__":
    tests = [
        test_matching_combination_resolves_env_vars,
        test_missing_env_var_exits,
        test_no_matching_combination_exits,
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except Exception as e:
            failures += 1
            print(f"FAIL: {t.__name__}: {e}")
    if failures:
        sys.exit(1)
    print("ALL TESTS PASSED")
