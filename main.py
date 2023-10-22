from PIL import Image
import time, argparse, sys, os
import dearpygui.dearpygui as dpg
from tqdm import trange

class openFile:

    def callback(self, sender, app_data):
        if os.path.isfile(sender["file_path_name"]) == False:
            with dpg.window(label="File Error"):
                dpg.add_text("Error: File Doesn't Exist")
            return

        width, height, channels, data = dpg.load_image(sender["file_path_name"])

        with dpg.texture_registry(show=True):
            dpg.add_static_texture(width=width, height=height, default_value=data, tag=sender["file_path_name"])
            dpg.add_tab(label=sender["file_name"], closable=True, tag=sender["file_name"], parent="Files")
            dpg.add_image(sender["file_path_name"], parent=sender["file_name"])

    def create(self):
        with dpg.file_dialog(directory_selector=False, height=300, show=True, callback=openFile.callback):
            dpg.add_file_extension(".png")
            dpg.add_file_extension(".jpg")

def gui():
    dpg.create_context()
    
    with dpg.window(label="Test", tag="Wind_1") as window:
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Open", callback=openFile.create)
                dpg.add_menu_item(label="Save")
        dpg.add_tab_bar(label="file", tag="Files")

    dpg.create_viewport(title="main.py", width=600, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Wind_1", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

def main():
    start = time.time()
    imagePath = args.Input_File
    imageOut = args.Output_File
    im = Image.open(imagePath)
    pixel_xy = [0, 0]
    pixel_color = (0,0,0)
    grayscaleDiff = (255/args.NumofShades)
    neighboringPixelDiff = args.Differrence
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
    Mainparser = argparse.ArgumentParser(prog="main.py", description="Grayscale's an Image")
    Mainparser.add_argument("command", help="How to run main.py", choices=["cmdline", "gui"])
    args = Mainparser.parse_args(sys.argv[1:2])

    if args.command == "gui":
        gui()
    else:
        cmdparser = argparse.ArgumentParser(prog="main.py cmdline", description="Grayscale's an Image")
        cmdparser.add_argument("Input_File", help="Input File")
        cmdparser.add_argument("-o", "--Out", help="Output File [Default: out.png]", default="out.png", metavar="OUT_FILE", dest="Output_File")
        cmdparser.add_argument("-Sn", "--ShadeNum", dest="NumofShades", type=int, help="Num of Shades of Gray to allow", metavar="[0-255]", required=True)
        cmdparser.add_argument("-D", "--Diff", dest="Differrence", type=float, help="Neighbouring pixel differrence", metavar="[0.0-1.0]", required=True)
        cmdparser.add_argument("--gui", dest="guiFlag", action="store_true", help="Start GUI mode")
        args = cmdparser.parse_args(sys.argv[2::])
        main()
