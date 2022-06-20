#!/usr/bin/python3
import os
import json
import subprocess
from argparse import ArgumentParser


class TapeManifest:
    @staticmethod
    def dump_manifest(manifest_dict):
        return json.dumps(manifest_dict)

    @staticmethod
    def load_manifest(manifest_string):
        return json.loads(manifest_string)


class Backup:
    def __init__(self, label=None, tape_device=None):
        self.label = label
        self.tape_device = tape_device
        self.sources = None
        self.backup_size = 0
        self.backup_manifest = []
        self.tape_status = None
        self.manifest = []
        self.load_tape_manifest()

    def initialize_tape(self):
        if not os.path.isdir('/var/LTO-Backup'):
            os.mkdir('/var/LTO-Backup')
        manifest = []
        self.write_manifest(manifest)

    def write_manifest(self, manifest):
        tape_manifest = TapeManifest()
        payload = tape_manifest.dump_manifest(manifest)

        with open(f'/var/LTO-Backup/{self.label}', 'w') as f:
            f.write(payload)

    def load_tape_manifest(self):
        if not os.path.isfile(f'/var/LTO-Backup/{self.label}'):
            self.initialize_tape()

        with open(f'/var/LTO-Backup/{self.label}', 'r') as f:
            data = f.read()
            self.manifest = TapeManifest.load_manifest(data)

    def status(self):
        cmd = f'mt-gnu -f {self.tape_device} status'
        subprocess.call(cmd, shell=True)

    def rewind(self):
        cmd = f'mt-gnu -f {self.tape_device} rewind'
        subprocess.call(cmd, shell=True)

    def set_tape_to_file_index(self, file_index):
        cmd = f'mt-gnu -f {self.tape_device} asf {file_index}'
        subprocess.call(cmd, shell=True)
        self.status()

    def set_tape_to_logical_end(self):
        cmd = f'mt-gnu -f {self.tape_device} eom'
        subprocess.call(cmd, shell=True)
        self.status()

    def eject(self):
        cmd = f'mt-gnu -f {self.tape_device} eject'
        subprocess.call(cmd, shell=True)

    def backward_skip_file_marker(self, num):
        cmd = f'mt-gnu -f {self.tape_device} bsfm {num}'
        subprocess.call(cmd, shell=True)

    def backup(self, sources):
        self.load_tape_manifest()
        print(json.dumps(self.manifest, indent=2))
        self.set_tape_to_logical_end()
        paths = ' '.join(x for x in sources)

        this_manifest = {
            'index': len(self.manifest) + 1,
            'contents': sources
        }
        self.manifest.append(this_manifest)

        cmd = f'size=`du -sc {paths} | tail -1 | '
        cmd += 'awk {\'print $1\'}`'
        cmd += f'; tar cf - {paths} | pv -w 100 | mbuffer -m 4G -P 100% | dd of={self.tape_device} bs=128k'
        subprocess.call(cmd, shell=True)
        self.write_manifest(self.manifest)
        print(json.dumps(self.manifest, indent=2))

    def restore(self, destination):
        try:
            cmd = 'mkdir -p {destination} && tar -b 256 -xvf {tape_device} -C {destination}/'.format(
                tape_device=self.tape_device, destination=destination)
            print(cmd)
            subprocess.call(cmd, shell=True)
        except Exception as error:
            pass


if __name__ == '__main__':
    parser = ArgumentParser(description='(c) GPLv3. A simple python script to write TAR archives to tape. '
                                        'A tape manifest is write in the first file on tape and updated on each '
                                        'additional backup')
    parser.add_argument('-l', '--label', type=str, metavar='label', required=True,
                        help='Set tape label (name of manifest in /var/LTO-Backup')
    parser.add_argument('-d', '--device', type=str, metavar='device-file', default='/dev/nst0',
                        help='Set tape device (default: /dev/nst0)')
    commands = parser.add_mutually_exclusive_group()
    commands.add_argument('-E', '--eject', action='store_true', help='Eject tape')
    commands.add_argument('-r', '--rewind', action='store_true', help='Rewind tape')
    commands.add_argument('-e', '--end_of_logical_tape', action='store_true',
                          help='Set tape position after last archive')
    commands.add_argument('-R', '--restore', type=str, default=None, metavar='target-dir',
                          help='Restore tape archive at current index to destination')
    commands.add_argument('-s', '--status', action='store_true', help='Show drive status')
    commands.add_argument('-b', '--backup_directory', nargs="*", metavar='dir',
                          help='Write contents of given directories to tape after the last archive')
    commands.add_argument("-i", "--set_tape_to_index", type=int, metavar='<int>', default=None,
                          help="The tape is positioned at the beginning of the file at index <int>")

    args = parser.parse_args()
    label = args.label
    backup = Backup(label=label, tape_device=args.device)
    sources = args.backup_directory
    restore = args.restore
    eject = args.eject
    rewind = args.rewind
    end_of_logical_tape = args.end_of_logical_tape
    status = args.status
    tape_index = args.set_tape_to_index

    if sources is not None:
        backup.backup(sources)
    elif restore is not None:
        backup.restore(restore)
    elif eject is True:
        backup.eject()
    elif rewind is True:
        backup.rewind()
    elif end_of_logical_tape is True:
        backup.set_tape_to_logical_end()
    elif status is True:
        backup.status()
    elif tape_index is not None:
        if tape_index < 0:
            raise Exception('Index cannot be negative')
        backup.set_tape_to_file_index(tape_index)
    else:
        parser.print_help()

