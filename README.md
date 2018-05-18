# Simple WebAssembly demo using source map 

## Building .wasm and .wasm.map files

It's nessary to install and use wasmception and wasm-dwarf to build WebAssembly binary and source map files:
* See https://github.com/yurydelendik/wasmception
* Run `cargo install --git https://github.com/yurydelendik/wasm-dwarf.git`

The `make` command will execute clang to compile C files, and then extract source maps using wasm-dwarf. See also "Makefile" file.

## Location of .wasm.map files

The .wasm file points to the .wasm.map file that is located at https://yurydelendik.github.io/sqlite-playground/build/, but this location can be changed at "Makefile".
