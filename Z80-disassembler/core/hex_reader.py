def hex_reader(code):
    ByteList=[]
    if code is not None:
        code = code.split("\n")
        for line in code:
            line1=line[9:len(line)-3]
            for i in range(0, len(line1), 2):
                a=line1[i:i+2]
                try:
                    u=int(a, 16)
                except ValueError:
                    return None
                ByteList.append(u)
    return bytes(ByteList)
