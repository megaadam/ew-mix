#!/usr/bin/python3

from collections import namedtuple
import math
import os

Cue = namedtuple('Cue', 'start end text note')

all_cues = [
    Cue(1.8,  4.2,  '#1:  Span 1',                        '1.8,  4.2'),
    Cue(5.9,  8.1,  '#2:  Span 2 -- make this fail',      '5.9,  8.1'),
    Cue(10, 12.001, '#3:  Trailing leftofers',            '10.1, 12.001 microsec edge-to-edge'),
    Cue(12.001, 14.001,   '#4 9.9 .................... ', '12.001, 14.001 microsec overlap'),
    Cue(14, 17,     '#4:',                                '14, 17'),
]


class Segment:
    def __init__(self, seg_offs):
        self.seg = []
        self.seg_offs = seg_offs
    
    def render_header(self, seg_start):
        self.seg.append('WEBVTT')
        self.seg.append(f'#EXT-X-TIMESTAMP-MAP=MPEGTS: {self.seg_offs * 90000}')
        self.seg.append('')

    def render_cue(self, cue):
        start = max(cue.start - self.seg_offs, 0)
        end = cue.end - self.seg_offs
        self.seg.append(f'')
        self.seg.append(f'{self.timestamp(start)} --> '
                        f'{self.timestamp(end)}')
        self.seg.append(f'{cue.text}')
        self.seg.append('')
        self.seg.append(f'NOTE  {cue.note}')
        self.seg.append('')

    def timestamp(self, time):
        # works up to 59 sec
        sec = str(int(time)).zfill(2)
        frame= str(int(math.modf(time)[0] * 1000)).zfill(3)
        ts = f'00:00:{sec}:{frame}'
        return ts

    def flush(self, seg_no, outdir):
        with open(os.path.join(outdir, f'{seg_no}.webvtt'), 'w') as f:
            for line in self.seg:
                f.writelines(line + '\n')

class SegmentGenerator:
    def __init__(self, seg_len, outdir):
        self.track_duration = 30  # in seconds
        self.seg_len = seg_len    # in seconds
        self.outdir = outdir

    def render_media_playlist(self):
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)

        with open(os.path.join(self.outdir, 'index.m3u8'), 'w') as f:
            f.writelines([
                '#EXT-X-VERSION:3', '\n',
                '#EXT-X-MEDIA-SEQUENCE:1', '\n',
                '#EXT-X-TARGETDURATION:2', '\n',
                '#EXT-X-PLAYLIST-TYPE:VOD', '\n',
                '', '\n',]
            )
            for i in range(1, math.ceil(self.track_duration / self.seg_len) + 1):
                f.writelines([
                    '#EXTINF:2.000,', '\n',
                    f'{i}.webvtt', '\n', '\n',
                ])


    def render_primitive_playlist(self):
        seg_no = 1
        seg_start = 0
        seg_end = seg_start + self.seg_len
        while seg_start < self.track_duration:
            segment_cues = self.cues_for_segment(seg_start, seg_end)
            s = Segment(seg_start)
            s.render_header(seg_start)
            for cue_to_render in segment_cues:
                s.render_cue(cue_to_render)

            s.flush(seg_no, self.outdir)

            seg_start = seg_end
            seg_end += self.seg_len
            seg_no += 1

    def cues_for_segment(self, seg_start, seg_end):
        first_cue = None
        last_cue = None
        for i in range(0, len(all_cues)):
            edge_in_segment = ((seg_start < all_cues[i].start < seg_end) or
                               (seg_start < all_cues[i].end < seg_end))
            edges_around_segment = ((all_cues[i].start <= seg_start) and
                                    (all_cues[i].end >= seg_end))

            if(first_cue is None and
               (edge_in_segment or edges_around_segment)):
                first_cue = i
            
            if(all_cues[i].start > seg_end):
                last_cue = i - 1
                break

        if first_cue == None:
            return []

        if last_cue is None:
            last_cue = len(all_cues)

        return all_cues[first_cue:last_cue + 1]




    
def main():
    seg_gen = SegmentGenerator(seg_len=2, outdir='./primitive')
    seg_gen.render_media_playlist()
    seg_gen.render_primitive_playlist()


main()
