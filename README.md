# Animu scripts

Various scripts for modifying animu video files (mkv video, ass subtitles) 

Required MKV tool windows executables are in mkvtools.7z.

### addsubs.py

Simple script to add subtitle files with accompanying fonts attachments.

### addsubs_chapters.py

Same as above but can also add video chapters formatted per [these instructions](https://mkvtoolnix.download/doc/mkvmerge.html#mkvmerge.chapters).

### addsubs_chapters_edit_tracks.py

Same as above but can also modify audio and subtitle tracks (keeping and removing selected track ids) and controlling copy of existing attachments.

### extractsubs.py

Extracts subtitles and attachments from .mkv files.

### fix_titles.py

Simple title replacement based on file name without extension.

### AssFontHacker.py and AssParser.py

Hacky scripts for bulk modifying .ass subtitle files.

### re_encode.py

Re-encoding videos with ffmpeg. Current settings are probably bad.

### regex_rename.py

Bulk file renaming script with regexes.

### remove_dual_audio.py

For removing unwanted audio and subtitle tracks.

### sift_tracks.py

Filters MKV tracks in the file per given criteria and makes an importable .py script of them which is automatically used by a few other scripts.

### extract_tracks.py

Extracts subtitles, chapters and attachments.

### sift_subtitle_fonts.py

Poorly made script that tries to confirm which fonts are actually and really used in the .ass subtitles.
