WASMCEPTION ?= /Users/yury/llvmwasm/inception
WASM_DWARF ?= wasm-dwarf
PUBLISH_URL ?= https://yurydelendik.github.io/sqlite-playground/
CUR_DIR = $(shell pwd)
WASM_DWARF_CMD = $(WASM_DWARF) -s --prefix $(HOME)/=wasm-src:///
LLVM = $(WASMCEPTION)/dist/bin/clang \
  -Imisc/ \
  --target=wasm32-unknown-unknown-wasm \
  --sysroot $(WASMCEPTION)/sysroot \
  -nostartfiles -O2 -v -g
EXPORTS = \
  alloc_mem \
  free_mem \
  init_db \
  destroy_db \
  exec_cmd \
  get_last_error \
  $(NULL)

build: build/playground.wasm build/playground.wasm.map

build/playground.o: src/playground.c misc/sqlite3.h Makefile
	# Build wasm binaries
	mkdir -p build/
	$(LLVM) $(CUR_DIR)/src/playground.c -c -o build/playground.o

build/sqlite3.o: misc/sqlite3.c misc/sqlite3.h Makefile
	# Build wasm binaries
	mkdir -p build/
	$(LLVM) $(CUR_DIR)/misc/sqlite3.c -c -o build/sqlite3.o

LINKER_PREFIX := -Wl,
build/playground.wasm: build/playground.o build/sqlite3.o
	$(LLVM) build/playground.o build/sqlite3.o -o build/playground.wasm \
	  $(LINKER_PREFIX)--no-entry,--no-threads,--allow-undefined-file=src/playground.syms \
	  $(patsubst %,$(LINKER_PREFIX)--export=%,$(EXPORTS))
	# Make sources available for debugger
	mkdir -p build/src; cp src/playground.c build/src/
	mkdir -p build/misc; cp misc/sqlite3.c misc/sqlite3.h build/misc/

build/playground.wasm.map: build/playground.wasm
	$(WASM_DWARF_CMD) build/playground.wasm -o build/playground.wasm.map \
	  -w build/playground.prod.wasm -x --source-map=$(PUBLISH_URL)build/playground.wasm.map

clean:
	-rm build/playground.* build/sqlite3.*

.PHONY: build clean
