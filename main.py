from PIL import Image
import sys, time
from tqdm import trange

def main():
    start = time.time()
    imagePath = sys.argv[1]
    imageOut = sys.argv[2]
    im = Image.open(imagePath)
    pixel_xy = [0, 0]
    pixel_color = (0,0,0)
    grayscaleDiff = (255/int(sys.argv[3]))
    neighboringPixelDiff = float(sys.argv[4])
    skipped = 0
    rawData = b''
    area = im.size[0]*im.size[1]

    with trange(area, desc="Pixels Processed") as pBar:
        
        while True:
            prevShadeColor = 0
            prevPixelColorAverg = 0

            while pixel_xy[0] < im.size[0]:

                scale = 0
                pixel_color = im.getpixel(tuple(pixel_xy))
                pixelColorAverg = (pixel_color[0]+pixel_color[1]+pixel_color[2])/3

                if abs((pixelColorAverg/255)-(prevPixelColorAverg/255)) <= neighboringPixelDiff:
                    skipped += 1
                    rawData += int(prevShadeColor).to_bytes(1, "little")
                    pBar.update(1)
                    pixel_xy[0] += 1
                    continue
            
                while True:
                   #print(scale*grayscaleDiff)
                   if 255-(scale*grayscaleDiff) <= pixelColorAverg:
                       prevShadeColor = 255-(scale*grayscaleDiff)
                       prevPixelColorAverg = pixelColorAverg
                       rawData += int(255-(scale*grayscaleDiff)).to_bytes(1, "little")
                       pBar.update(1)
                       break
                   scale += 1

                pixel_xy[0] += 1

            pixel_xy[0] = 0
            pixel_xy[1] += 1

            if pixel_xy[1] >= im.size[1]:
                break
    
    print("Completed in " + str(round(time.time()-start, 2)) + "s")
    print("Skipped " + str(skipped))

    out = Image.frombytes('L', (im.size[0], im.size[1]), rawData)
    out.save(imageOut)
    out.show()

if __name__ == "__main__":
    main()
