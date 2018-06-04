#!/usr/bin/env python
from subprocess import Popen, PIPE
import re
import json
import argparse
import os

parser = argparse.ArgumentParser(prog='wasm-sourcemap.py')
parser.add_argument('wasm', help='wasm file')
parser.add_argument('map', help='output source map')
parser.add_argument('-p', '--prefix', nargs='*', help='replace source filename prefix')
parser.add_argument('-s', '--sources', action='store_true', help='read and embed source files')
parser.add_argument('-w', nargs='?', help='set output wasm file')
parser.add_argument('-x', '--strip', action='store_true', help='removes debug and linking sections')
parser.add_argument('-m', '--source-map', nargs='?', help='specifies sourceMappingURL section contest')
args = parser.parse_args()

llvm_prefix = os.environ['LLVM_BIN'] + '/' if os.environ.get('LLVM_BIN') else '';
llvm_dwarfdump = llvm_prefix + "llvm-dwarfdump"
llvm_readobj = llvm_prefix + "llvm-readobj"
wasm_input = args.wasm
map_output = args.map

vlq_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
def encode(n):
  x = (n << 1) if n >= 0 else ((-n << 1) + 1)
  result = ""
  while x > 31:
    result = result + vlq_chars[32 + (x & 31)]
    x = x >> 5
  return result + vlq_chars[x]

def read_var_uint(wasm, pos):
  n = 0
  shift = 0
  b = ord(wasm[pos])
  pos = pos + 1
  while b >= 128:
    n = n | ((b - 128) << shift)
    b = ord(wasm[pos])
    pos = pos + 1
    shift += 7
  return [n + (b << shift), pos]

def strip_debug_sections(wasm):
  print('Strip debug sections')
  pos = 8
  stripped = wasm[:pos]

  while pos < len(wasm):
    section_start = pos
    [section_id, pos_] = read_var_uint(wasm, pos)
    [section_size, section_body] = read_var_uint(wasm, pos_)
    pos = section_body + section_size
    if section_id == 0:
      [name_len, name_pos] = read_var_uint(wasm, section_body)
      name_end = name_pos + name_len
      name = wasm[name_pos:name_end]
      if name == "linking" or name == "sourceMappingURL" or name.startswith("reloc..debug_") or name.startswith(".debug_"):
        continue # skip debug related sections
    stripped = stripped + wasm[section_start:pos]

  return stripped

def get_uint_var(n):
  result = bytearray()
  while n > 127:
    result.append(128 | (n & 127))
    n = n >> 7
  result.append(n)
  return bytes(result)

def append_source_mapping(wasm, url):
  print('Append sourceMappingURL section')
  section_name = "sourceMappingURL"
  section_content = get_uint_var(len(section_name)) + section_name + get_uint_var(len(url)) + url
  return wasm + get_uint_var(0) + get_uint_var(len(section_content)) + section_content
  
def get_code_section_offset(wasm):
  print('Read sections index')

#  process = Popen([llvm_readobj, "-sections", wasm_input], stdout=PIPE)
#  (output, err) = process.communicate()
#  exit_code = process.wait()
#  if exit_code != 0:
#    print('Error during llvm-readobj execution (%s)' % exit_code)
#    exit(1)

#  code_match = re.search(r"Section \{\s+Type: CODE \(0xA\)\s+Size: \d+\s+Offset: (\d+)", output)
#  code_section_offset = int(code_match.group(1))

  # hacking
  pos = 8

  while pos < len(wasm):
    [section_id, pos_] = read_var_uint(wasm, pos)
    [section_size, pos] = read_var_uint(wasm, pos_)
    if section_id == 10:
      return pos
    pos = pos + section_size

def read_dwarf_entries():
  print('Reading DWARF information from %s' % wasm_input)
  process = Popen([llvm_dwarfdump, "-debug-line", wasm_input], stdout=PIPE)
  (output, err) = process.communicate()
  exit_code = process.wait()
  if exit_code != 0:
    print('Error during llvm-dwarfdump execution (%s)' % exit_code)
    exit(1)

  entries = []
  debug_line_chunks = re.split(r"(debug_line\[0x[0-9a-f]*\])", output)
  for i in range(1,len(debug_line_chunks),2):
    line_chunk = debug_line_chunks[i + 1]

    # include_directories[  1] = "/Users/yury/Work/junk/sqlite-playground/src"
    # file_names[  1]:
    #            name: "playground.c"
    #       dir_index: 1
    #        mod_time: 0x00000000
    #          length: 0x00000000
    #
    # Address            Line   Column File   ISA Discriminator Flags
    # ------------------ ------ ------ ------ --- ------------- -------------
    # 0x0000000000000006     22      0      1   0             0  is_stmt
    # 0x0000000000000007     23     10      1   0             0  is_stmt prologue_end
    # 0x000000000000000f     23      3      1   0             0 
    # 0x0000000000000010     23      3      1   0             0  end_sequence
    # 0x0000000000000011     28      0      1   0             0  is_stmt

    include_directories = {'0': ""}
    for dir in re.finditer(r"include_directories\[\s*(\d+)\] = \"([^\"]*)", line_chunk):
      include_directories[dir.group(1)] = dir.group(2)

    files = {}
    for file in re.finditer(r"file_names\[\s*(\d+)\]:\s+name: \"([^\"]*)\"\s+dir_index: (\d+)", line_chunk):
      file_path = include_directories[file.group(3)] + '/' + file.group(2)
      files[file.group(1)] = file_path

    
    for line in re.finditer(r"\n0x([0-9a-f]+)\s+(\d+)\s+(\d+)\s+(\d+)", line_chunk):
      entry = {'address': int(line.group(1), 16), 'line': int(line.group(2)), 'column': int(line.group(3)), 'file': files[line.group(4)]}
      entries.append(entry)
  return entries

def build_sourcemap(entries, code_section_offset):
  prefixes = []
  for p in args.prefix:
    if p.find('=') < 0:
      prefixes.append({'prefix': p, 'replacement': None})
    else:
      [prefix, replacement] = p.split('=')
      prefixes.append({'prefix': prefix, 'replacement': replacement})
      
  sources = []
  sources_content = [] if args.sources else None
  mappings = []

  sources_map = {}
  last_address = 0
  last_source_id = 0
  last_line = 1
  last_column = 1
  for entry in entries:
    line = entry['line']
    column = entry['column']
    if line == 0 or column == 0:
      continue
    address = entry['address'] + code_section_offset
    file_name = entry['file']
    if file_name not in sources_map:
      source_id = len(sources)
      sources_map[file_name] = source_id
      source_name = file_name
      for p in prefixes:
        if file_name.startswith(p['prefix']):
          if p['replacement'] is None:
            source_name = file_name[len(p['prefix'])::]
          else:
            source_name = p['replacement'] + file_name[len(p['prefix'])::]
          break
      sources.append(source_name)
      if args.sources:
        try:
          with open(file_name, 'r') as infile:
            source_content = infile.read()
          sources_content.append(source_content)
        except:
          # ignore source load failures
          sources_content.append(None)
    else:
      source_id = sources_map[file_name]

    address_delta = address - last_address
    source_id_delta = source_id - last_source_id
    line_delta = line - last_line
    column_delta = column - last_column
    mappings.append(encode(address_delta) + encode(source_id_delta) + encode(line_delta) + encode(column_delta))
    last_address = address
    last_source_id = source_id
    last_line = line
    last_column = column
  return {'version': 3, 'names': [], 'sources': sources, 'sourcesContent': sources_content, 'mappings': ','.join(mappings)}

with open(wasm_input, 'rb') as infile:
  wasm = infile.read()

entries = read_dwarf_entries()

code_section_offset = get_code_section_offset(wasm)

print('Saving to %s' % map_output)
map = build_sourcemap(entries, code_section_offset)
with open(map_output, 'w') as outfile:
    json.dump(map, outfile)

if args.strip:
  wasm = strip_debug_sections(wasm)

if args.source_map:
  wasm = append_source_mapping(wasm, args.source_map)

if args.w:
  print('Saving wasm to %s' % args.w)
  with open(args.w, 'wb') as outfile:
    outfile.write(wasm)

print('Done.')
