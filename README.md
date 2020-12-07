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

### fonthacker.py

Hacky script for bulk modifying .ass subtitle files.

### re_encode.py

Re-encoding videos with ffmpeg. Current settings are probably bad.

### regex_rename.py

Bulk file renaming script with regexes.

### remove_dual_audio.py

For removing unwanted audio and subtitle tracks.
