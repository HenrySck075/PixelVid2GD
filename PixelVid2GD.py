try:
    import base64,os,cv2,math,colorsys,zlib,regex as re,tkinter as tk,traceback
    from copy import deepcopy#,numpy as np
    from PIL import Image,ImageTk
    #if not os.path.exists("./PixelVid2GDHelper.js"): print("Cannot find helper file. Please also include it here or rename the helper file if you did"); exit(1)
    SAVE_FILE_PATH = os.path.join(os.getenv('LocalAppData'), 'GeometryDash')
    data={
        "ham": "<k>k_0</k><d><k>kCEK</k><i>4</i><k>k1</k><i>0</i><k>k2</k><s>[[NAME]]</s><k>k4</k><s>",
        "bur": "kS38,1_0_2_0_3_0_11_0_12_0_13_0_4_-1_6_1000_7_1_15_1_18_0_8_1|1_0_2_0_3_0_11_255_12_255_13_255_4_-1_6_1001_7_1_15_1_18_0_8_1|1_0_2_0_3_0_11_255_12_255_13_255_4_-1_6_1009_7_1_15_1_18_0_8_1|1_0_2_0_3_0_11_255_12_255_13_255_4_-1_6_1002_5_1_7_1_15_1_18_0_8_1|1_135_2_135_3_135_11_255_12_255_13_255_4_-1_6_1005_5_1_7_1_15_1_18_0_8_1|1_255_2_125_3_0_11_255_12_255_13_255_4_-1_6_1006_5_1_7_1_15_1_18_0_8_1|,kA13,0,kA15,0,kA16,0,kA14,,kA6,13,kA7,0,kA17,0,kA18,0,kS39,0,kA2,0,kA3,0,kA8,0,kA4,4,kA9,0,kA10,0,kA11,0;",
        "ger": "</s><k>k3</k><s>[[DESC]]</s><k>k14</k><t /><k>k46</k><i>0</i><k>k5</k><s></s><k>k13</k><t /><k>k21</k><i>2</i><k>k48</k><i>69</i><k>k16</k><i>1</i><k>k23</k><s>3</s><k>k8</k><i>0</i><k>k45</k><i>[[SONG_ID]]</i><k>k80</k><i>0</i><k>k50</k><i>0</i><k>k47</k><t /><k>k84</k><i>0</i><k>kI1</k><r>[[EDITORX]]</r><k>kI2</k><r>0</r><k>kI3</k><r>0</r><k>kI5</k><i>6</i><k>kI6</k><d><k>0</k><s>0</s><k>1</k><s>0</s><k>2</k><s>0</s><k>3</k><s>0</s><k>4</k><s>0</s><k>5</k><s>0</s><k>6</k><s>0</s><k>7</k><s>0</s><k>8</k><s>0</s><k>9</k><s>0</s><k>10</k><s>0</s><k>11</k><s>0</s><k>12</k><s>0</s><k>k64</k><i>6</i></d></d>"
    }
    def xor_bytes(data: bytes, value: int) -> bytes:
        return bytes(map(lambda x: x ^ value, data))

    def rgb_to_hsv(rgb):
        return tuple(str(int(i)) for i in colorsys.rgb_to_hsv(*rgb))

    def read_in_chunks(file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def decrypt(encrypted_data,need_xor=True):  # decrypt

            if need_xor: decrypted_data = xor_bytes(encrypted_data, 11)
            else: decrypted_data=encrypted_data
            decoded_data = base64.b64decode(decrypted_data, altchars=b'-_')
            decompressed_data = zlib.decompress(decoded_data[10:], -zlib.MAX_WBITS)

            return decompressed_data

    def replacenth(string, sub, wanted, n):
        where = [m.start() for m in re.finditer(sub, string)][n-1]
        before = string[:where]
        after = string[where:]
        after = after.replace(sub, wanted, 1)
        newString = before + after
        return newString
    #print(decrypt(re.search("<k>k4</k><s>(.*)</s>",decrypted).group(1),False))
    levle_array=[
        "1,1612,2,-29,3,705;",
        "1,747,2,-29,3,55,54,850;",
        "1,749,2,-39,3,955,32,-1;",
        "1,13,2,-29,3,945;"
    ]

    # Get the Current Dir
    root = os.getcwd()
    x, y=7.5,1087
    trig_x, trig_y=0,y+30*80
    last_pxArray=[]

    videoFile = input("File name (and extension) to process: ")
    songID=input("Song ID to replace with the video's audio: ")
    showProgress=input("Show current frame while processing it (0 or 1, others is 0): ")
    if showProgress.isdigit():
        showProgress=True if int(showProgress) == 1 else False
    else: showProgress=False
    #7.5
    print("\n\n")

    with open(os.path.join(SAVE_FILE_PATH,"CCLocalLevels.dat"),'r') as r:
        m=r.read()
        if "<k>_isArr</k><t />" not in m: decrypted=decrypt(m.encode('utf-8'))
        else: decrypted=m.encode('utf-8')

    def readFrames():
        global videoFile,last_pxArray,levle_array,x,y,trig_x,trig_y
        step=(60/30) #change value after 60/ to change fps
        frames=0
        if showProgress:
            r=tk.Tk()
            panel=tk.Label(r)
            panel.pack(side="bottom", fill="both", expand="yes")
        print('Read file: {}'.format(videoFile))
        cap = cv2.VideoCapture(videoFile) # says we capture an image from a webcam
        width  = math.floor(cap.get(3))
        height = math.floor(cap.get(4))
        groupIds=[]
        m=2
        while(cap.isOpened()):
            ret,cv2_im = cap.read()
            if ret and frames%step == 0:
                converted = cv2.cvtColor(cv2_im,cv2.COLOR_BGR2RGB)

                pil_im = Image.fromarray(converted)

                im = pil_im.resize((math.floor((width/height)*40),40))
                if showProgress:
                    photo=ImageTk.PhotoImage(im)
                    panel.configure(image=photo)
                    r.update()
                pxArray=[]
                #please help me
                for w in range(im.width):
                    lay=[]
                    for h in range(40):
                        lay.append(im.getpixel((w,h)))
                    pxArray.append(lay)
                changes=0
                if last_pxArray == []: #init object canvas
                    xoffs=0
                    for wi,w in enumerate(pxArray):
                        yoffs=0
                        he=[]
                        if wi == math.floor(len(pxArray)/2):
                            levle_array.append(f"1,901,2,{x+wi*x-73.5},3,765,58,1,51,1,10,99999999999;") #move trigger
                        for hi,h in enumerate(w):
                            m+=1
                            additional_pulse_str=f"1,1006,2,0,3,{y+yoffs+8000},46,99999999999,{'7,{0},8,{1},9,{2}'.format(*pxArray[wi][hi])},24,1,52,1,48,0,86,1,51,{m};"
                            levle_array.append(f"1,917,2,{x+xoffs},3,{y-yoffs},21,10,41,1,57,1.{m},64,1,67,1;{'' if pxArray[wi][hi] == (255,255,255) else additional_pulse_str}") #objec
                            yoffs+=7.5
                            he.append(m)
                        xoffs+=7.5
                        groupIds.append(he)
                else:
                    yoffs=0
                    for wi,w in enumerate(pxArray):
                        for hi,h in enumerate(w):
                            if pxArray[wi][hi] != last_pxArray[wi][hi]:
                                levle_array.append(f"1,1006,2,{trig_x},3,{trig_y+yoffs},46,99999999999,{'7,{0},8,{1},9,{2}'.format(*pxArray[wi][hi])},51,{groupIds[wi][hi]},52,1,48,0,86,1;") #pulse trigger
                                yoffs+=4
                                changes+=1
                last_pxArray=deepcopy(pxArray)
            elif not ret:
                break
            #print(f"{frames} with {frames-1}: {changes} change(s)      ",end="\r")
            trig_x+=19.2
            frames+=1
                
        cap.release()
    print("Comparing frames")
    readFrames()
    levle_array.append(f"1,1049,2,{trig_x+700},3,1,51,1;")
    levle_string=''.join(levle_array)
    os.system(f"ffmpeg -y -i \"{videoFile}\" \"{os.path.join(SAVE_FILE_PATH,f'{str(songID)}.mp3')}\" ")
        #".format(saveData=r.read(),levelStr=levle_string,fileName=videoFile.replace(".mp4",""),songID=songID))
    raise KeyboardInterrupt("I'm funny")
except KeyboardInterrupt:
    print("writing")
    s=1
    saveData = decrypted.decode('utf-8').split("<k>_isArr</k><t />")
    for i in re.finditer("<k>k_(\d+)</k><d><k>kCEK</k>", saveData[1]):
        saveData[1] = replacenth(saveData[1], i.group(), f"<k>k_{int(i.group(1))+1}</k><d><k>kCEK</k>", s)
        s=2
    saveData:str = ''.join([saveData[0], "<k>_isArr</k><t />", data['ham'], data['bur'], levle_string, data['ger'], saveData[1]])
    saveData = saveData.replace("[[NAME]]", re.sub("[^a-z0-9A-Z| ]","",videoFile.replace(".mp4","").split("/")[-1].split("\\")[-1][0:30])).replace("[[DESC]]", "").replace("[[SONG_ID]]",songID).replace("[[EDITORX]]",str(trig_x+3000))
    with open(os.path.join(SAVE_FILE_PATH,"CCLocalLevels.dat"),"w") as w:
        w.write(saveData)

    print(f"Done!  {videoFile} | {len(levle_array)*2-5} objects")
except Exception as e:
    traceback.print_tb(e.__traceback__)
