# Simple WebAssembly demo using source map 

## Building .wasm and .wasm.map files

It's nessary to install and use emscripten to build WebAssembly binary and source map files. See https://kripken.github.io/emscripten-site/docs/tools_reference/emsdk.html for details. Incoming version of SDK is used from this demo.

The `make` command will execute `emcc` with needed parameters. See also "Makefile" file.

## Location of .wasm.map files

The .wasm file points to the .wasm.map file that is located at https://yurydelendik.github.io/sqlite-playground/build/, but this location can be changed at "Makefile".
