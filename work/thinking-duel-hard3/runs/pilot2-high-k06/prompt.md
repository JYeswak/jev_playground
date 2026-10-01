# Task k06: display-width wrap

Work in $PWD. `wrap.py` has `wrap(text, width)` breaking text into lines of
display width <= width (break on spaces; a word longer than width goes on its
own line unbroken, EXCEPT a word of all wide East-Asian chars which breaks
between any two characters into width-sized chunks): wide East-Asian chars
(W/F) count 2, combining marks count 0, all else 1, using unicodedata.
shipped code uses len() and breaks mid-word. Fix it, stdlib only. Verify with CJK and accented text.
