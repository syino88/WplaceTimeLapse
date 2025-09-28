import json, os, re, requests, shutil
from datetime import datetime, timezone, timedelta
from PIL import Image

class WplaceTimeLapse:
    
    def __init__(self, target):
        self.setup(target)
        self.download()
        self.merge()
        self.delete()
        self.gif()
    
    def setup(self, target):
        self.dirname = target['name']
        os.makedirs(self.dirname, exist_ok=True)
        os.makedirs(f'{self.dirname}/temp', exist_ok=True)
        self.filename = f"{datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d %H%M%S')}.png"
        start = re.search(r"\(Tl X: (\d*), Tl Y: (\d*), Px X: (\d*), Px Y: (\d*)\)", target['start'])
        end = re.search(r"\(Tl X: (\d*), Tl Y: (\d*), Px X: (\d*), Px Y: (\d*)\)", target['end'])
        self.tx1, self.ty1, self.px1, self.py1 = map(int, start.groups())
        self.tx2, self.ty2, self.px2, self.py2 = map(int, end.groups())
        self.txl, self.tyl = self.tx2 - self.tx1 + 1, self.ty2 - self.ty1 + 1

    def download(self):
        for x in range(self.tx1, self.tx2+1):
            for y in range(self.ty1, self.ty2+1):
                response = requests.get(f"https://backend.wplace.live/files/s0/tiles/{x}/{y}.png")
                open(f"{self.dirname}/temp/{x}_{y}.png", "wb").write(response.content)
    
    def merge(self):
        canvas = Image.new("RGBA", (self.txl*1000, self.tyl*1000))
        for x in range(self.tx1, self.tx2+1):
            for y in range(self.ty1, self.ty2+1):
                img = Image.open(f"{self.dirname}/temp/{x}_{y}.png").convert("RGBA")
                canvas.paste(img, ((x-self.tx1)*1000, (y-self.ty1)*1000), img)
        canvas = canvas.crop((self.px1, self.py1, (self.txl-1)*1000 + self.px2 + 1, (self.tyl-1)*1000 + self.py2 + 1))
        canvas.save(f'{self.dirname}/{self.filename}')
        
    def delete(self):
        shutil.rmtree(f'{self.dirname}/temp')
    
    def gif(self):
        png_files = sorted([f for f in os.listdir(self.dirname) if f.endswith(".png")])
        frames = [Image.open(os.path.join(self.dirname, f)).convert("RGBA") for f in png_files]
        frames[0].save(f"{self.dirname}/{self.dirname}.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)

if __name__ == "__main__":
    targets = json.load(open('.github/workflows/targets.json', 'r'))['targets']
    for target in targets:
        # try:
            WplaceTimeLapse(target)
        # except:
        #     pass
