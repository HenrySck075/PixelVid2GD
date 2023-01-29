
const zlib = require('zlib')
const fs = require('fs')
let arg=process.argv
let levelStr = arg[2]
let fileName = arg[3]

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
