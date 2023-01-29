import base64,os,struct,zlib,cv2,math,colorsys,js2py
from copy import deepcopy#,numpy as np
from PIL import Image
if not os.path.exists("./PixelVid2GDHelper.js"): print("Cannot find helper file. Please also include it here or rename the helper file if you did"); exit(1)
SAVE_FILE_PATH = os.path.join(os.getenv('LocalAppData'), 'GeometryDash')
print("""
Warning: The result will overwrite first level in "Created Level" list contains level data (aka atleast 1 object in the level)!
Make sure you've prepared one to not get your level vanished.""")
def xor_bytes(data: bytes, value: int) -> bytes:
    return bytes(map(lambda x: x ^ value, data))

def rgb_to_hsv(rgb):
    return tuple(str(int(i)) for i in colorsys.rgb_to_hsv(*rgb))

def encrypt(decrypted_data,need_xor=True):  # encrypt
    compressed_data = zlib.compress(decrypted_data)
    data_crc32 = zlib.crc32(decrypted_data)
    data_size = len(decrypted_data)

    compressed_data = (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x0b' +  # gzip header
                        compressed_data[2:-4] +
                        struct.pack('I I', data_crc32, data_size))
    encoded_data = base64.b64encode(compressed_data, altchars=b'-_')
    encrypted_data = xor_bytes(encoded_data, 11)

    return encrypted_data if need_xor else encoded_data

def decrypt(encrypted_data,need_xor=True):  # decrypt

    decrypted_data = xor_bytes(encrypted_data, 11) if need_xor else encrypted_data
    decoded_data = base64.b64decode(decrypted_data, altchars=b'-_')
    decompressed_data = zlib.decompress(decoded_data[10:], -zlib.MAX_WBITS)

    return decompressed_data

with open(os.path.join(SAVE_FILE_PATH,"CCLocalLevels.dat"),"rb") as w:
    decrypted=decrypt(w.read()).decode("utf-8")
#print(decrypt(re.search("<k>k4</k><s>(.*)</s>",decrypted).group(1),False))
levle_array=[
    "1,1612,2,-29,3,705;",
    "1,747,2,-29,3,105,54,850;",
    "1,749,2,-39,3,955,32,-1;",
    "1,13,2,-29,3,945;"
]
print("\n\n")
# Get the Current Dir
root = os.getcwd()
x, y=3.75,783.75
trig_x, trig_y=0,y+30*80
last_pxArray=[]

videoFile = input("File name (and extension) to process: ")
songID=input("Song ID to replace with the video's audio: ")
#1.875
print("Comparing frames")
def readFrames():
    global videoFile,last_pxArray,levle_array,x,y,trig_x,trig_y
    frames=0
    
    print('Read file: {}'.format(videoFile))
    cap = cv2.VideoCapture(videoFile) # says we capture an image from a webcam
    width  = math.floor(cap.get(3))
    height = math.floor(cap.get(4))
    groupIds=[]
    while(cap.isOpened()):
        ret,cv2_im = cap.read()
        if ret :

            converted = cv2.cvtColor(cv2_im,cv2.COLOR_BGR2RGB)

            pil_im = Image.fromarray(converted)

            im = pil_im.resize((math.floor(width/(height/80)),80))
                    
            pxArray=[]
            #please help me
            for w in range(im.width):
                lay=[]
                for h in range(im.height):
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
                        m=(wi+1)+(wi*80)+(hi+1)
                        levle_array.append(f"1,971,2,{x+xoffs},3,{y+yoffs},22,10,42,1,44,{'{0}a{1}a{2}a0a0'.format(*rgb_to_hsv(pxArray[wi][hi]))},57,1.{m},32,0.5;") #objec
                        yoffs+=1.875
                        he.append(m)
                    xoffs+=1.875
                    groupIds.append(he)
            else:
                yoffs=0
                for wi,w in enumerate(pxArray):
                    for hi,h in enumerate(w):
                        if pxArray[wi][hi] != last_pxArray[wi][hi]:
                            levle_array.append(f"1,1006,2,{trig_x},3,{trig_y+yoffs},10,99999999999,50,10,49,{'{0}a{1}a{2}a1a1'.format(*rgb_to_hsv(pxArray[wi][hi]))},51,{groupIds[wi][hi]},52,1,48,1;") #pulse trigger
                            yoffs+=2
                            changes+=1
            last_pxArray=deepcopy(pxArray)
        elif not ret:
            break
        if frames==0: print("First frame, nothing to compare")
        else: print(f"{frames} with {frames-1}: {changes} change(s)")
        trig_x+=19.2
        cv2.waitKey(int(1000/30))
        frames+=1
            
    cap.release()
readFrames()
levle_array.append(f"1,1,2,{trig_x+700},3,1")
levle_string=''.join(levle_array)

os.system(f"ffmpeg -y -i \"./{videoFile}\" {os.path.join(SAVE_FILE_PATH,f'{str(songID)}.mp3')}")
jshelper="""
function helper(fileName,levelStr) {
    const zlib = require('zlib')
    const fs = require('fs')
    let arg=process.argv
    let fileName = arg[2]

    let data = require('./leveldata.json')
    let gdLevels = process.env.HOME || process.env.USERPROFILE + "/AppData/Local/GeometryDash/CCLocalLevels.dat"

    fs.readFile(gdLevels, 'utf8', function(err, saveData) {

        if (err) return console.log("Error! Could not open or find GD save file")

        if (!saveData.startsWith('<?xml version="1.0"?>')) {
            function xor(str, key) {
                str = String(str).split('').map(letter => letter.charCodeAt());
                let res = "";
                for (i = 0; i < str.length; i++) res += String.fromCodePoint(str[i] ^ key);
                return res;
            }
            saveData = xor(saveData, 11)
            saveData = Buffer.from(saveData, 'base64')
            try { saveData = zlib.unzipSync(saveData).toString() }
            catch(e) { return console.log("Error! GD save file seems to be corrupt!\nMaybe try saving a GD level in-game to refresh it?\n") }
        }
        
        saveData = saveData.split("<k>_isArr</k><t />")
        saveData[1] = saveData[1].replace(/<k>k_(\d+)<\/k><d><k>kCEK<\/k>/g, function(n) { return "<k>k_" + (Number(n.slice(5).split("<")[0])+1) + "</k><d><k>kCEK</k>" })
        saveData = saveData[0] + "<k>_isArr</k><t />" + data.ham + data.bur + levelStr + data.ger + saveData[1]        
        
        saveData = saveData.replace("[[NAME]]", fileName.split(".")[0].replace(/[^a-z|0-9]/gi, "").slice(0, 30)).replace("[[DESC]]", "info goes here")
        fs.writeFileSync(gdLevels, saveData, 'utf8')
    })
}"""
#with open("levelstring",'w') as w: w.write(levle_string)
helpe=js2py.eval_js(jshelper)
helpe(videoFile,levle_string)
