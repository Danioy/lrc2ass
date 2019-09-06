
# This script to convert lcr into ass

import os
import re
import subprocess


filelist = []


def get_mp3_lcr_paired_filename( path="." ):

# scan the path and find out all paired mp3-lcr source files,
# and update to the filelist list.

    for file in os.listdir(path):
        if file.endswith(".mp3"):
            base = file[0:-4]
            lcr = os.path.join(path, base + ".lrc")
            if os.path.isfile(lcr):
                src = (file, lcr, os.path.join(path, base + ".ass"))
                filelist.append(src)


def read_in_lcr_lines( lcrpath ):

# read the lcr file and clean,
# return a list of cleaned lcr lines.

    lines = []
    valid = re.compile(r"^\[[0-9][0-9]:[0-9.]+\]")

    with open(lcrpath, 'r') as lcr:
        for line in lcr:
            if (valid.match(line)):
                time = "0:" + line[1:8] + "0"
                text = line[10:-1]
                lines.append((time, text))

    return lines


def write_ass_files(file, lines):

# generate .ass file according to the lines list returned
# from read_in_lcr_lines()
    mp3, lcr, ass = file

    # we need to call ffprobe to get the exact ending
    # time for ass file
    cmd = "ffprobe -v error -show_entries format=duration   -of default=noprint_wrappers=1:nokey=1 -sexagesimal '{}'".format(mp3)
    ending = subprocess.getoutput(cmd)

    with open(ass, 'w') as af:
        af.write("[Script Info]\n")
        af.write("\n")
        af.write("[Aegisub Project Garbage]\n")
        af.write("Audio File: {}\n".format(mp3))
        af.write("Active Line: {}\n".format(len(lines)))
        af.write("\n")

        af.write("""
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
""")
        af.write("\n")

        af.write("[Events]\n")
        af.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for i in range(len(lines)-1):
            af.write("Dialogue: 0,")
            af.write(lines[i][0])
            af.write(",")
            af.write(lines[i+1][0])
            af.write(",Default,,0,0,0,,")
            af.write(lines[i][1])
            af.write("\n")

        # write the last line.
        af.write("Dialogue: 0,")
        af.write(lines[len(lines)-1][0])
        af.write(",")
        af.write(ending)
        af.write(",Default,,0,0,0,,")
        af.write(lines[len(lines)-1][1])
        af.write("\n")


def main():
    get_mp3_lcr_paired_filename()
    for file in filelist:
        lines = read_in_lcr_lines(file[1])
        write_ass_files(file, lines)


if __name__ == '__main__':
    main()
