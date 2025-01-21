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


def _fullpath_file(f):
    return os.path.join(FILESYSTEM_DIR, f)


def _ensafe_pattern(p):
    if set(p.lower()) - ALPHABET_LOWER:
        raise ValueError("Unsafe pattern detected.")


def _ensafe_filename(f):
    if set(f.lower()) - FILENAME_LOWER:
        raise ValueError("Unsafe filename detected.")


def _ensure_not_exists(fpf):
    if os.path.exists(fpf):
        raise ValueError(f"File already exists.")


def fs_find(pattern):
    _ensafe_pattern(pattern)
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
    _ensafe_pattern(pattern)
    _ensafe_filename(file)
    assert set(file.lower()) - FILENAME_LOWER == set()
    assert set(pattern.lower()) - ALPHABET_LOWER == set()
    cmd = ["grep", "-i", pattern, file]
    proc = subprocess.Popen(cmd, cwd=FILESYSTEM_DIR, stdout=subprocess.PIPE)
    output, error = proc.communicate()
    assert error is None
    out_s = output.decode()
    out_lines = [l.strip() for l in out_s.split("\n") if l.strip()]
    return out_lines


def fs_cat(file):
    _ensafe_filename(file)
    return open(_fullpath_file(file)).read()


def fs_create(file, content):
    _ensafe_filename(file)
    fpfile = _fullpath_file(file)
    _ensure_not_exists(fpfile)
    with open(fpfile, 'w') as fout:
        fout.write(content)
    return "success"
