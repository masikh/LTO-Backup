# LTO-Backup
Simple python script for self describing LTO backups on tapes

# Requirements

In linux there are mt-gnu and mt-st packages, almost similar but different!
    
    mt-st  

# Install
    
    chmod +x Backup.py

# Usage

    usage: Backup.py [-h] [-d device-file] [-I | -L | -E | -r | -e | -R target-dir | -s | -b [dir [dir ...]] | -i SET_TAPE_TO_INDEX]

    (c) GPLv3. A simple python script to write TAR archives to tape. A tape manifest is write in the first file on tape and updated on each additional backup
    
    optional arguments:
      -h, --help            show this help message and exit
      -d device-file, --device device-file
                            Set tape device (default: /dev/nst0)
      -I, --initialize_tape
                            Write empty index to beginning of tape. Size is 104857600 byte (100Mb)
      -L, --load_tape_index
                            Load/Show index on tape
      -E, --eject           Eject tape
      -r, --rewind          Rewind tape
      -e, --end_of_logical_tape
                            Set tape position after last archive
      -R target-dir, --restore target-dir
                            Restore tape archive at current index to destination
      -s, --status          Show drive status
      -b [dir [dir ...]], --backup_directory [dir [dir ...]]
                            Write contents of given directories to tape after the last archive
      -i <int>, --set_tape_to_index <int>
                            The tape is positioned at the beginning of the file at index. Index 0 is reserved for the Tape-manifest, 1..N are for archives. The tape
                            is first rewinded.
