#include <stdlib>

struct block {
  void *allocated;
  size_t size;

  void free() {
    jefree(this);
  }
};

typedef struct block Block;

Block jemalloc(size_t size) {
  return { malloc(size), size };
}

void jefree(Block *block) {
  free(block->allocated);
}

int main(int argc, char const *argv[]) {
  Block b = jemalloc(30);
  printf("data at %p with size %d\n", b.allocated, b.size);
  jefree(&b);
  return 0;
}
