if (!Math.clz32) {
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/clz32
  Math.clz32 = function (x) {
    // Let n be ToUint32(x).
    // Let p be the number of leading zero bits in 
    // the 32-bit binary representation of n.
    // Return p.    
    if (x == null || x === 0) {
      return 32;
    }
    return 31 - Math.floor(Math.log(x >>> 0) * Math.LOG2E);
  };
}
if (!Math.fround) {
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/fround
  Math.fround = (function (array) {
    return function (x) {
      return array[0] = x, array[0];
    };
  })(new Float32Array(1));
}
if (!Math.imul) {
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/imul
  Math.imul = function (a, b) {
    var aHi = (a >>> 16) & 0xffff;
    var aLo = a & 0xffff;
    var bHi = (b >>> 16) & 0xffff;
    var bLo = b & 0xffff;
    // the shift by 0 fixes the sign on the high part
    // the final |0 converts the unsigned value into a signed value
    return ((aLo * bLo) + (((aHi * bLo + aLo * bHi) << 16) >>> 0) | 0);
  };
}
