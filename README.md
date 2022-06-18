# LTO-Backup
Simple python script for self describing LTO backups on tapes

# Install
    
    chmod +x Backup.py

# Usage

    usage: Backup.py [-h] [-d DEVICE] [-I | -L | -E | -r | -e | -R RESTORE | -s | -b [BACKUP_DIRECTORY [BACKUP_DIRECTORY ...]] | -i SET_TAPE_TO_INDEX]
    
    optional arguments:
      -h, --help            show this help message and exit
      -d DEVICE, --device DEVICE
                            Set tape device (default: /dev/nst0)
      -I, --initialize_tape
                            Write empty index to beginning of tape. Size is 104857600 byte
      -L, --load_tape_index
                            Load/Show index on tape
      -E, --eject           Eject tape
      -r, --rewind          Rewind tape
      -e, --end_of_logical_tape
                            Set tape position after last archive
      -R RESTORE, --restore RESTORE
                            Restore tape archive at current index to destination
      -s, --status          Show drive status
      -b [BACKUP_DIRECTORY [BACKUP_DIRECTORY ...]], --backup_directory [BACKUP_DIRECTORY [BACKUP_DIRECTORY ...]]
                            Write contents of given directories to tape after the last file
      -i SET_TAPE_TO_INDEX, --set_tape_to_index SET_TAPE_TO_INDEX
                            The tape is positioned at the beginning of the file at index. Index 0 is reserved for the Tape-manifest, 1..N are for archives. The tape
                            is first rewinded.
