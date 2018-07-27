# Simple WebAssembly demo using source map 

## Building .wasm and .wasm.map files

It's nessary to install and use wasmception and wasm-sourcemap.py to build WebAssembly binary and source map files:
* See https://github.com/yurydelendik/wasmception
* See https://github.com/kripken/emscripten/

The `make` command will execute clang to compile C files, and then extract source maps using wasm-sourcemap. See also "Makefile" file.

## Location of .wasm.map files

The .wasm file points to the .wasm.map file that is located at https://yurydelendik.github.io/sqlite-playground/build/, but this location can be changed at "Makefile".
