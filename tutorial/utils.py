import os
def get_move_ts_url_list_from_index(prefix=None,index_file_path=None):
    result = []
    if not os.path.exists(index_file_path):
        raise FileNotFoundError(F"{index_file_path} is not exist...")
    else:
        with open(index_file_path,"r",encoding="utf-8") as fp:
            for line in fp.readlines():
                line = line.strip()
                if line.strip().endswith("ts"):
                    result.append(line) if prefix is None else result.append(f"{prefix}/{line}")
    return result


print(get_move_ts_url_list_from_index(None,os.path.join(os.path.dirname(__file__),"index.m3u8")))