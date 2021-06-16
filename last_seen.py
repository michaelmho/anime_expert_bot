import json

FILENAME = './text_files/last_seen.txt'


def get_last_seen_id(FILENAME):
    f_read = open(FILENAME, "r")
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def set_last_seen_id(last_seen_id, FILENAME):
    f_write = open(FILENAME, "w")
    f_write.write(str(last_seen_id))
    f_write.close()
    return
