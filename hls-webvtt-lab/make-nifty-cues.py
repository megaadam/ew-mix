#!/usr/bin/python3

from collections import namedtuple
from copy import deepcopy
import math
import os
import random

# Cue = namedtuple('Cue', 'start end text note')
class Cue:
    def __init__(self, start=None, end=None, text=None, note=None):
        self.start = start
        self.end = end
        self.text = text
        self.note = note

all_cues = [
    Cue(1.8,  4.2,  'No. 1:  Span 1',                        '1.8,  4.2'),
    Cue(5.9,  8.1,  'No. :  Span 2 -- make this fail',      '5.9,  8.1'),
    Cue(10, 12.001, 'No. :  Trailing leftofers',            '10.1, 12.001 microsec edge-to-edge'),
    Cue(12.001, 14.001,   '#4 9.9 .................... ', '12.001, 14.001 microsec overlap'),
    Cue(14, 17,     'No. ',                                '14, 17'),
]


def timestamp(seconds, fractions=True):
    hours = int(seconds/60/60)
    min = int(seconds/60) % 60
    sec = int(seconds) % 60

    if fractions:  # fractions
        fracs = int(1000 * math.modf(seconds)[0])
        s = f'{hours:02}:{min:02}:{sec:02}.{fracs:03}'

    else:  # frames
        frames = int(25 * math.modf(seconds)[0])
        s = f'{hours:02}:{min:02}:{sec:02}:{frames:02}'
        
    return s

class Segment:
    def __init__(self, seg_offs):
        self.seg = []
        self.seg_offs = seg_offs
    
    def render_header(self):
        self.seg.append('WEBVTT')
        self.seg.append(f'X-TIMESTAMP-MAP=MPEGTS:{self.seg_offs * 90000},LOCAL:00:00:00.000')
        self.seg.append('')

    def render_cue(self, cue):            
        start = max(cue.start - self.seg_offs, 0)
        end = cue.end - self.seg_offs
        if abs(start-end) < 0.002:
            return
            # Narrow condition, but it works in this case

        self.seg.append(f'')
        self.seg.append(f'{timestamp(start)} --> '
                        f'{timestamp(end)}')
        self.seg.append(f'{cue.text}')
        self.seg.append('')
#        self.seg.append(f'NOTE  {cue.note}')
#        self.seg.append('')

    def flush(self, seg_no, outdir):
        with open(os.path.join(outdir, f'{str(seg_no).zfill(2)}.webvtt'), 'w') as f:
            for line in self.seg:
                f.writelines(line + '\n')

class SegmentGenerator:
    def __init__(self, outdir, seg_len=2, track_duration=30):
        self.track_duration = track_duration  # in seconds
        self.seg_len = seg_len    # in seconds
        self.outdir = outdir
        self.cues = all_cues # default, can be overwritten

    def num_text(self, n):
        s = str(n)
        s = s.replace('0', ' zero')
        s = s.replace('1', ' one')
        s = s.replace('2', ' two')
        s = s.replace('3', ' three')
        s = s.replace('4', ' four')
        s = s.replace('5', ' five')
        s = s.replace('6', ' six')
        s = s.replace('7', ' seven')
        s = s.replace('8', ' eight')
        s = s.replace('9', ' nine')
        return s
        
    def time_text(self, seconds):
        hours = int(seconds/60/60)
        min = int(seconds/60) % 60
        sec = int(seconds) % 60
        frames = int(25 * math.modf(seconds)[0])

        s = f'{hours:02}:{min:02}:{sec:02}:{frames:02}'
        return s

    def generate_cues(self):
        self.cues = []
        cue_out = 0
        cue_num = 0
        while cue_out < self.track_duration:
            cue_gap = round(random.uniform(0, 2), 2)
            cue_dur = round(random.uniform(2, 6), 2)
            if cue_gap <= 0.25:
                cue_gap = 0  # adjacent cues
            
            cue_in = cue_out + cue_gap
            if cue_in >= self.track_duration:
                break

            cue_out = min(cue_in + cue_dur, self.track_duration)
            cue_text = f'{self.num_text(cue_num)} {timestamp(cue_in, False)}'
            cue = Cue(cue_in, cue_out, cue_text)
            self.cues.append(cue)
            cue_num += 1
        
        return

    def render_media_playlist(self):
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)

        with open(os.path.join(self.outdir, 'index.m3u8'), 'w') as f:
            f.writelines([
                '#EXTM3U', '\n',
                '#EXT-X-VERSION:3', '\n',
                '#EXT-X-MEDIA-SEQUENCE:1', '\n',
                f'#EXT-X-TARGETDURATION:{self.seg_len}', '\n',
                '#EXT-X-PLAYLIST-TYPE:VOD', '\n',
                '', '\n',]
            )
            for i in range(1, math.ceil(self.track_duration / self.seg_len) + 1):
                f.writelines([
                    f'#EXTINF:{self.seg_len}.000,', '\n',
                    f'{str(i).zfill(2)}.webvtt', '\n',
                ])
            
            f.writelines(['#EXT-X-ENDLIST\n'])


    def render_primitive_playlist(self):
        # Each segment has MPEGTS = seg_start
        # Cue start never before seg start
        # Cue end can be after segment end
        seg_no = 1
        seg_start = 0
        seg_end = seg_start + self.seg_len
        while seg_start < self.track_duration:
            segment_cues = self.cues_for_segment(seg_start, seg_end)
            s = Segment(seg_start)
            s.render_header()
            for cue_to_render in segment_cues:
                s.render_cue(cue_to_render)

            s.flush(seg_no, self.outdir)

            seg_start = seg_end
            seg_end += self.seg_len
            seg_no += 1
            
    def render_rfc_compliant_playlist(self):
        # Each segment has MPEGTS = 0
        # Cue start may be before segment start
        # Cue end can be after segment end
        seg_no = 1
        seg_start = 0
        seg_end = seg_start + self.seg_len
        while seg_start < self.track_duration:
            segment_cues = self.cues_for_segment(seg_start, seg_end)
            s = Segment(0)
            s.render_header()
            for cue_to_render in segment_cues:
                s.render_cue(cue_to_render)

            s.flush(seg_no, self.outdir)

            seg_start = seg_end
            seg_end += self.seg_len
            seg_no += 1

    def render_semi_compliant_playlist(self):
        # Each segment has MPEGTS = 0
        # Cue start may be before segment start
        # Cue ends at segment end
        seg_no = 1
        seg_start = 0
        seg_end = seg_start + self.seg_len
        while seg_start < self.track_duration:
            segment_cues = self.cues_for_segment(seg_start, seg_end)
            s = Segment(0)
            s.render_header()
            for cue in segment_cues:
                cue_to_render = deepcopy(cue)
                cue_to_render.end = seg_end
                s.render_cue(cue_to_render)

            s.flush(seg_no, self.outdir)

            seg_start = seg_end
            seg_end += self.seg_len
            seg_no += 1

    def cues_for_segment(self, seg_start, seg_end):
        first_cue = None
        last_cue = None
        for i in range(0, len(self.cues)):
            edge_in_segment = ((seg_start < self.cues[i].start < seg_end) or
                               (seg_start < self.cues[i].end < seg_end))
            edges_around_segment = ((self.cues[i].start <= seg_start) and
                                    (self.cues[i].end >= seg_end))

            if(first_cue is None and
               (edge_in_segment or edges_around_segment)):
                first_cue = i
            
            if(self.cues[i].start > seg_end):
                last_cue = i - 1
                break

        if first_cue == None:
            return []

        if last_cue is None:
            last_cue = len(self.cues)

        return self.cues[first_cue:last_cue + 1]
    
def main():
    # seg_gen = SegmentGenerator(seg_len=2, outdir='./primitive')
    # seg_gen.render_media_playlist()
    # seg_gen.render_primitive_playlist()

    seg_gen = SegmentGenerator(seg_len=2, track_duration=48*60, outdir='./rfc-2-sec')
    seg_gen.generate_cues()
    seg_gen.render_media_playlist()
    seg_gen.render_rfc_compliant_playlist()

    seg_gen = SegmentGenerator(seg_len=20, track_duration=48*60, outdir='./rfc-20-sec')
    seg_gen.generate_cues()
    seg_gen.render_media_playlist()
    seg_gen.render_rfc_compliant_playlist()

    # seg_gen = SegmentGenerator(seg_len=2, outdir='./semi-compliant')
    # seg_gen.render_media_playlist()
    # seg_gen.render_semi_compliant_playlist()


main()
