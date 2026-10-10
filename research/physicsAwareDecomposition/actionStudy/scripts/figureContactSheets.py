"""Create temporary visual-QA sheets after regenerating scientific figures."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
from analysis import ROOT
def main():
    index=json.loads((ROOT/'figures/index.json').read_text());destination=ROOT/'data/raw/figureQA';destination.mkdir(exist_ok=True)
    for start in range(0,len(index),15):
        group=index[start:start+15];sheet=Image.new('RGB',(1500,math.ceil(len(group)/3)*350),'#eeeeee');draw=ImageDraw.Draw(sheet)
        for offset,record in enumerate(group):
            original=Image.open(ROOT/'figures'/(record['name']+'.png')).convert('RGB')
            tile=ImageOps.contain(original,(480,315));x=(offset%3)*500+(500-tile.width)//2;y=(offset//3)*350
            sheet.paste(tile,(x,y+25));draw.text(((offset%3)*500+12,y+5),record['name'],fill='black')
        target=destination/f'contact_{start//15+1:02d}.png';sheet.save(target);print(target)
if __name__=='__main__':main()
