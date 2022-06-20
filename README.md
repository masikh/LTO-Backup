# LTO-Backup
Simple python script for self describing LTO backups on tapes

# Requirements

In linux there are mt-gnu and mt-st packages, almost similar but different!
    
    mt-gnu  

# Install
    
    chmod +x Backup.py

# Usage

    usage: Backup.py [-h] -l label [-d device-file] [-E | -r | -e | -R target-dir | -s | -b [dir [dir ...]] | -i <int>]

    Copyright: (c) GPLv3 (20 june 2022)
    Author: Robert Nagtegaal
    
    Description:
    A simple python script to write TAR archives to tape. You need to give a label (name) for the tape. 
    This label is used as filename for keeping a manifest. Manifests are kept in /var/LTO-Backup. 
    This program relies on mt-gnu.
    
    optional arguments:
      -h, --help            show this help message and exit
      -l label, --label label
                            Set tape label (name of manifest in /var/LTO-Backup
      -d device-file, --device device-file
                            Set tape device (default: /dev/nst0)
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
                            The tape is positioned at the beginning of the file at index <int>