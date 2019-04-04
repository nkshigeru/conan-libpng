#include <stdio.h>
#include <string.h>
#include "png.h"
#include "zlib.h"

int main()
{
  fprintf(stderr, "   Compiled with libpng %s; using libpng %s.\n",
    PNG_LIBPNG_VER_STRING, png_libpng_ver);
  fprintf(stderr, "   Compiled with zlib %s; using zlib %s.\n",
    ZLIB_VERSION, zlib_version);
#ifdef PNG_APNG_SUPPORTED
  fprintf(stderr, "   APNG is supported\n");
#else
# error APNG is not supported
#endif

  return 0;
}