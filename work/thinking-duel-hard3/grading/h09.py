import sys, tempfile, os

sys.path.insert(0, SYS_PATH)
from delim import write_delim, read_delim

rows = [["a", "b|c", 'd"e', "f\ng", None, ""], ["x|y", "NULL", None]]
for delim, none_as in [("|", ""), (";", "NULL"), ("\t", "NA")]:
    fd, p = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    write_delim(p, rows, delim, none_as)
    back = read_delim(p, delim, none_as)
    assert back == [["a", "b|c", 'd"e', "f\ng", None, ""], ["x|y", "NULL", None]], (
        delim,
        none_as,
        back,
    )
    os.unlink(p)
print("h09 PASS")
