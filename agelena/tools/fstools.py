import os
import subprocess

ALPHABET_LOWER = set('qwertyuiopasdfghjklzxcvbnm')
FILENAME_LOWER = ALPHABET_LOWER | set("/._-0123456789")

FILESYSTEM_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "filesystem",
    )
)


def fs_find(pattern):
    assert set(pattern.lower()) - ALPHABET_LOWER == set()
    cmd = ["find", "-iname", f"*{pattern}*", "-type", "f"]
    proc = subprocess.Popen(cmd, cwd=FILESYSTEM_DIR, stdout=subprocess.PIPE)
    output, error = proc.communicate()
    assert error is None
    out_s = output.decode()
    out_lines0 = [l.strip() for l in out_s.split("\n") if l.strip()]
    assert all(ol.startswith("./") for ol in out_lines0)
    out_lines = sorted(ol[2:] for ol in out_lines0)
    return out_lines


def fs_grep(file, pattern):
    assert set(file.lower()) - FILENAME_LOWER == set()
    assert set(pattern.lower()) - ALPHABET_LOWER == set()
    cmd = ["grep", "-i", pattern, file]
    proc = subprocess.Popen(cmd, cwd=FILESYSTEM_DIR, stdout=subprocess.PIPE)
    output, error = proc.communicate()
    assert error is None
    out_s = output.decode()
    out_lines = [l.strip() for l in out_s.split("\n") if l.strip()]
    return out_lines
