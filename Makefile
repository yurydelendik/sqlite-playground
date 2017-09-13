EMCC_OPTIONS = \
  -Imisc/ \
  -O2 \
  -g4 \
  -s WASM=1 \
  --source-map-base https://yurydelendik.github.io/sqlite-playground/build/ \
  -s EXPORTED_FUNCTIONS="['_init_db','_destroy_db','_exec_cmd', '_get_last_error']" \
  -s RESERVED_FUNCTION_POINTERS=1

build: build/playground.js

build/playground.js: src/playground.c misc/sqlite3.c misc/sqlite3.h Makefile
	# Build wasm binaries
	mkdir -p build/
	emcc $(EMCC_OPTIONS) src/playground.c misc/sqlite3.c -o build/playground.js
	# Make sources available for debugger
	mkdir -p build/src; cp src/playground.c build/src/
	mkdir -p build/misc; cp misc/sqlite3.c misc/sqlite3.h build/misc/

clean:
	-rm build/playground.*

.PHONY: build clean
