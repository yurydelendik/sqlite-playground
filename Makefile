WASMCEPTION ?= /Users/yury/llvmwasm/inception
WASM_DWARF ?= wasm-dwarf
PUBLISH_URL ?= https://yurydelendik.github.io/sqlite-playground/
CUR_DIR = $(shell pwd)
WASM_SOURCEMAP ?= ./wasm-sourcemap.py -s --prefix $(HOME)/=wasm-src:///
LLVM = $(WASMCEPTION)/dist/bin/clang \
  -Imisc/ \
  --target=wasm32-unknown-unknown-wasm \
  --sysroot $(WASMCEPTION)/sysroot \
  -Wl,--allow-undefined-file=src/playground.syms \
  -nostartfiles -O2 -v -g

build: build/playground.wasm build/playground.wasm.map

build/playground.o: src/playground.c misc/sqlite3.h Makefile
	# Build wasm binaries
	mkdir -p build/
	$(LLVM) $(CUR_DIR)/src/playground.c -c -o build/playground.o

build/sqlite3.o: misc/sqlite3.c misc/sqlite3.h Makefile
	# Build wasm binaries
	mkdir -p build/
	$(LLVM) $(CUR_DIR)/misc/sqlite3.c -c -o build/sqlite3.o

build/playground.wasm: build/playground.o build/sqlite3.o
	$(LLVM) build/playground.o build/sqlite3.o -o build/playground.wasm
	# Make sources available for debugger
	mkdir -p build/src; cp src/playground.c build/src/
	mkdir -p build/misc; cp misc/sqlite3.c misc/sqlite3.h build/misc/

build/playground.wasm.map: build/playground.wasm
	$(WASM_SOURCEMAP) \
	 -x -m $(PUBLISH_URL)/build/playground.wasm.map -w build/playground.prod.wasm \
	 build/playground.wasm build/playground.wasm.map

clean:
	-rm build/playground.* build/sqlite3.*

.PHONY: build clean
