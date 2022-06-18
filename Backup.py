#!/usr/bin/python3
import json
import subprocess
from argparse import ArgumentParser


class TapeManifest:
    def __init__(self):
        self.manifest_json = None
        self.manifest_str = None
        self.manifest_size = 104857600  # 100 megabytes = 1024 * 1024 * 100 byte

    def set_manifest(self):
        json_data = json.dumps(self.manifest_json)
        length = len(json_data.encode('utf-8'))
        prepend_string = '0'.encode('utf-8') * (self.manifest_size - length)
        self.manifest_str = prepend_string + json_data.encode('utf-8')
        return len(self.manifest_str)

    def load_manifest(self):
        if len(self.manifest_str) != self.manifest_size:
            raise Exception('Index size error')
        self.manifest_json = json.loads(self.manifest_str.decode('utf-8').lstrip('0'))


class Backup:
    def __init__(self, tape_device=None):
        self.tape_device = tape_device
        self.sources = None
        self.backup_size = 0
        self.backup_manifest = []
        self.tape_status = None
        self.manifest = []

    def initialize_tape(self):
        self.rewind()
        tape_manifest = TapeManifest()
        manifest = [{
            'index': 0,
            'size': tape_manifest.manifest_size,
            'contents': ['Tape-manifest']
        }]
        self.write_manifest(manifest)

    def write_manifest(self, manifest):
        self.rewind()
        tape_manifest = TapeManifest()
        tape_manifest.manifest_json = manifest
        tape_manifest.set_manifest()
        tmp_manifest = '/tmp/manifest'
        with open(tmp_manifest, 'wb') as f:
            f.write(tape_manifest.manifest_str)
        cmd = f'tar cf - {tmp_manifest} | pv -w 100 | mbuffer -m 4G -P 100% | dd of={self.tape_device} bs=128k'
        subprocess.call(cmd, shell=True)

    def load_tape_manifest(self):
        self.rewind()
        tape_manifest = TapeManifest()
        cmd = f'tar -b 256 -xvf {self.tape_device} -C /'
        subprocess.call(cmd, shell=True)
        with open('/tmp/manifest', 'rb') as f:
            tape_manifest.manifest_str = f.read()
            tape_manifest.load_manifest()
            print(json.dumps(tape_manifest.manifest_json, indent=2))
            self.manifest = tape_manifest.manifest_json

    def status(self):
        cmd = f'mt -f {self.tape_device} status'
        subprocess.call(cmd, shell=True)

    def rewind(self):
        cmd = f'mt -f {self.tape_device} rewind'
        subprocess.call(cmd, shell=True)

    def set_tape_to_file_index(self, file_index):
        cmd = f'mt -f {self.tape_device} asf {file_index}'
        subprocess.call(cmd, shell=True)

    def set_tape_to_logical_end(self):
        cmd = f'mt -f {self.tape_device} eod'
        subprocess.call(cmd, shell=True)

    def eject(self):
        cmd = f'mt -f {self.tape_device} eject'
        subprocess.call(cmd, shell=True)

    def backward_skip_file_marker(self, num):
        cmd = f'mt -f {self.tape_device} bsfm {num}'
        subprocess.call(cmd, shell=True)

    def backup(self, sources):
        self.rewind()
        self.load_tape_manifest()
        last_manifest = self.manifest[len(self.manifest) - 1]
        self.set_tape_to_logical_end()
        paths = ' '.join(x for x in sources)

        this_manifest = {
            'index': last_manifest['index'] + 1,
            'size': None,
            'contents': sources
        }
        self.manifest.append(this_manifest)

        cmd = f'size=`du -sc {paths} | tail -1 | '
        cmd += 'awk {\'print $1\'}`'
        cmd += f'; tar cf - {paths} | pv -w 100 | mbuffer -m 4G -P 100% | dd of={self.tape_device} bs=128k'
        print(cmd)
        subprocess.call(cmd, shell=True)
        self.rewind()
        self.write_manifest(self.manifest)

    def restore(self, destination):
        try:
            cmd = 'mkdir -p {destination} && tar -b 256 -xvf {tape_device} -C {destination}/'.format(tape_device=self.tape_device, destination=destination)
            print(cmd)
            subprocess.call(cmd, shell=True)
        except Exception as error:
            pass


if __name__ == '__main__':
    parser = ArgumentParser(description='(c) GPLv3. A simple python script to write TAR archives to tape. '
                                        'A tape manifest is write in the first file on tape and updated on each '
                                        'additional backup')
    parser.add_argument('-d', '--device', type=str, metavar='device-file', default='/dev/nst0', help='Set tape device (default: /dev/nst0)')
    commands = parser.add_mutually_exclusive_group()
    commands.add_argument('-I', '--initialize_tape', action='store_true', help='Write empty index to beginning of tape. Size is 104857600 byte (100Mb)')
    commands.add_argument('-L', '--load_tape_index', action='store_true', help='Load/Show index on tape')
    commands.add_argument('-E', '--eject', action='store_true', help='Eject tape')
    commands.add_argument('-r', '--rewind', action='store_true', help='Rewind tape')
    commands.add_argument('-e', '--end_of_logical_tape', action='store_true', help='Set tape position after last archive')
    commands.add_argument('-R', '--restore', type=str, default=None, metavar='target-dir', help='Restore tape archive at current index to destination')
    commands.add_argument('-s', '--status', action='store_true', help='Show drive status')
    commands.add_argument('-b', '--backup_directory', nargs="*", metavar='dir', help='Write contents of given directories to tape after the last archive')
    commands.add_argument("-i", "--set_tape_to_index", type=int, metavar='<int>', default=None, help="The tape is positioned at the beginning of the file at index. Index 0 is reserved for the Tape-manifest, 1..N are for archives. The tape is first rewinded.")

    args = parser.parse_args()
    backup = Backup(tape_device=args.device)
    initialise_tape = args.initialize_tape
    load_tape_index = args.load_tape_index
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
    elif initialise_tape is True:
        backup.initialize_tape()
    elif load_tape_index is True:
        backup.load_tape_manifest()
    else:
        parser.print_help()
