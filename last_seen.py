def get_last_seen_id(file_path):
    try:
        f_read = open(file_path, "r")
        last_seen_id = int(f_read.read().strip())
        f_read.close()
    except ValueError:
        f_read.close()
        last_seen_id = 111111111
        set_last_seen_id(last_seen_id, file_path)
    except FileNotFoundError:
        last_seen_id = 111111111
        set_last_seen_id(last_seen_id, file_path)
    
    return last_seen_id


def set_last_seen_id(last_seen_id, file_path):
    f_write = open(file_path, "w")
    f_write.write(str(last_seen_id))
    f_write.close()
    return
